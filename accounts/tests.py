from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_signup_and_login_work_with_current_allauth(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newmember",
                "email": "member@example.test",
                "password1": "Uncommon!MemberPass492",
                "password2": "Uncommon!MemberPass492",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(username="newmember").exists()
        )
        self.assertIn("_auth_user_id", self.client.session)
        self.client.logout()
        response = self.client.post(
            reverse("account_login"),
            {"login": "newmember", "password": "Uncommon!MemberPass492"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_signup_rejects_weak_password(self):
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "weak",
                "email": "weak@example.test",
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="weak").exists()
        )
