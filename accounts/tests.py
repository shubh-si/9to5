from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import SeekerProfile, EmployerProfile

User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_creation_and_signal_profiles(self):

        seeker = User.objects.create_user(
            username="testseeker",
            email="seeker@example.com",
            password="password123",
            role=User.Role.JOB_SEEKER,
        )
        self.assertTrue(seeker.is_seeker)
        self.assertFalse(seeker.is_employer)
        self.assertTrue(SeekerProfile.objects.filter(user=seeker).exists())
        self.assertTrue(seeker.groups.filter(name="Job Seekers").exists())

        employer = User.objects.create_user(
            username="testemployer",
            email="employer@example.com",
            password="password123",
            role=User.Role.EMPLOYER,
        )
        self.assertTrue(employer.is_employer)
        self.assertFalse(employer.is_seeker)
        self.assertTrue(EmployerProfile.objects.filter(user=employer).exists())
        self.assertTrue(employer.groups.filter(name="Employers").exists())

    def test_registration_view(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "newuserpass123",
                "password2": "newuserpass123",
                "role": User.Role.JOB_SEEKER,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_and_logout(self):
        User.objects.create_user(
            username="loginuser", email="login@example.com", password="password123"
        )
        login_res = self.client.post(
            reverse("accounts:login"),
            {"username": "loginuser", "password": "password123"},
        )
        self.assertEqual(login_res.status_code, 302)

        logout_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(logout_res.status_code, 302)
