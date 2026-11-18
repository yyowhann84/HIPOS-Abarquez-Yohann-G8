from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import UserProfile

User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_creates_member_and_hashes_password(self):
        response = self.client.post("/accounts/register/", {
            "username": "cleanupuser",
            "first_name": "Cleanup",
            "last_name": "Member",
            "email": "cleanup@example.com",
            "password1": "CampusCleanup!2026",
            "password2": "CampusCleanup!2026",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="cleanupuser")
        self.assertTrue(user.check_password("CampusCleanup!2026"))
        self.assertEqual(user.profile.role, UserProfile.Role.CLEANUP_MEMBER)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(username="first", email="same@example.com", password="SafePass!2026")
        response = self.client.post("/accounts/register/", {
            "username": "second", "first_name": "Second", "last_name": "User",
            "email": "SAME@example.com", "password1": "CampusCleanup!2026",
            "password2": "CampusCleanup!2026",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="second").exists())
