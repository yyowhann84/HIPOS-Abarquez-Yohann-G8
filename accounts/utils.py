from .models import UserProfile


def role_for(user):
    """Return a user's role, treating legacy users without a profile as members."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.Role.ORGANIZER
    profile = getattr(user, "profile", None)
    return profile.role if profile else UserProfile.Role.CLEANUP_MEMBER
