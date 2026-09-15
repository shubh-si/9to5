from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "applicant_name",
        "job_title",
        "employer_name",
        "status",
        "created_at",
        "has_resume",
    )
    list_filter = ("status", "created_at", "job__category")
    search_fields = (
        "applicant__username",
        "applicant__email",
        "job__title",
        "job__employer__company_name",
    )
    readonly_fields = ("created_at", "updated_at")

    def applicant_name(self, obj):
        return obj.applicant.get_full_name() or obj.applicant.username

    applicant_name.short_description = "Applicant"

    def job_title(self, obj):
        return obj.job.title

    job_title.short_description = "Applied Job"

    def employer_name(self, obj):
        return obj.job.employer.company_name

    employer_name.short_description = "Company"

    def has_resume(self, obj):
        return bool(obj.resume)

    has_resume.boolean = True
