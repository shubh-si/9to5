import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.files.base import ContentFile

from .models import Application
from .forms import ApplicationForm
from jobs.models import Job


@login_required
@require_POST
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.POST.get("ajax") == "1"
    )

    if not request.user.is_seeker and not request.user.is_superuser:
        msg = "Only registered Job Seekers can apply for open positions."
        if is_ajax:
            return JsonResponse({"status": "error", "message": msg}, status=403)
        messages.error(request, msg)
        return redirect("jobs:job_detail", slug=job.slug)

    if job.status != Job.Status.APPROVED:
        msg = "This job listing is not accepting applications at this time."
        if is_ajax:
            return JsonResponse({"status": "error", "message": msg}, status=400)
        messages.error(request, msg)
        return redirect("jobs:job_detail", slug=job.slug)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        msg = "You have already applied for this position."
        if is_ajax:
            return JsonResponse({"status": "error", "message": msg}, status=400)
        messages.warning(request, msg)
        return redirect("jobs:job_detail", slug=job.slug)

    form = ApplicationForm(request.POST, request.FILES)
    if form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant = request.user

        uploaded_resume = request.FILES.get("resume")
        use_profile = form.cleaned_data.get("use_profile_resume")

        seeker_profile = getattr(request.user, "seeker_profile", None)

        if uploaded_resume:
            application.resume = uploaded_resume
        elif use_profile and seeker_profile and seeker_profile.resume:
            application.resume = seeker_profile.resume
        else:
            msg = "Please upload a resume file or attach your profile resume."
            if is_ajax:
                return JsonResponse({"status": "error", "message": msg}, status=400)
            messages.error(request, msg)
            return redirect("jobs:job_detail", slug=job.slug)

        application.save()

        success_msg = f"Your application for '{job.title}' was submitted successfully!"
        if is_ajax:
            return JsonResponse(
                {
                    "status": "success",
                    "message": success_msg,
                    "application_id": application.id,
                }
            )
        messages.success(request, success_msg)
        return redirect("jobs:job_detail", slug=job.slug)
    else:
        errors = "; ".join([f"{k}: {', '.join(v)}" for k, v in form.errors.items()])
        if is_ajax:
            return JsonResponse({"status": "error", "message": errors}, status=400)
        messages.error(request, f"Submission error: {errors}")
        return redirect("jobs:job_detail", slug=job.slug)


@login_required
def download_resume(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related("job__employer__user", "applicant"),
        id=application_id,
    )

    user = request.user
    is_applicant = user == application.applicant
    is_job_employer = user == application.job.employer.user
    is_admin = user.is_superuser or getattr(user, "role", "") == "ADMIN"

    if not (is_applicant or is_job_employer or is_admin):
        return HttpResponseForbidden(
            "You do not have permission to access this candidate document."
        )

    if not application.resume:
        raise Http404("No resume file associated with this application.")

    try:
        filename = os.path.basename(application.resume.name)
        return FileResponse(
            application.resume.open("rb"), as_attachment=True, filename=filename
        )
    except FileNotFoundError:
        raise Http404("The requested file was not found on the server.")


@login_required
@require_POST
def update_application_status(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related("job__employer__user"), id=application_id
    )

    user = request.user
    if not (
        user.is_superuser
        or user == application.job.employer.user
        or getattr(user, "role", "") == "ADMIN"
    ):
        return HttpResponseForbidden("Unauthorized to modify application status.")

    new_status = request.POST.get("status")
    notes = request.POST.get("notes", "").strip()

    valid_statuses = [choice[0] for choice in Application.Status.choices]
    if new_status in valid_statuses:
        application.status = new_status
        if notes:
            application.employer_notes = notes
        application.save()

        is_ajax = (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.POST.get("ajax") == "1"
        )
        msg = f"Candidate status updated to {application.get_status_display()}."
        if is_ajax:
            return JsonResponse(
                {
                    "status": "success",
                    "message": msg,
                    "new_status": application.status,
                    "status_label": application.get_status_display(),
                    "badge_class": application.status_badge_class,
                }
            )
        messages.success(request, msg)

    return redirect("dashboard:job_applicants", job_slug=application.job.slug)
