from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import User, SeekerProfile, EmployerProfile
from jobs.models import Job, Category, SavedJob
from applications.models import Application


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or getattr(user, "role", "") == "ADMIN":
        return redirect("dashboard:admin_dashboard")
    elif user.is_employer:
        return redirect("dashboard:employer_dashboard")
    else:
        return redirect("dashboard:seeker_dashboard")


@login_required
def seeker_dashboard(request):
    if not request.user.is_seeker and not request.user.is_superuser:
        messages.warning(request, "Switched to Job Seeker view.")

    profile, _ = SeekerProfile.objects.get_or_create(user=request.user)

    applications = (
        Application.objects.filter(applicant=request.user)
        .select_related("job", "job__employer", "job__category")
        .order_by("-created_at")
    )

    saved_jobs = SavedJob.objects.filter(user=request.user).select_related(
        "job", "job__employer", "job__category"
    )

    app_stats = {
        "total": applications.count(),
        "shortlisted": applications.filter(
            status=Application.Status.SHORTLISTED
        ).count(),
        "hired": applications.filter(status=Application.Status.HIRED).count(),
        "rejected": applications.filter(status=Application.Status.REJECTED).count(),
    }

    context = {
        "profile": profile,
        "completion": profile.completion_percentage(),
        "applications": applications,
        "saved_jobs": saved_jobs,
        "app_stats": app_stats,
    }
    return render(request, "dashboard/seeker_dashboard.html", context)


@login_required
def employer_dashboard(request):
    if not request.user.is_employer and not request.user.is_superuser:
        messages.error(request, "Only employers can access the employer dashboard.")
        return redirect("home")

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": f"{request.user.username}'s Company"},
    )

    jobs = (
        Job.objects.filter(employer=profile)
        .annotate(applicant_count=Count("applications"))
        .order_by("-created_at")
    )

    total_views = jobs.aggregate(total=Sum("views_count"))["total"] or 0
    total_apps = Application.objects.filter(job__employer=profile).count()
    active_jobs_count = jobs.filter(status=Job.Status.APPROVED).count()
    pending_jobs_count = jobs.filter(status=Job.Status.PENDING).count()

    context = {
        "company": profile,
        "jobs": jobs,
        "total_views": total_views,
        "total_apps": total_apps,
        "active_jobs_count": active_jobs_count,
        "pending_jobs_count": pending_jobs_count,
    }
    return render(request, "dashboard/employer_dashboard.html", context)


@login_required
def job_applicants(request, job_slug):
    job = get_object_or_404(Job.objects.select_related("employer__user"), slug=job_slug)

    user = request.user
    if not (
        user.is_superuser
        or user == job.employer.user
        or getattr(user, "role", "") == "ADMIN"
    ):
        return HttpResponseForbidden("Unauthorized to view applicants for this job.")

    applications = (
        Application.objects.filter(job=job)
        .select_related("applicant", "applicant__seeker_profile")
        .order_by("-created_at")
    )

    status_filter = request.GET.get("status")
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        "job": job,
        "applications": applications,
        "status_choices": Application.Status.choices,
        "selected_status": status_filter,
    }
    return render(request, "dashboard/job_applicants.html", context)


def is_admin_check(user):
    return user.is_authenticated and (
        user.is_superuser or user.is_staff or getattr(user, "role", "") == "ADMIN"
    )


@user_passes_test(is_admin_check, login_url="accounts:login")
def admin_dashboard(request):
    total_users = User.objects.count()
    total_seekers = User.objects.filter(role=User.Role.JOB_SEEKER).count()
    total_employers = User.objects.filter(role=User.Role.EMPLOYER).count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status=Job.Status.APPROVED).count()
    pending_jobs = Job.objects.filter(status=Job.Status.PENDING).count()
    total_applications = Application.objects.count()

    moderation_queue = (
        Job.objects.filter(status=Job.Status.PENDING)
        .select_related("employer", "category")
        .order_by("-created_at")
    )

    category_data = Category.objects.annotate(job_count=Count("jobs")).values(
        "name", "job_count"
    )
    cat_labels = [c["name"] for c in category_data if c["job_count"] > 0]
    cat_counts = [c["job_count"] for c in category_data if c["job_count"] > 0]

    app_statuses = Application.objects.values("status").annotate(total=Count("id"))
    status_map = dict(Application.Status.choices)
    app_status_labels = [status_map.get(s["status"], s["status"]) for s in app_statuses]
    app_status_counts = [s["total"] for s in app_statuses]

    recent_applications = Application.objects.select_related(
        "job", "applicant"
    ).order_by("-created_at")[:8]
    recent_users = User.objects.order_by("-date_joined")[:6]

    context = {
        "total_users": total_users,
        "total_seekers": total_seekers,
        "total_employers": total_employers,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "pending_jobs": pending_jobs,
        "total_applications": total_applications,
        "moderation_queue": moderation_queue,
        "cat_labels_json": json.dumps(cat_labels),
        "cat_counts_json": json.dumps(cat_counts),
        "app_status_labels_json": json.dumps(app_status_labels),
        "app_status_counts_json": json.dumps(app_status_counts),
        "recent_applications": recent_applications,
        "recent_users": recent_users,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@user_passes_test(is_admin_check, login_url="accounts:login")
@require_POST
def admin_moderate_job(request, job_id, action):
    job = get_object_or_404(Job, id=job_id)
    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.POST.get("ajax") == "1"
    )

    if action == "approve":
        job.status = Job.Status.APPROVED
        job.save()
        msg = f"Job '{job.title}' approved and published successfully."
    elif action == "reject":
        job.status = Job.Status.REJECTED
        job.save()
        msg = f"Job '{job.title}' has been rejected."
    else:
        msg = "Invalid moderation action."
        if is_ajax:
            return JsonResponse({"status": "error", "message": msg}, status=400)
        messages.error(request, msg)
        return redirect("dashboard:admin_dashboard")

    if is_ajax:
        return JsonResponse(
            {
                "status": "success",
                "message": msg,
                "job_id": job.id,
                "new_status": job.status,
                "new_status_display": job.get_status_display(),
            }
        )

    messages.success(request, msg)
    return redirect("dashboard:admin_dashboard")
