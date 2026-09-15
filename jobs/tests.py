from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category, Job, SavedJob
from accounts.models import EmployerProfile

User = get_user_model()


class JobsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Engineering", slug="engineering")

        self.employer_user = User.objects.create_user(
            username="techcorp",
            email="hr@techcorp.com",
            password="password123",
            role=User.Role.EMPLOYER,
        )
        self.employer_profile = self.employer_user.employer_profile
        self.employer_profile.company_name = "TechCorp Solutions"
        self.employer_profile.save()

        self.seeker_user = User.objects.create_user(
            username="jobseeker",
            email="seeker@domain.com",
            password="password123",
            role=User.Role.JOB_SEEKER,
        )

        self.job = Job.objects.create(
            employer=self.employer_profile,
            category=self.category,
            title="Django Backend Developer",
            location="Austin, TX",
            is_remote=True,
            job_type=Job.JobType.FULL_TIME,
            experience_level=Job.Experience.MID,
            salary_min=100000,
            salary_max=130000,
            description="Build web services with Django and PostgreSQL.",
            requirements="Python, Django, SQL",
            status=Job.Status.APPROVED,
        )

    def test_job_list_view_and_ajax_search(self):

        res = self.client.get(reverse("jobs:job_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Django Backend Developer")

        ajax_res = self.client.get(
            reverse("jobs:job_list"),
            {"q": "Django"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(ajax_res.status_code, 200)
        data = ajax_res.json()
        self.assertIn("html", data)
        self.assertEqual(data["total_count"], 1)

    def test_job_detail_view_and_view_count(self):
        initial_views = self.job.views_count
        res = self.client.get(
            reverse("jobs:job_detail", kwargs={"slug": self.job.slug})
        )
        self.assertEqual(res.status_code, 200)
        self.job.refresh_from_db()
        self.assertEqual(self.job.views_count, initial_views + 1)

    def test_toggle_bookmark_ajax(self):
        self.client.login(username="jobseeker", password="password123")

        res = self.client.post(
            reverse("jobs:toggle_save", kwargs={"job_id": self.job.id})
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["saved"])
        self.assertTrue(
            SavedJob.objects.filter(user=self.seeker_user, job=self.job).exists()
        )

        res2 = self.client.post(
            reverse("jobs:toggle_save", kwargs={"job_id": self.job.id})
        )
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()["saved"])
        self.assertFalse(
            SavedJob.objects.filter(user=self.seeker_user, job=self.job).exists()
        )
