from django.contrib import admin
from .models import Category, Job, SavedJob


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "job_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def job_count(self, obj):
        return obj.jobs.count()

    job_count.short_description = "Active Postings"


@admin.action(description="Approve selected job postings")
def approve_jobs(modeladmin, request, queryset):
    updated = queryset.update(status=Job.Status.APPROVED)
    modeladmin.message_user(request, f"{updated} job(s) approved and marked active.")


@admin.action(description="Reject selected job postings")
def reject_jobs(modeladmin, request, queryset):
    updated = queryset.update(status=Job.Status.REJECTED)
    modeladmin.message_user(request, f"{updated} job(s) rejected.")


@admin.action(description="Close selected job postings")
def close_jobs(modeladmin, request, queryset):
    updated = queryset.update(status=Job.Status.CLOSED)
    modeladmin.message_user(request, f"{updated} job(s) closed.")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer_name",
        "category",
        "job_type",
        "location",
        "status",
        "views_count",
        "created_at",
    )
    list_filter = (
        "status",
        "job_type",
        "experience_level",
        "is_remote",
        "category",
        "created_at",
    )
    search_fields = ("title", "employer__company_name", "description", "location")
    prepopulated_fields = {"slug": ("title",)}
    actions = [approve_jobs, reject_jobs, close_jobs]
    readonly_fields = ("views_count", "created_at", "updated_at")

    def employer_name(self, obj):
        return obj.employer.company_name

    employer_name.short_description = "Company"


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")
    search_fields = ("user__username", "job__title")
    list_filter = ("created_at",)
