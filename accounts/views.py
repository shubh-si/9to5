import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserBasicForm,
    SeekerProfileForm,
    EmployerProfileForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
)
from .models import User, SeekerProfile, EmployerProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:redirect_dashboard")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to JobPortal, {user.username}! Your account has been created.",
            )

            messages.info(
                request,
                "A verification link has been sent to your email (stub simulation mode).",
            )

            if user.role == User.Role.EMPLOYER:
                return redirect("accounts:employer_profile_edit")
            return redirect("accounts:seeker_profile_edit")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        role_param = request.GET.get("role", "").strip().upper()
        if role_param in ["EMPLOYER", "COMPANY", "RECRUITER", "HIRE"]:
            initial_role = User.Role.EMPLOYER
        else:
            initial_role = User.Role.JOB_SEEKER
        form = UserRegistrationForm(initial={"role": initial_role})

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:redirect_dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("dashboard:redirect_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def seeker_profile_edit(request):
    if not request.user.is_seeker and not request.user.is_superuser:
        messages.warning(request, "This page is intended for job seekers.")

    profile, _ = SeekerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserBasicForm(request.POST, request.FILES, instance=request.user)
        profile_form = SeekerProfileForm(request.POST, request.FILES, instance=profile)

        exp_titles = request.POST.getlist("exp_title[]")
        exp_companies = request.POST.getlist("exp_company[]")
        exp_periods = request.POST.getlist("exp_period[]")
        exp_descriptions = request.POST.getlist("exp_description[]")

        edu_degrees = request.POST.getlist("edu_degree[]")
        edu_institutions = request.POST.getlist("edu_institution[]")
        edu_years = request.POST.getlist("edu_year[]")

        experience_list = []
        for i in range(len(exp_titles)):
            if exp_titles[i].strip():
                experience_list.append(
                    {
                        "title": exp_titles[i].strip(),
                        "company": exp_companies[i].strip()
                        if i < len(exp_companies)
                        else "",
                        "period": exp_periods[i].strip()
                        if i < len(exp_periods)
                        else "",
                        "description": exp_descriptions[i].strip()
                        if i < len(exp_descriptions)
                        else "",
                    }
                )

        education_list = []
        for j in range(len(edu_degrees)):
            if edu_degrees[j].strip():
                education_list.append(
                    {
                        "degree": edu_degrees[j].strip(),
                        "institution": edu_institutions[j].strip()
                        if j < len(edu_institutions)
                        else "",
                        "year": edu_years[j].strip() if j < len(edu_years) else "",
                    }
                )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            p = profile_form.save(commit=False)
            p.experience_data = experience_list
            p.education_data = education_list
            p.save()
            messages.success(request, "Your profile has been successfully updated!")
            return redirect("accounts:seeker_profile_edit")
        else:
            messages.error(request, "Please check for errors in the form.")
    else:
        user_form = UserBasicForm(instance=request.user)
        profile_form = SeekerProfileForm(instance=profile)

    return render(
        request,
        "accounts/seeker_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
            "experiences": profile.experience_data or [],
            "educations": profile.education_data or [],
        },
    )


@login_required
def employer_profile_edit(request):
    if not request.user.is_employer and not request.user.is_superuser:
        messages.warning(request, "This page is intended for employers.")

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": f"{request.user.username}'s Company"},
    )

    if request.method == "POST":
        user_form = UserBasicForm(request.POST, request.FILES, instance=request.user)
        profile_form = EmployerProfileForm(
            request.POST, request.FILES, instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Company profile updated successfully!")
            return redirect("accounts:employer_profile_edit")
        else:
            err_items = []
            for f in [user_form, profile_form]:
                for field_name, errors in f.errors.items():
                    field_obj = f.fields.get(field_name)
                    label = (
                        field_obj.label
                        if (field_obj and field_obj.label)
                        else field_name.replace("_", " ").title()
                    )
                    err_items.append(f"{label}: {errors[0]}")
            msg = (
                "Please correct the following: " + "; ".join(err_items)
                if err_items
                else "Please check form errors."
            )
            messages.error(request, msg)
    else:
        user_form = UserBasicForm(instance=request.user)
        profile_form = EmployerProfileForm(instance=profile)

    return render(
        request,
        "accounts/employer_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile": profile,
        },
    )


@login_required
def verify_email_stub(request):
    token = request.GET.get("token")
    user = request.user

    if token and user.verification_token == token:
        user.is_verified = True
        user.save()
        messages.success(
            request,
            "Email verified successfully! Your profile now has verified status.",
        )
    elif request.method == "POST":
        user.is_verified = True
        user.save()
        messages.success(request, "Email verified successfully!")
    else:
        messages.info(
            request,
            f"Simulated verification link: /accounts/verify-email/?token={user.verification_token}",
        )

    return redirect("dashboard:redirect_dashboard")


def password_reset_request_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:redirect_dashboard")

    reset_sent = False
    simulated_reset_url = None
    target_email = ""

    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email__iexact=email).first()
            reset_sent = True
            target_email = email
            if user:
                if not user.verification_token:
                    import uuid

                    user.verification_token = uuid.uuid4().hex
                    user.save(update_fields=["verification_token"])
                simulated_reset_url = (
                    f"/accounts/password-reset/confirm/{user.verification_token}/"
                )
                messages.success(
                    request,
                    f"Password reset instructions have been generated for {email}.",
                )
            else:
                messages.info(
                    request,
                    f"If an account exists for {email}, a reset link has been dispatched.",
                )
    else:
        form = PasswordResetRequestForm()

    return render(
        request,
        "accounts/password_reset.html",
        {
            "form": form,
            "reset_sent": reset_sent,
            "simulated_reset_url": simulated_reset_url,
            "target_email": target_email,
        },
    )


def password_reset_confirm_view(request, token):
    if request.user.is_authenticated:
        return redirect("dashboard:redirect_dashboard")

    user = get_object_or_404(User, verification_token=token)

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            user.set_password(new_password)
            import uuid

            user.verification_token = uuid.uuid4().hex
            user.save()
            messages.success(
                request,
                "Your password has been updated successfully! Please sign in with your new credentials.",
            )
            return redirect("accounts:login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SetNewPasswordForm()

    return render(
        request,
        "accounts/password_reset_confirm.html",
        {"form": form, "user_obj": user, "token": token},
    )


def resume_builder_view(request):
    profile = None
    if request.user.is_authenticated:
        profile, _ = SeekerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Please sign in or register to save your resume to your account.",
            )
            return redirect("accounts:login")

        action_type = request.POST.get("action_type", "builder")

        if action_type == "upload_file":
            uploaded_file = request.FILES.get("resume_file")
            if uploaded_file:
                profile.resume = uploaded_file
                profile.save()
                messages.success(
                    request,
                    f"Resume document '{uploaded_file.name}' uploaded successfully!",
                )
            else:
                messages.error(
                    request,
                    "Please select a PDF or Word document (.pdf, .doc, .docx) to upload.",
                )
            return redirect("accounts:resume_builder")

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()

        user = request.user
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        user.save()

        profile.headline = request.POST.get("headline", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.skills = request.POST.get("skills", "").strip()
        profile.portfolio_url = request.POST.get("portfolio_url", "").strip()
        profile.github_url = request.POST.get("github_url", "").strip()
        profile.linkedin_url = request.POST.get("linkedin_url", "").strip()

        exp_salary = request.POST.get("expected_salary", "").strip()
        if exp_salary and exp_salary.isdigit():
            profile.expected_salary = int(exp_salary)

        exp_titles = request.POST.getlist("exp_title[]")
        exp_companies = request.POST.getlist("exp_company[]")
        exp_periods = request.POST.getlist("exp_period[]")
        exp_descriptions = request.POST.getlist("exp_description[]")

        experience_list = []
        for i in range(len(exp_titles)):
            if exp_titles[i].strip():
                experience_list.append(
                    {
                        "title": exp_titles[i].strip(),
                        "company": exp_companies[i].strip()
                        if i < len(exp_companies)
                        else "",
                        "period": exp_periods[i].strip()
                        if i < len(exp_periods)
                        else "",
                        "description": exp_descriptions[i].strip()
                        if i < len(exp_descriptions)
                        else "",
                    }
                )
        profile.experience_data = experience_list

        edu_degrees = request.POST.getlist("edu_degree[]")
        edu_institutions = request.POST.getlist("edu_institution[]")
        edu_years = request.POST.getlist("edu_year[]")

        education_list = []
        for j in range(len(edu_degrees)):
            if edu_degrees[j].strip():
                education_list.append(
                    {
                        "degree": edu_degrees[j].strip(),
                        "institution": edu_institutions[j].strip()
                        if j < len(edu_institutions)
                        else "",
                        "year": edu_years[j].strip() if j < len(edu_years) else "",
                    }
                )
        profile.education_data = education_list

        proj_titles = request.POST.getlist("proj_title[]")
        proj_techs = request.POST.getlist("proj_tech[]")
        proj_links = request.POST.getlist("proj_link[]")
        proj_descriptions = request.POST.getlist("proj_description[]")

        project_list = []
        for k in range(len(proj_titles)):
            if proj_titles[k].strip():
                project_list.append(
                    {
                        "title": proj_titles[k].strip(),
                        "tech": proj_techs[k].strip() if k < len(proj_techs) else "",
                        "link": proj_links[k].strip() if k < len(proj_links) else "",
                        "description": proj_descriptions[k].strip()
                        if k < len(proj_descriptions)
                        else "",
                    }
                )
        profile.projects_data = project_list

        if "builder_resume_file" in request.FILES:
            profile.resume = request.FILES["builder_resume_file"]

        profile.save()
        messages.success(
            request, "Your structured resume has been saved and synced to your profile!"
        )
        return redirect("accounts:resume_builder")

    sample_experiences = [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Innovations Inc.",
            "period": "2022 - Present",
            "description": "Designed and implemented resilient microservices handling 20k+ RPM with 99.99% uptime. Optimized database query latencies by 35% using Redis caching.",
        },
        {
            "title": "Full Stack Developer",
            "company": "NextGen Apps",
            "period": "2020 - 2022",
            "description": "Engineered interactive user interfaces using React and decoupled Django REST APIs. Mentored 4 junior engineers on clean architecture.",
        },
    ]

    sample_educations = [
        {
            "degree": "B.S. in Computer Science",
            "institution": "State University",
            "year": "2020",
        }
    ]

    sample_projects = [
        {
            "title": "Distributed Job Queue Engine",
            "tech": "Python, Celery, Redis, Docker",
            "link": "https://github.com/example/job-queue",
            "description": "Asynchronous task orchestration engine with automated retry backoff and Prometheus metrics exporter.",
        }
    ]

    experiences = (
        profile.experience_data
        if profile and profile.experience_data
        else sample_experiences
    )
    educations = (
        profile.education_data
        if profile and profile.education_data
        else sample_educations
    )
    projects = (
        profile.projects_data if profile and profile.projects_data else sample_projects
    )

    context = {
        "profile": profile,
        "experiences": experiences,
        "educations": educations,
        "projects": projects,
    }
    return render(request, "accounts/resume_builder.html", context)
