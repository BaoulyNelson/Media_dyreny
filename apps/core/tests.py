from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SiteSettingsViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="Password123",
            is_staff=True,
        )

    def test_settings_page_requires_staff_access(self):
        response = self.client.get(reverse("core:settings"))
        self.assertEqual(response.status_code, 302)

        self.client.login(username="admin", password="Password123")
        response = self.client.get(reverse("core:settings"))
        self.assertEqual(response.status_code, 200)
