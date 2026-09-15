from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.redirect_dashboard, name="redirect_dashboard"),
    path("seeker/", views.seeker_dashboard, name="seeker_dashboard"),
    path("employer/", views.employer_dashboard, name="employer_dashboard"),
    path(
        "employer/jobs/<slug:job_slug>/applicants/",
        views.job_applicants,
        name="job_applicants",
    ),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path(
        "admin/moderate/<int:job_id>/<str:action>/",
        views.admin_moderate_job,
        name="admin_moderate_job",
    ),
]
