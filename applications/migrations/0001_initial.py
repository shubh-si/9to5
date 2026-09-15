import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("jobs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
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
                (
                    "resume",
                    models.FileField(
                        blank=True, null=True, upload_to="application_resumes/%Y/%m/"
                    ),
                ),
                ("cover_letter", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("APPLIED", "Applied"),
                            ("SHORTLISTED", "Shortlisted"),
                            ("REJECTED", "Rejected"),
                            ("HIRED", "Hired"),
                        ],
                        default="APPLIED",
                        max_length=20,
                    ),
                ),
                (
                    "employer_notes",
                    models.TextField(
                        blank=True, help_text="Private internal notes for hiring team"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="jobs.job",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("job", "applicant")},
            },
        ),
    ]
