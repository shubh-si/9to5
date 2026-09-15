from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SeekerProfile, EmployerProfile


class SeekerProfileInline(admin.StackedInline):
    model = SeekerProfile
    can_delete = False
    verbose_name_plural = "Seeker Profile"
    fk_name = "user"


class EmployerProfileInline(admin.StackedInline):
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = "Employer Profile"
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "first_name",
        "last_name",
        "is_verified",
        "is_staff",
        "date_joined",
    )
    list_filter = ("role", "is_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Custom Profile Attributes",
            {
                "fields": (
                    "role",
                    "phone",
                    "avatar",
                    "is_verified",
                    "verification_token",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Custom Profile Attributes", {"fields": ("role", "email", "phone")}),
    )


@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline", "location", "expected_salary", "updated_at")
    search_fields = ("user__username", "user__email", "headline", "skills", "location")
    list_filter = ("location",)


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "user",
        "industry",
        "company_size",
        "location",
        "established_year",
    )
    search_fields = ("company_name", "user__username", "industry", "location")
    list_filter = ("industry", "company_size")
    prepopulated_fields = {"company_slug": ("company_name",)}
