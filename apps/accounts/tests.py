from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123",
        )

    def test_login_with_email_works(self):
        response = self.client.post(
            reverse("accounts:connexion"),
            {"username": "alice@example.com", "password": "StrongPass123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="form-control"')

    def test_password_reset_redirects_to_done_page(self):
        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            response = self.client.post(
                reverse("accounts:password_reset"),
                {"email": self.user.email},
            )

        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn("/comptes/reinitialiser/", mail.outbox[0].body)

    def test_password_reset_confirm_displays_styled_toggle_fields(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.get(
            reverse(
                "accounts:password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="id_new_password1"')
        self.assertContains(response, 'id="id_new_password2"')
        self.assertContains(response, 'class="form-control"')
        self.assertContains(response, 'class="pw-toggle"', count=2)

    def test_logout_shows_success_message_after_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:deconnexion"), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "Vous avez été déconnecté avec succès.")
