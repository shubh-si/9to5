from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from jobs.models import Job, Category
from applications.models import Application

User = get_user_model()


class ApplicationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Design", slug="design")

        self.employer_user = User.objects.create_user(
            username="designstudio",
            email="hello@design.co",
            password="password123",
            role=User.Role.EMPLOYER,
        )

        self.job = Job.objects.create(
            employer=self.employer_user.employer_profile,
            category=self.category,
            title="UI/UX Designer",
            location="Remote",
            status=Job.Status.APPROVED,
        )

        self.seeker = User.objects.create_user(
            username="candidatetest",
            email="candidate@domain.com",
            password="password123",
            role=User.Role.JOB_SEEKER,
        )

        fake_resume = SimpleUploadedFile(
            "resume.pdf", b"Dummy resume content", content_type="application/pdf"
        )
        self.seeker.seeker_profile.resume = fake_resume
        self.seeker.seeker_profile.save()

    def test_ajax_apply_job(self):
        self.client.login(username="candidatetest", password="password123")

        response = self.client.post(
            reverse("applications:apply_job", kwargs={"job_id": self.job.id}),
            {
                "use_profile_resume": True,
                "cover_letter": "I am eager to join your design team.",
                "ajax": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(
            Application.objects.filter(job=self.job, applicant=self.seeker).exists()
        )

        dup_res = self.client.post(
            reverse("applications:apply_job", kwargs={"job_id": self.job.id}),
            {"use_profile_resume": True, "ajax": "1"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(dup_res.status_code, 400)

    def test_update_application_status(self):
        app = Application.objects.create(
            job=self.job, applicant=self.seeker, status=Application.Status.APPLIED
        )

        self.client.login(username="designstudio", password="password123")
        update_res = self.client.post(
            reverse("applications:update_status", kwargs={"application_id": app.id}),
            {"status": Application.Status.SHORTLISTED, "ajax": "1"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(update_res.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.SHORTLISTED)
