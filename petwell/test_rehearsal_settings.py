"""Offline startup probes; never connects to or resets a restored database."""

import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


PROBE = """
import json
import socket

def refuse_network(*args, **kwargs):
    raise AssertionError("Rehearsal configuration probes must stay offline.")

socket.socket.connect = refuse_network

try:
    import django
    django.setup()
except Exception as exc:
    print(json.dumps({"error": type(exc).__name__, "message": str(exc)}))
else:
    import cloudinary
    from django.conf import settings
    from cloudinary_storage import app_settings
    db = settings.DATABASES["default"]
    print(json.dumps({
        "host": db["HOST"], "name": db["NAME"],
        "ssl_forced": db.get("OPTIONS", {}).get("sslmode") == "require",
        "local_secret": settings.SECRET_KEY.startswith("local-fixture-"),
        "hosts": settings.ALLOWED_HOSTS, "site": settings.SITE_URL,
        "debug": settings.DEBUG, "redirect": settings.SECURE_SSL_REDIRECT,
        "secure_cookie": settings.SESSION_COOKIE_SECURE,
        "stripe_disabled": not settings.STRIPE_SECRET_KEY
            and not settings.STRIPE_WEBHOOK_SECRET and not settings.STRIPE_LIVE_MODE,
        "email_backend": settings.EMAIL_BACKEND,
        "smtp_disabled": not settings.EMAIL_HOST_PASSWORD,
        "cloudinary_disabled": not cloudinary.config().cloud_name
            and not cloudinary.config().api_key and not cloudinary.config().api_secret,
        "storage_disabled": not app_settings.user_settings["API_SECRET"],
    }))
"""


class RehearsalSettingsTests(SimpleTestCase):
    def probe(self, variables=None):
        # Whitelist process infrastructure; never inherit service credentials.
        environment = {
            key: value for key, value in os.environ.items()
            if key in {
                "PATH", "SYSTEMROOT", "LANG", "LC_ALL", "TMPDIR",
                "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH",
            }
        }
        environment.update(
            DJANGO_SETTINGS_MODULE="petwell.rehearsal_settings",
            REHEARSAL_SECRET_KEY="local-fixture-" + "x" * 60,
        )
        environment.update(variables or {})
        result = subprocess.run(
            [sys.executable, "-c", PROBE], cwd=settings.BASE_DIR,
            env=environment, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, "Offline startup probe failed.")
        return json.loads(result.stdout)

    def test_missing_local_url_never_falls_back_to_production_database(self):
        result = self.probe({
            "DATABASE_URL": "postgres://fixture:fixture@remote.invalid/production",
        })
        self.assertEqual(result["error"], "ImproperlyConfigured")
        self.assertIn("never used as a fallback", result["message"])
        self.assertNotIn("remote.invalid", result["message"])

    def test_local_restored_copy_does_not_force_ssl_or_inherit_providers(self):
        result = self.probe({
            "REHEARSAL_DATABASE_URL": (
                "postgresql://fixture:fixture@127.0.0.1:5432/isolated_restore"
            ),
            "DATABASE_URL": "postgres://fixture:fixture@remote.invalid/production",
            "SECRET_KEY": "production-fixture-do-not-reuse",
            "STRIPE_SECRET_KEY": "sk_live_fixture_never_used",
            "STRIPE_WEBHOOK_SECRET": "whsec_fixture_never_used",
            "STRIPE_LIVE_MODE": "True",
            "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "EMAIL_HOST": "smtp.gmail.com",
            "EMAIL_HOST_USER": "petwell.shop.uk@gmail.com",
            "EMAIL_HOST_PASSWORD": "fixture-gmail-password-never-used",
            "SENDGRID_API_KEY": "fixture-only",
            "CLOUDINARY_URL": "cloudinary://fixture:fixture@inherited-cloud",
        })
        self.assertNotIn("error", result)
        self.assertEqual(result["host"], "127.0.0.1")
        self.assertEqual(result["name"], "isolated_restore")
        self.assertFalse(result["ssl_forced"])
        for key in (
            "local_secret", "stripe_disabled", "smtp_disabled",
            "cloudinary_disabled", "storage_disabled",
        ):
            self.assertTrue(result[key], key)
        self.assertEqual(
            result["email_backend"], "django.core.mail.backends.dummy.EmailBackend"
        )
        self.assertEqual(result["site"], "http://127.0.0.1:8000")
        self.assertNotIn("petwell-u0cr.onrender.com", result["hosts"])
        self.assertFalse(result["debug"])
        self.assertFalse(result["redirect"])
        self.assertFalse(result["secure_cookie"])

    def test_remote_non_postgres_and_maintenance_targets_are_rejected(self):
        for url in (
            "postgres://fixture:private-password@remote.invalid/restore",
            "sqlite:///restored.sqlite3",
            "postgres://fixture:fixture@127.0.0.1/postgres",
            "postgres://fixture:fixture@127.0.0.1/template1",
            "postgres://fixture:fixture@127.0.0.1/",
        ):
            with self.subTest(target=url.split(":")[0]):
                result = self.probe({"REHEARSAL_DATABASE_URL": url})
                self.assertEqual(result["error"], "ImproperlyConfigured")
                self.assertNotIn("private-password", result["message"])
                self.assertNotIn(url, result["message"])

    def test_query_or_libpq_routing_overrides_are_rejected(self):
        base = "postgres://fixture:fixture@localhost/isolated_restore"
        for variables in (
            {"REHEARSAL_DATABASE_URL": base + "?hostaddr=203.0.113.1"},
            {"REHEARSAL_DATABASE_URL": base + "#fragment"},
            {"REHEARSAL_DATABASE_URL": base, "PGHOSTADDR": "203.0.113.1"},
            {"REHEARSAL_DATABASE_URL": base, "PGSERVICE": "remote-service"},
        ):
            result = self.probe(variables)
            self.assertEqual(result["error"], "ImproperlyConfigured")

    def test_rehearsal_secret_is_required_instead_of_production_secret(self):
        result = self.probe({
            "REHEARSAL_DATABASE_URL": "postgres://localhost/isolated_restore",
            "REHEARSAL_SECRET_KEY": "",
            "SECRET_KEY": "production-fixture-" + "x" * 60,
        })
        self.assertEqual(result["error"], "ImproperlyConfigured")
        self.assertIn("REHEARSAL_SECRET_KEY", result["message"])
        self.assertNotIn("production-fixture", result["message"])

    def test_ipv6_loopback_is_supported_without_connecting(self):
        result = self.probe({
            "REHEARSAL_DATABASE_URL": "postgres://[::1]:5432/isolated_restore",
        })
        self.assertNotIn("error", result)
        self.assertEqual(result["host"], "::1")
