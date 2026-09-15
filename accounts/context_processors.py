def user_roles(request):
    if not request.user.is_authenticated:
        return {
            "is_seeker": False,
            "is_employer": False,
            "is_admin_user": False,
            "current_profile": None,
        }

    user = request.user
    role = getattr(user, "role", None)

    profile = None
    if role == "SEEKER":
        profile = getattr(user, "seeker_profile", None)
    elif role == "EMPLOYER":
        profile = getattr(user, "employer_profile", None)

    return {
        "is_seeker": role == "SEEKER",
        "is_employer": role == "EMPLOYER",
        "is_admin_user": role == "ADMIN" or user.is_superuser or user.is_staff,
        "current_profile": profile,
    }
