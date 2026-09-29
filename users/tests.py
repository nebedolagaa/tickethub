from django.test import TestCase

# Create your tests here.


from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Account


# Sikkerhetstester for innlogging og tilbakestilling av passord
class AuthSecurityTestCase(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user("Test", "Bruker", "bruker@example.com", "GammeltPassord123")

    def test_login_is_blocked_after_too_many_attempts(self):
        for _ in range(5):
            self.client.post(reverse("users:login"), {"email": "bruker@example.com", "password": "feil"})
        # riktig passord hjelper ikke når kontoen er midlertidig låst
        self.client.post(reverse("users:login"), {"email": "bruker@example.com", "password": "GammeltPassord123"})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_forgot_password_gives_same_answer_for_unknown_email(self):
        known = self.client.post(reverse("users:forgotPassword"), {"email": "bruker@example.com"}, follow=True)
        unknown = self.client.post(reverse("users:forgotPassword"), {"email": "finnes.ikke@example.com"}, follow=True)
        self.assertEqual(
            [str(m) for m in known.context["messages"]], [str(m) for m in unknown.context["messages"]]
        )
        self.assertEqual(len(mail.outbox), 1)

    def _open_reset_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        self.client.get(reverse("users:resetpassword_validate", args=[uid, token]))

    def test_reset_rejects_weak_password(self):
        self._open_reset_link()
        self.client.post(reverse("users:resetPassword"), {"password": "123", "confirm_password": "123"})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("GammeltPassord123"))

    def test_reset_link_can_only_be_used_once(self):
        self._open_reset_link()
        self.client.post(reverse("users:resetPassword"), {"password": "NyttPassord!2027", "confirm_password": "NyttPassord!2027"})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NyttPassord!2027"))
        self.assertNotIn("uid", self.client.session)
