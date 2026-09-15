from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("<int:application_id>/resume/", views.download_resume, name="download_resume"),
    path(
        "<int:application_id>/status/",
        views.update_application_status,
        name="update_status",
    ),
]
