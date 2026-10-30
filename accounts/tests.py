import re
from datetime import timedelta
from html.parser import HTMLParser
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
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


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "resetmember",
            email="resetmember@example.test",
            password="Original!UniquePass492",
        )
        self.uid = user_pk_to_url_str(self.user)
        self.request_url = reverse("account_reset_password")
        mail.outbox.clear()

    def reset_url(self, token):
        return reverse(
            "account_reset_password_from_key",
            kwargs={"uidb36": self.uid, "key": token},
        )

    def assert_unavailable_link(self, response):
        self.assertContains(response, "invalid or has expired")
        self.assertContains(response, self.request_url)
        self.assertContains(response, "Request a new reset link")
        self.assertNotContains(response, 'name="password1"')
        self.assertNotContains(response, 'name="password2"')
        self.assertNotContains(response, ">Reset Password</button>")

    def test_invalid_reset_link_explains_recovery_without_password_form(self):
        self.assert_unavailable_link(
            self.client.get(self.reset_url("invalid-token"))
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Original!UniquePass492"))

    def test_expired_reset_link_offers_fresh_request(self):
        expired_time = default_token_generator._now() - timedelta(
            seconds=settings.PASSWORD_RESET_TIMEOUT + 1
        )
        with patch.object(
            default_token_generator, "_now", return_value=expired_time
        ):
            token = default_token_generator.make_token(self.user)
        self.assert_unavailable_link(self.client.get(self.reset_url(token)))

    def test_clean_reset_url_without_original_browser_session_is_unavailable(
        self,
    ):
        self.assert_unavailable_link(
            self.client.get(self.reset_url("set-password"))
        )

    def test_requested_reset_email_and_valid_password_change_progression(self):
        response = self.client.post(
            self.request_url, {"email": self.user.email}
        )
        self.assertRedirects(response, reverse("account_reset_password_done"))
        self.assertEqual(len(mail.outbox), 1)
        links = re.findall(r"https?://[^\s<>]+", mail.outbox[0].body)
        reset_link = next(
            link for link in links if "/password/reset/key/" in link
        )
        initial_path = urlsplit(reset_link).path
        response = self.client.get(initial_path)
        self.assertEqual(response.status_code, 302)
        clean_path = self.reset_url("set-password")
        self.assertEqual(urlsplit(response.url).path, clean_path)
        response = self.client.get(clean_path)
        self.assertContains(response, "Choose a New Password")
        self.assertContains(response, 'name="password1"')
        self.assertNotContains(response, "invalid or has expired")

        response = self.client.post(
            clean_path,
            {
                "password1": "Changed!UniquePass825",
                "password2": "Different!UniquePass825",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Original!UniquePass492"))

        response = self.client.post(
            clean_path,
            {
                "password1": "Changed!UniquePass825",
                "password2": "Changed!UniquePass825",
            },
        )
        self.assertRedirects(
            response, reverse("account_reset_password_from_key_done")
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Changed!UniquePass825"))
        self.assertFalse(self.user.check_password("Original!UniquePass492"))
        self.assert_unavailable_link(self.client.get(initial_path))

    def test_reset_completion_does_not_disclose_whether_an_account_exists(self):
        for email in (self.user.email, "notregistered@example.test"):
            with self.subTest(registered=email == self.user.email):
                response = self.client.post(
                    self.request_url, {"email": email}, follow=True
                )
                self.assertRedirects(
                    response, reverse("account_reset_password_done")
                )
                self.assertContains(
                    response, "If an account uses that email address"
                )
                self.assertNotContains(response, "We’ve sent a password reset")
                self.assertNotContains(response, email)
                self.assertNotContains(response, self.user.username)
                self.assertNotContains(response, "/password/reset/key/")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Original!UniquePass492"))

    @override_settings(ALLOWED_HOSTS=["petwell-u0cr.onrender.com"])
    def test_reset_email_uses_https_render_host_behind_trusted_proxy(self):
        response = self.client.post(
            self.request_url,
            {"email": self.user.email},
            HTTP_HOST="petwell-u0cr.onrender.com",
            HTTP_X_FORWARDED_PROTO="https",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        links = re.findall(r"https?://[^\s<>]+", mail.outbox[0].body)
        reset_link = next(
            link for link in links if "/password/reset/key/" in link
        )
        self.assertEqual(urlsplit(reset_link).scheme, "https")
        self.assertEqual(
            urlsplit(reset_link).netloc, "petwell-u0cr.onrender.com"
        )
        self.assertNotIn("set-password", reset_link)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertNotContains(response, reset_link, status_code=302)

    def test_password_reset_invalidates_other_authenticated_browser_session(
        self,
    ):
        other_browser = Client()
        other_browser.force_login(self.user)
        self.assertEqual(
            other_browser.get(reverse("pets:list")).status_code, 200
        )
        token = default_token_generator.make_token(self.user)
        self.assertEqual(
            self.client.get(self.reset_url(token)).status_code, 302
        )
        response = self.client.post(
            self.reset_url("set-password"),
            {
                "password1": "Changed!UniquePass825",
                "password2": "Changed!UniquePass825",
            },
        )
        self.assertRedirects(
            response, reverse("account_reset_password_from_key_done")
        )
        self.assertRedirects(
            other_browser.get(reverse("pets:list")),
            reverse("account_login") + "?next=" + reverse("pets:list"),
        )


class AccountSwitchLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = {}
        self.href = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.links[" ".join("".join(self.text).split())] = self.href
            self.href = None


class AccountRedirectTests(TestCase):
    def switch_link(self, response, text):
        links = AccountSwitchLinks()
        links.feed(response.content.decode())
        self.assertIn(text, links.links)
        return links.links[text]

    def test_login_signup_switch_preserves_internal_next_in_both_directions(
        self,
    ):
        destination = reverse("blog:create_post")
        response = self.client.get(
            reverse("account_login") + "?" + urlencode({"next": destination})
        )
        signup_link = self.switch_link(response, "Sign Up")
        self.assertEqual(urlsplit(signup_link).path, reverse("account_signup"))
        self.assertEqual(
            parse_qs(urlsplit(signup_link).query).get("next"), [destination]
        )
        response = self.client.get(signup_link)
        self.assertContains(response, f'name="next" value="{destination}"')
        login_link = self.switch_link(response, "Sign In")
        self.assertEqual(urlsplit(login_link).path, reverse("account_login"))
        self.assertEqual(
            parse_qs(urlsplit(login_link).query).get("next"), [destination]
        )

    def test_login_finishes_at_internal_next_destination(self):
        get_user_model().objects.create_user(
            "returnmember", password="Return!UniquePassword492"
        )
        destination = reverse("orders:history")
        response = self.client.post(
            reverse("account_login"),
            {
                "login": "returnmember",
                "password": "Return!UniquePassword492",
                "next": destination,
            },
        )
        self.assertRedirects(response, destination)

    def test_signup_finishes_at_internal_next_destination(self):
        destination = reverse("blog:create_post")
        response = self.client.post(
            reverse("account_signup"),
            {
                "username": "newreturnmember",
                "email": "newreturn@example.test",
                "password1": "Return!UniquePassword492",
                "password2": "Return!UniquePassword492",
                "next": destination,
            },
        )
        self.assertRedirects(response, destination)

    def test_external_next_never_turns_into_an_external_switch_or_redirect(
        self,
    ):
        get_user_model().objects.create_user(
            "safereturnmember", password="Safe!UniquePassword492"
        )
        unsafe = "https://untrusted.example.test/"
        cases = (
            (
                "account_login",
                "Sign Up",
                {
                    "login": "safereturnmember",
                    "password": "Safe!UniquePassword492",
                },
            ),
            (
                "account_signup",
                "Sign In",
                {
                    "username": "safesignupmember",
                    "email": "safesignup@example.test",
                    "password1": "Safe!UniquePassword492",
                    "password2": "Safe!UniquePassword492",
                },
            ),
        )
        for view, switch_text, fields in cases:
            with self.subTest(view=view):
                client = Client()
                url = reverse(view)
                response = client.get(url + "?" + urlencode({"next": unsafe}))
                switch = self.switch_link(response, switch_text)
                self.assertFalse(urlsplit(switch).netloc)
                self.assertFalse(urlsplit(switch).scheme)
                response = client.post(url, {**fields, "next": unsafe})
                self.assertRedirects(response, reverse("home"))
