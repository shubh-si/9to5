from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import SeekerProfile, EmployerProfile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            (User.Role.JOB_SEEKER, "Job Seeker"),
            (User.Role.EMPLOYER, "Employer"),
        ],
        widget=forms.RadioSelect(attrs={"class": "form-check-input role-radio-input"}),
        initial=User.Role.JOB_SEEKER,
        required=True,
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "name@example.com"}
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password (min 6 chars)"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm Password"}
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username or Email",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class UserBasicForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "avatar")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 (555) 000-0000"}
            ),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class SeekerProfileForm(forms.ModelForm):
    class Meta:
        model = SeekerProfile
        fields = (
            "headline",
            "bio",
            "location",
            "skills",
            "expected_salary",
            "resume",
            "portfolio_url",
            "github_url",
            "linkedin_url",
        )
        widgets = {
            "headline": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Senior Full-Stack Engineer",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Brief summary of your expertise and goals...",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. San Francisco, CA or Remote",
                }
            ),
            "skills": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Python, Django, React, PostgreSQL, Docker",
                }
            ),
            "expected_salary": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g. 110000"}
            ),
            "resume": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf,.doc,.docx"}
            ),
            "portfolio_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://yourportfolio.com",
                }
            ),
            "github_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username",
                }
            ),
            "linkedin_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://linkedin.com/in/username",
                }
            ),
        }


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = (
            "company_name",
            "logo",
            "website",
            "industry",
            "company_size",
            "location",
            "description",
            "established_year",
        )
        widgets = {
            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Acme Tech Solutions",
                }
            ),
            "logo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://acme.example.com",
                }
            ),
            "industry": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. SaaS / Cloud Infrastructure",
                }
            ),
            "company_size": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Austin, TX"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Tell candidates about your company mission, culture, and team...",
                }
            ),
            "established_year": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "2018"}
            ),
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your registered email",
                "autofocus": True,
            }
        ),
    )


class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter new password (min 6 characters)",
            }
        ),
        min_length=6,
        required=True,
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match. Please try again.")
        return cleaned_data
