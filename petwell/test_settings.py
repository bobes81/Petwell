"""Isolated, offline automated tests. Never connects to configured production services."""

from .settings import *

SECRET_KEY = "offline-test-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}
STRIPE_SECRET_KEY = "sk_test_offline"
STRIPE_WEBHOOK_SECRET = "whsec_offline"
STRIPE_LIVE_MODE = False

# Public cloud name only, for deterministic URL rendering; no upload credentials.
cloudinary.config(cloud_name="offline-test", api_key=None, api_secret=None)
