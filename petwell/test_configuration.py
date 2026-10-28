"""Fresh-process configuration regressions using synthetic credentials only."""

import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


STARTUP_PROBE = """
import json
import os
import socket

def refuse_network(*args, **kwargs):
    raise AssertionError("Configuration tests must stay offline.")

socket.socket.connect = refuse_network

import django
django.setup()

import cloudinary
from django.conf import settings
from cloudinary_storage import app_settings

config = cloudinary.config()
print(json.dumps({
    "cloud_name": config.cloud_name,
    "credentials_match": (
        config.api_key == os.environ.get("EXPECTED_CLOUDINARY_KEY")
        and config.api_secret == os.environ.get("EXPECTED_CLOUDINARY_SECRET")
    ),
    "storage_matches_sdk": (
        app_settings.user_settings["CLOUD_NAME"] == config.cloud_name
        and app_settings.user_settings["API_KEY"] == config.api_key
        and app_settings.user_settings["API_SECRET"] == config.api_secret
    ),
    "secure": config.secure is True,
    "media_url": settings.MEDIA_URL,
    "image_url": cloudinary.CloudinaryImage("fixture.png").build_url()
        if config.cloud_name else None,
    "database_engine": settings.DATABASES["default"]["ENGINE"],
    "database_ssl": settings.DATABASES["default"].get("OPTIONS", {}).get("sslmode"),
    "debug": settings.DEBUG,
    "site_url": settings.SITE_URL,
    "render_host_allowed": "petwell-u0cr.onrender.com" in settings.ALLOWED_HOSTS,
    "stripe_disabled": (
        not settings.STRIPE_SECRET_KEY and not settings.STRIPE_WEBHOOK_SECRET
    ),
    "stripe_live_mode": settings.STRIPE_LIVE_MODE,
    "email_backend": settings.EMAIL_BACKEND,
    "email_host": settings.EMAIL_HOST,
    "email_port": settings.EMAIL_PORT,
    "email_tls": settings.EMAIL_USE_TLS,
    "email_user": settings.EMAIL_HOST_USER,
    "email_timeout": settings.EMAIL_TIMEOUT,
    "email_password_matches": (
        settings.EMAIL_HOST_PASSWORD == os.environ.get("SENDGRID_API_KEY")
    ),
    "from_email": settings.DEFAULT_FROM_EMAIL,
}))
"""


class ProductionConfigurationTests(SimpleTestCase):
    def configuration(self, variables=None, credentials=None):
        # Never inherit real service credentials or a production database.
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(
                ("CLOUDINARY_", "STRIPE_", "EMAIL_", "EXPECTED_CLOUDINARY_")
            )
            and key not in {
                "DATABASE_URL",
                "SENDGRID_API_KEY",
                "DEFAULT_FROM_EMAIL",
                "ALLOWED_HOSTS",
                "SITE_URL",
                "SECRET_KEY",
            }
        }
        environment.update(
            DJANGO_SETTINGS_MODULE="petwell.settings",
            DEBUG="False",
            SECRET_KEY="synthetic-configuration-test-key-never-for-deployment",
        )
        environment.update(variables or {})
        if credentials:
            environment["EXPECTED_CLOUDINARY_KEY"] = credentials[0]
            environment["EXPECTED_CLOUDINARY_SECRET"] = credentials[1]
        process = subprocess.run(
            [sys.executable, "-c", STARTUP_PROBE],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
        # Keep stderr/environment out of assertion output even on startup errors.
        self.assertEqual(process.returncode, 0, "Offline startup probe failed.")
        return json.loads(process.stdout)

    def test_existing_render_url_only_configuration_survives_storage_import(self):
        config = self.configuration(
            {
                "CLOUDINARY_URL": (
                    "cloudinary://fixture-key:fixture-secret@url-fixture-cloud"
                ),
                "DATABASE_URL": (
                    "postgres://fixture:fixture@localhost:5432/offline_fixture"
                ),
            },
            credentials=("fixture-key", "fixture-secret"),
        )
        self.assertEqual(config["cloud_name"], "url-fixture-cloud")
        self.assertTrue(config["credentials_match"])
        self.assertTrue(config["storage_matches_sdk"])
        self.assertEqual(
            config["media_url"],
            "https://res.cloudinary.com/url-fixture-cloud/image/upload/",
        )
        self.assertTrue(config["secure"])
        self.assertTrue(config["image_url"].startswith("https://"))
        self.assertNotIn("fixture-secret", config["image_url"])
        self.assertNotIn("fixture-key", config["image_url"])
        self.assertEqual(config["database_engine"], "django.db.backends.postgresql")
        self.assertEqual(config["database_ssl"], "require")
        self.assertFalse(config["debug"])
        self.assertTrue(config["render_host_allowed"])
        self.assertEqual(config["site_url"], "https://petwell-u0cr.onrender.com")

    def test_separate_cloudinary_variables_remain_supported(self):
        config = self.configuration(
            {
                "CLOUDINARY_CLOUD_NAME": "separate-fixture-cloud",
                "CLOUDINARY_API_KEY": "separate-fixture-key",
                "CLOUDINARY_API_SECRET": "separate-fixture-secret",
            },
            credentials=("separate-fixture-key", "separate-fixture-secret"),
        )
        self.assertEqual(config["cloud_name"], "separate-fixture-cloud")
        self.assertTrue(config["credentials_match"])
        self.assertTrue(config["storage_matches_sdk"])

    def test_mixed_sources_follow_sdk_separate_variable_precedence(self):
        config = self.configuration(
            {
                "CLOUDINARY_URL": "cloudinary://url-key:url-secret@url-cloud",
                "CLOUDINARY_CLOUD_NAME": "separate-fixture-cloud",
                "CLOUDINARY_API_KEY": "separate-fixture-key",
                "CLOUDINARY_API_SECRET": "separate-fixture-secret",
            },
            credentials=("separate-fixture-key", "separate-fixture-secret"),
        )
        self.assertEqual(config["cloud_name"], "separate-fixture-cloud")
        self.assertTrue(config["credentials_match"])
        self.assertTrue(config["storage_matches_sdk"])

    def test_url_query_cannot_disable_https_images(self):
        config = self.configuration(
            {
                "CLOUDINARY_URL": (
                    "cloudinary://fixture-key:fixture-secret@url-fixture-cloud"
                    "?secure=false"
                ),
            },
            credentials=("fixture-key", "fixture-secret"),
        )
        self.assertEqual(config["cloud_name"], "url-fixture-cloud")
        self.assertTrue(config["secure"])
        self.assertTrue(config["image_url"].startswith("https://"))

    def test_missing_optional_services_keep_startup_and_safe_defaults(self):
        config = self.configuration()
        self.assertIsNone(config["cloud_name"])
        self.assertTrue(config["credentials_match"])
        self.assertTrue(config["storage_matches_sdk"])
        self.assertIsNone(config["image_url"])
        self.assertEqual(config["media_url"], "/media/")
        self.assertTrue(config["stripe_disabled"])
        self.assertFalse(config["stripe_live_mode"])
        self.assertEqual(
            config["email_backend"], "django.core.mail.backends.console.EmailBackend"
        )

    def test_explicit_sendgrid_settings_use_tls_without_sending(self):
        config = self.configuration(
            {
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "SENDGRID_API_KEY": "synthetic-smtp-fixture-only",
                "DEFAULT_FROM_EMAIL": "PetWell <sender@example.test>",
            }
        )
        self.assertEqual(
            config["email_backend"], "django.core.mail.backends.smtp.EmailBackend"
        )
        self.assertEqual(config["email_host"], "smtp.sendgrid.net")
        self.assertEqual(config["email_port"], 587)
        self.assertTrue(config["email_tls"])
        self.assertEqual(config["email_user"], "apikey")
        self.assertEqual(config["email_timeout"], 10)
        self.assertTrue(config["email_password_matches"])
        self.assertEqual(config["from_email"], "PetWell <sender@example.test>")
