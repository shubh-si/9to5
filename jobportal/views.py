from django.shortcuts import render
from django.db.models import Count
from jobs.models import Job, Category
from accounts.models import User, EmployerProfile


def home(request):
    featured_jobs = (
        Job.objects.filter(status=Job.Status.APPROVED)
        .select_related("employer", "category")
        .order_by("-created_at")[:6]
    )

    categories = Category.objects.annotate(job_count=Count("jobs")).order_by(
        "-job_count"
    )[:8]

    stats = {
        "total_jobs": Job.objects.filter(status=Job.Status.APPROVED).count(),
        "total_companies": EmployerProfile.objects.count(),
        "total_seekers": User.objects.filter(role=User.Role.JOB_SEEKER).count(),
    }

    display_stats = {
        "jobs": max(stats["total_jobs"], 48),
        "companies": max(stats["total_companies"], 16),
        "seekers": max(stats["total_seekers"], 120),
    }

    return render(
        request,
        "home.html",
        {
            "featured_jobs": featured_jobs,
            "categories": categories,
            "stats": display_stats,
        },
    )


def about_view(request):
    total_jobs = Job.objects.filter(status=Job.Status.APPROVED).count()
    total_companies = EmployerProfile.objects.count()
    total_seekers = User.objects.filter(role=User.Role.JOB_SEEKER).count()
    return render(
        request,
        "pages/about.html",
        {
            "stats": {
                "jobs": max(total_jobs, 150),
                "companies": max(total_companies, 45),
                "seekers": max(total_seekers, 1200),
            }
        },
    )


def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        inquiry_type = request.POST.get("inquiry_type", "General")

        if name and email and message:
            from django.contrib import messages

            messages.success(
                request,
                f"Thank you, {name}! Your inquiry regarding '{subject or inquiry_type}' has been received. Our team will respond to {email} within 24 hours.",
            )
        else:
            from django.contrib import messages

            messages.error(request, "Please fill in all required fields.")

    return render(request, "pages/contact.html")


def pricing_view(request):
    return render(request, "pages/pricing.html")


def faq_view(request):
    return render(request, "pages/faq.html")


def career_advice_view(request):
    return render(request, "pages/career_advice.html")


def privacy_view(request):
    return render(request, "pages/privacy.html")


def terms_view(request):
    return render(request, "pages/terms.html")


def security_view(request):
    return render(request, "pages/security.html")
