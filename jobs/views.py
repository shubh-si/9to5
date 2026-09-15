from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, F, Count
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Job, Category, SavedJob
from .forms import JobPostForm
from accounts.models import EmployerProfile, SeekerProfile, User
from applications.models import Application


def job_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    location_query = request.GET.get("location", "").strip()
    job_type = request.GET.get("job_type", "").strip()
    experience = request.GET.get("experience", "").strip()
    remote_only = request.GET.get("remote") in ["1", "true", "True"]
    min_sal = request.GET.get("min_salary", "").strip()

    jobs_qs = Job.objects.filter(status=Job.Status.APPROVED).select_related(
        "employer", "category"
    )

    if query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(requirements__icontains=query)
            | Q(employer__company_name__icontains=query)
        )

    if category_slug:
        jobs_qs = jobs_qs.filter(category__slug=category_slug)

    if location_query:
        jobs_qs = jobs_qs.filter(location__icontains=location_query)

    if job_type:
        jobs_qs = jobs_qs.filter(job_type=job_type)

    if experience:
        jobs_qs = jobs_qs.filter(experience_level=experience)

    if remote_only:
        jobs_qs = jobs_qs.filter(is_remote=True)

    if min_sal and min_sal.isdigit():
        jobs_qs = jobs_qs.filter(
            Q(salary_max__gte=int(min_sal)) | Q(salary_min__gte=int(min_sal))
        )

    jobs_qs = jobs_qs.order_by("-created_at")

    paginator = Paginator(jobs_qs, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    saved_job_ids = set()
    if request.user.is_authenticated:
        saved_job_ids = set(
            SavedJob.objects.filter(user=request.user, job__in=page_obj).values_list(
                "job_id", flat=True
            )
        )

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "job_types": Job.JobType.choices,
        "experience_levels": Job.Experience.choices,
        "saved_job_ids": saved_job_ids,
        "current_filters": {
            "q": query,
            "category": category_slug,
            "location": location_query,
            "job_type": job_type,
            "experience": experience,
            "remote": remote_only,
            "min_salary": min_sal,
        },
        "total_count": paginator.count,
    }

    is_ajax = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.GET.get("ajax") == "1"
    )
    if is_ajax:
        cards_html = render_to_string("jobs/_job_cards.html", context, request=request)
        pagination_html = render_to_string(
            "jobs/_pagination.html", context, request=request
        )
        return JsonResponse(
            {
                "html": cards_html,
                "pagination_html": pagination_html,
                "total_count": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            }
        )

    return render(request, "jobs/job_list.html", context)


def job_detail(request, slug):
    job = get_object_or_404(
        Job.objects.select_related("employer", "category"), slug=slug
    )

    session_key = f"viewed_job_{job.id}"
    if not request.session.get(session_key):
        Job.objects.filter(pk=job.pk).update(views_count=F("views_count") + 1)
        job.refresh_from_db(fields=["views_count"])
        request.session[session_key] = True

    is_saved = False
    has_applied = False
    existing_application = None

    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
        if request.user.is_seeker:
            existing_application = Application.objects.filter(
                job=job, applicant=request.user
            ).first()
            has_applied = existing_application is not None

    related_jobs = (
        Job.objects.filter(category=job.category, status=Job.Status.APPROVED)
        .exclude(id=job.id)
        .select_related("employer")[:3]
    )

    context = {
        "job": job,
        "is_saved": is_saved,
        "has_applied": has_applied,
        "application": existing_application,
        "related_jobs": related_jobs,
    }
    return render(request, "jobs/job_detail.html", context)


@login_required
def job_create(request):
    if not request.user.is_employer and not request.user.is_superuser:
        messages.error(request, "Only registered employers can post new jobs.")
        return redirect("home")

    employer_profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": f"{request.user.username}'s Company"},
    )

    if request.method == "POST":
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer_profile

            job.status = Job.Status.PENDING
            job.save()
            messages.success(
                request,
                f"Job listing '{job.title}' submitted! It will appear publicly once approved by moderation.",
            )
            return redirect("dashboard:employer_dashboard")
        else:
            messages.error(request, "Please review the form errors below.")
    else:
        form = JobPostForm()

    return render(request, "jobs/job_form.html", {"form": form, "action": "Create"})


@login_required
def job_edit(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if not request.user.is_superuser and (
        not hasattr(request.user, "employer_profile")
        or job.employer != request.user.employer_profile
    ):
        return HttpResponseForbidden("You are not authorized to edit this job posting.")

    if request.method == "POST":
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' has been updated.")
            return redirect("dashboard:employer_dashboard")
        else:
            messages.error(request, "Please review form errors.")
    else:
        form = JobPostForm(instance=job)

    return render(
        request, "jobs/job_form.html", {"form": form, "job": job, "action": "Edit"}
    )


@login_required
@require_POST
def job_delete(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if not request.user.is_superuser and (
        not hasattr(request.user, "employer_profile")
        or job.employer != request.user.employer_profile
    ):
        return HttpResponseForbidden("You are not authorized to delete this job.")

    title = job.title
    job.delete()
    messages.success(request, f"Job listing '{title}' was deleted.")
    return redirect("dashboard:employer_dashboard")


@login_required
@require_POST
def toggle_save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    saved_obj = SavedJob.objects.filter(user=request.user, job=job).first()

    if saved_obj:
        saved_obj.delete()
        is_saved = False
        message = "Job removed from saved list."
    else:
        SavedJob.objects.create(user=request.user, job=job)
        is_saved = True
        message = "Job saved to your bookmarks."

    return JsonResponse(
        {"status": "success", "saved": is_saved, "message": message, "job_id": job_id}
    )


def companies_list(request):
    q = request.GET.get("q", "").strip()
    industry = request.GET.get("industry", "").strip()
    size = request.GET.get("size", "").strip()

    companies_qs = EmployerProfile.objects.annotate(
        active_jobs_count=Count("jobs", filter=Q(jobs__status=Job.Status.APPROVED))
    ).order_by("-active_jobs_count", "company_name")

    if q:
        companies_qs = companies_qs.filter(
            Q(company_name__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
            | Q(industry__icontains=q)
        )

    if industry:
        companies_qs = companies_qs.filter(industry__icontains=industry)

    if size:
        companies_qs = companies_qs.filter(company_size=size)

    industries = (
        EmployerProfile.objects.exclude(industry="")
        .values_list("industry", flat=True)
        .distinct()
        .order_by("industry")
    )

    paginator = Paginator(companies_qs, 9)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_count": paginator.count,
        "industries": industries,
        "size_choices": EmployerProfile.SIZE_CHOICES,
        "current_filters": {
            "q": q,
            "industry": industry,
            "size": size,
        },
    }
    return render(request, "jobs/companies_list.html", context)


def company_detail(request, slug):
    company = get_object_or_404(
        EmployerProfile.objects.annotate(
            active_jobs_count=Count("jobs", filter=Q(jobs__status=Job.Status.APPROVED))
        ),
        company_slug=slug,
    )

    open_jobs = (
        Job.objects.filter(employer=company, status=Job.Status.APPROVED)
        .select_related("category")
        .order_by("-created_at")
    )

    other_companies = EmployerProfile.objects.exclude(pk=company.pk).order_by("?")[:4]

    context = {
        "company": company,
        "open_jobs": open_jobs,
        "other_companies": other_companies,
    }
    return render(request, "jobs/company_detail.html", context)


def categories_list(request):
    categories = Category.objects.annotate(
        job_count=Count("jobs", filter=Q(jobs__status=Job.Status.APPROVED))
    ).order_by("-job_count", "name")

    total_active_jobs = Job.objects.filter(status=Job.Status.APPROVED).count()

    context = {
        "categories": categories,
        "total_active_jobs": total_active_jobs,
    }
    return render(request, "jobs/categories_list.html", context)


def candidate_sourcing(request):
    q = request.GET.get("q", "").strip()
    skill_filter = request.GET.get("skill", "").strip()
    location_filter = request.GET.get("location", "").strip()
    min_comp = request.GET.get("min_salary", "").strip()

    seekers_qs = (
        SeekerProfile.objects.select_related("user")
        .filter(user__is_active=True)
        .order_by("-updated_at")
    )

    if q:
        seekers_qs = seekers_qs.filter(
            Q(headline__icontains=q)
            | Q(skills__icontains=q)
            | Q(bio__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__username__icontains=q)
        )

    if skill_filter:
        seekers_qs = seekers_qs.filter(skills__icontains=skill_filter)

    if location_filter:
        seekers_qs = seekers_qs.filter(location__icontains=location_filter)

    if min_comp and min_comp.isdigit():
        seekers_qs = seekers_qs.filter(expected_salary__lte=int(min_comp))

    popular_skills = [
        "Python",
        "React",
        "Django",
        "TypeScript",
        "Node.js",
        "PostgreSQL",
        "Docker",
        "AWS",
        "Kubernetes",
        "Product Management",
        "UI/UX Design",
        "Machine Learning",
    ]

    paginator = Paginator(seekers_qs, 8)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_count": paginator.count,
        "popular_skills": popular_skills,
        "current_filters": {
            "q": q,
            "skill": skill_filter,
            "location": location_filter,
            "min_salary": min_comp,
        },
    }
    return render(request, "jobs/candidate_sourcing.html", context)
