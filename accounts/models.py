from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
import uuid


class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = "SEEKER", "Job Seeker"
        EMPLOYER = "EMPLOYER", "Employer"
        ADMIN = "ADMIN", "Site Administrator"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.JOB_SEEKER
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, default="")

    @property
    def is_seeker(self):
        return self.role == self.Role.JOB_SEEKER

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class SeekerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="seeker_profile"
    )
    headline = models.CharField(
        max_length=160,
        blank=True,
        help_text="e.g. Senior Backend Engineer | Python & Cloud",
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    resume = models.FileField(upload_to="resumes/%Y/%m/", blank=True, null=True)
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated or tag list, e.g. Python, Django, PostgreSQL, Docker",
    )
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    expected_salary = models.PositiveIntegerField(
        blank=True, null=True, help_text="Annual USD or local currency"
    )

    experience_data = models.JSONField(default=list, blank=True)

    education_data = models.JSONField(default=list, blank=True)

    projects_data = models.JSONField(default=list, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def completion_percentage(self):
        fields = [
            self.headline,
            self.bio,
            self.location,
            self.resume,
            self.skills,
            self.experience_data,
            self.education_data,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    def __str__(self):
        return f"Seeker Profile: {self.user.username}"


class EmployerProfile(models.Model):
    SIZE_CHOICES = [
        ("1-10", "1-10 employees"),
        ("11-50", "11-50 employees"),
        ("51-200", "51-200 employees"),
        ("201-500", "201-500 employees"),
        ("500+", "500+ employees"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    company_name = models.CharField(max_length=160)
    company_slug = models.SlugField(max_length=180, unique=True, blank=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=40, choices=SIZE_CHOICES, blank=True)
    location = models.CharField(max_length=140, blank=True)
    description = models.TextField(blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.company_slug and self.company_name:
            base_slug = slugify(self.company_name)
            slug = base_slug
            counter = 1
            while (
                EmployerProfile.objects.filter(company_slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.company_slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name or f"Company for {self.user.username}"
