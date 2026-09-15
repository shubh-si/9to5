from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/seeker/", views.seeker_profile_edit, name="seeker_profile_edit"),
    path(
        "profile/employer/", views.employer_profile_edit, name="employer_profile_edit"
    ),
    path("verify-email/", views.verify_email_stub, name="verify_email"),
    path("password-reset/", views.password_reset_request_view, name="password_reset"),
    path(
        "password-reset/confirm/<str:token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path("resume-builder/", views.resume_builder_view, name="resume_builder"),
]
