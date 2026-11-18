from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from .models import CleanupArea, Event


class RoleAccessTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(username="member", email="member@example.com", password="SafePass!2026")
        UserProfile.objects.create(user=self.member, role=UserProfile.Role.CLEANUP_MEMBER)
        self.organizer = User.objects.create_user(username="organizer", email="organizer@example.com", password="SafePass!2026")
        UserProfile.objects.create(user=self.organizer, role=UserProfile.Role.ORGANIZER)

    def test_member_cannot_open_organizer_dashboard(self):
        self.client.login(username="member", password="SafePass!2026")
        response = self.client.get(reverse("organizer_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_organizer_can_create_event(self):
        self.client.login(username="organizer", password="SafePass!2026")
        response = self.client.post(reverse("event_create"), {
            "title": "Campus Forum", "event_date": (date.today() + timedelta(days=5)).isoformat(),
            "venue": "Gymnasium", "details": "Post-event cleanup test", "status": "open",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title="Campus Forum", created_by=self.organizer).exists())
