import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                (
                    "icon",
                    models.CharField(
                        default="bi-briefcase",
                        help_text="Bootstrap icon class, e.g. bi-code-slash, bi-palette, bi-graph-up",
                        max_length=60,
                    ),
                ),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                (
                    "location",
                    models.CharField(
                        help_text="e.g. San Francisco, CA or Remote - US",
                        max_length=140,
                    ),
                ),
                ("is_remote", models.BooleanField(default=False)),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("FULL_TIME", "Full-time"),
                            ("PART_TIME", "Part-time"),
                            ("REMOTE", "Remote"),
                            ("INTERNSHIP", "Internship"),
                            ("CONTRACT", "Contract"),
                        ],
                        default="FULL_TIME",
                        max_length=25,
                    ),
                ),
                (
                    "experience_level",
                    models.CharField(
                        choices=[
                            ("ENTRY", "Entry Level (0-2 yrs)"),
                            ("MID", "Mid Level (2-5 yrs)"),
                            ("SENIOR", "Senior Level (5+ yrs)"),
                            ("LEAD", "Lead / Executive"),
                        ],
                        default="MID",
                        max_length=20,
                    ),
                ),
                ("salary_min", models.PositiveIntegerField(blank=True, null=True)),
                ("salary_max", models.PositiveIntegerField(blank=True, null=True)),
                ("salary_negotiable", models.BooleanField(default=False)),
                (
                    "description",
                    models.TextField(
                        help_text="Full role description and day-to-day responsibilities"
                    ),
                ),
                (
                    "requirements",
                    models.TextField(
                        help_text="Required skills, qualifications, and stack"
                    ),
                ),
                (
                    "benefits",
                    models.TextField(
                        blank=True, help_text="Perks, health cover, equity, etc."
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending Moderation"),
                            ("APPROVED", "Approved / Active"),
                            ("REJECTED", "Rejected"),
                            ("CLOSED", "Closed"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("views_count", models.PositiveIntegerField(default=0)),
                ("deadline", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="jobs",
                        to="jobs.category",
                    ),
                ),
                (
                    "employer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="accounts.employerprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SavedJob",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_by_users",
                        to="jobs.job",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "job")},
            },
        ),
    ]
