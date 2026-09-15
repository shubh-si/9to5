from django.db import models
from django.conf import settings


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        REJECTED = "REJECTED", "Rejected"
        HIRED = "HIRED", "Hired"

    job = models.ForeignKey(
        "jobs.Job", on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.FileField(
        upload_to="application_resumes/%Y/%m/", blank=True, null=True
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.APPLIED
    )
    employer_notes = models.TextField(
        blank=True, help_text="Private internal notes for hiring team"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job", "applicant")
        ordering = ["-created_at"]

    @property
    def status_badge_class(self):
        mapping = {
            self.Status.APPLIED: "bg-primary-subtle text-primary border-primary-subtle",
            self.Status.SHORTLISTED: "bg-warning-subtle text-warning-emphasis border-warning-subtle",
            self.Status.REJECTED: "bg-danger-subtle text-danger border-danger-subtle",
            self.Status.HIRED: "bg-success-subtle text-success border-success-subtle",
        }
        return mapping.get(self.status, "bg-secondary text-white")

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title} ({self.get_status_display()})"
