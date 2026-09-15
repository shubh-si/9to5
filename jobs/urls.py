from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("post/", views.job_create, name="job_create"),
    path("companies/", views.companies_list, name="companies_list"),
    path("companies/<slug:slug>/", views.company_detail, name="company_detail"),
    path("categories/", views.categories_list, name="categories_list"),
    path("candidates/", views.candidate_sourcing, name="candidate_sourcing"),
    path("<slug:slug>/", views.job_detail, name="job_detail"),
    path("<slug:slug>/edit/", views.job_edit, name="job_edit"),
    path("<slug:slug>/delete/", views.job_delete, name="job_delete"),
    path("<int:job_id>/toggle-save/", views.toggle_save_job, name="toggle_save"),
]
