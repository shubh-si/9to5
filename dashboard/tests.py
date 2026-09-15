from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import Job, Category
from accounts.models import EmployerProfile

User = get_user_model()


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Technology", slug="tech")

        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@domain.com",
            password="password123",
            role=User.Role.ADMIN,
        )

        self.employer_user = User.objects.create_user(
            username="companyboss",
            email="boss@company.com",
            password="password123",
            role=User.Role.EMPLOYER,
        )

        self.seeker_user = User.objects.create_user(
            username="talentedseeker",
            email="seeker@domain.com",
            password="password123",
            role=User.Role.JOB_SEEKER,
        )

        self.pending_job = Job.objects.create(
            employer=self.employer_user.employer_profile,
            category=self.category,
            title="Pending Review Engineer",
            location="San Francisco",
            status=Job.Status.PENDING,
        )

    def test_dashboard_redirection(self):

        self.client.login(username="talentedseeker", password="password123")
        res = self.client.get(reverse("dashboard:redirect_dashboard"))
        self.assertRedirects(res, reverse("dashboard:seeker_dashboard"))

        self.client.login(username="companyboss", password="password123")
        res = self.client.get(reverse("dashboard:redirect_dashboard"))
        self.assertRedirects(res, reverse("dashboard:employer_dashboard"))

        self.client.login(username="adminuser", password="password123")
        res = self.client.get(reverse("dashboard:redirect_dashboard"))
        self.assertRedirects(res, reverse("dashboard:admin_dashboard"))

    def test_admin_dashboard_moderation_queue(self):
        self.client.login(username="adminuser", password="password123")
        res = self.client.get(reverse("dashboard:admin_dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Pending Review Engineer")

        approve_res = self.client.post(
            reverse(
                "dashboard:admin_moderate_job",
                kwargs={"job_id": self.pending_job.id, "action": "approve"},
            ),
            {"ajax": "1"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(approve_res.status_code, 200)
        self.pending_job.refresh_from_db()
        self.assertEqual(self.pending_job.status, Job.Status.APPROVED)
