from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    about_view,
    contact_view,
    pricing_view,
    faq_view,
    career_advice_view,
    privacy_view,
    terms_view,
    security_view,
)
from jobs import views as job_views
from accounts import views as account_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("pricing/", pricing_view, name="pricing"),
    path("faq/", faq_view, name="faq"),
    path("career-advice/", career_advice_view, name="career_advice"),
    path("privacy/", privacy_view, name="privacy"),
    path("terms/", terms_view, name="terms"),
    path("security/", security_view, name="security"),
    path("companies/", job_views.companies_list, name="companies_list"),
    path("companies/<slug:slug>/", job_views.company_detail, name="company_detail"),
    path("categories/", job_views.categories_list, name="categories_list"),
    path("candidates/", job_views.candidate_sourcing, name="candidate_sourcing"),
    path("resume-builder/", account_views.resume_builder_view, name="resume_builder"),
    path("accounts/", include("accounts.urls")),
    path("jobs/", include("jobs.urls")),
    path("applications/", include("applications.urls")),
    path("dashboard/", include("dashboard.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_header = "JobPortal Administration"
admin.site.site_title = "JobPortal Admin Portal"
admin.site.index_title = "Platform Management"
