from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    use_profile_resume = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "id": "useProfileResume"}
        ),
    )

    class Meta:
        model = Application
        fields = ["cover_letter", "resume"]
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Tell the employer why your experience makes you a stellar fit for this role...",
                }
            ),
            "resume": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "id": "applicationResumeInput",
                    "accept": ".pdf,.doc,.docx",
                }
            ),
        }
