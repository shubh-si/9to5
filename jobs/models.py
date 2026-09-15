from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=60,
        default="bi-briefcase",
        help_text="Bootstrap icon class, e.g. bi-code-slash, bi-palette, bi-graph-up",
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full-time"
        PART_TIME = "PART_TIME", "Part-time"
        REMOTE = "REMOTE", "Remote"
        INTERNSHIP = "INTERNSHIP", "Internship"
        CONTRACT = "CONTRACT", "Contract"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Moderation"
        APPROVED = "APPROVED", "Approved / Active"
        REJECTED = "REJECTED", "Rejected"
        CLOSED = "CLOSED", "Closed"

    class Experience(models.TextChoices):
        ENTRY = "ENTRY", "Entry Level (0-2 yrs)"
        MID = "MID", "Mid Level (2-5 yrs)"
        SENIOR = "SENIOR", "Senior Level (5+ yrs)"
        LEAD = "LEAD", "Lead / Executive"

    employer = models.ForeignKey(
        "accounts.EmployerProfile", on_delete=models.CASCADE, related_name="jobs"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="jobs"
    )
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    location = models.CharField(
        max_length=140, help_text="e.g. San Francisco, CA or Remote - US"
    )
    is_remote = models.BooleanField(default=False)
    job_type = models.CharField(
        max_length=25, choices=JobType.choices, default=JobType.FULL_TIME
    )
    experience_level = models.CharField(
        max_length=20, choices=Experience.choices, default=Experience.MID
    )
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_negotiable = models.BooleanField(default=False)

    description = models.TextField(
        help_text="Full role description and day-to-day responsibilities"
    )
    requirements = models.TextField(
        help_text="Required skills, qualifications, and stack"
    )
    benefits = models.TextField(
        blank=True, help_text="Perks, health cover, equity, etc."
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    views_count = models.PositiveIntegerField(default=0)
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def salary_display(self):
        if self.salary_negotiable and not (self.salary_min or self.salary_max):
            return "Negotiable"
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,} / yr"
        if self.salary_min:
            return f"From ${self.salary_min:,} / yr"
        if self.salary_max:
            return f"Up to ${self.salary_max:,} / yr"
        return "Not disclosed"

    def __str__(self):
        return f"{self.title} @ {self.employer.company_name}"


class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs"
    )
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="saved_by_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
