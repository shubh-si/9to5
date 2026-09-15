from django import forms
from .models import Job, Category


class JobPostForm(forms.ModelForm):
    deadline = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "category",
            "location",
            "is_remote",
            "job_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "salary_negotiable",
            "description",
            "requirements",
            "benefits",
            "deadline",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Senior Backend Engineer (Python/Django)",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. New York, NY or Remote - US",
                }
            ),
            "is_remote": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "job_type": forms.Select(attrs={"class": "form-select"}),
            "experience_level": forms.Select(attrs={"class": "form-select"}),
            "salary_min": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g. 90000"}
            ),
            "salary_max": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g. 130000"}
            ),
            "salary_negotiable": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Describe role responsibilities, daily work, and expectations...",
                }
            ),
            "requirements": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "List essential technical stack, experience, and nice-to-haves...",
                }
            ),
            "benefits": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Healthcare, 401(k), equity, flexible hours, annual learning budget...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_sal = cleaned_data.get("salary_min")
        max_sal = cleaned_data.get("salary_max")
        if min_sal and max_sal and min_sal > max_sal:
            self.add_error(
                "salary_max", "Maximum salary cannot be lower than minimum salary."
            )
        return cleaned_data
