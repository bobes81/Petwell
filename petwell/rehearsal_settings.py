"""Local restored-copy rehearsal only. Never use this module on Render."""

import os
from urllib.parse import unquote, urlsplit

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def _local_database():
    url = os.environ.get("REHEARSAL_DATABASE_URL", "")
    try:
        parsed = urlsplit(url)
        name = unquote(parsed.path.removeprefix("/"))
        valid = (
            parsed.scheme in {"postgres", "postgresql"}
            and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
            and bool(name)
            and name not in {"postgres", "template0", "template1"}
            and not parsed.query
            and not parsed.fragment
            and (parsed.port is None or 1 <= parsed.port <= 65535)
        )
        if not valid:
            raise ValueError
        # Refuse libpq routing overrides instead of silently changing the
        # owner's shell environment or accepting a possible remote target.
        if any(os.environ.get(key) for key in (
            "PGHOSTADDR", "PGSERVICE", "PGSERVICEFILE",
        )):
            raise ValueError
        return dj_database_url.parse(url, conn_max_age=0, ssl_require=False)
    except (ValueError, TypeError):
        # Never include the credential-bearing URL or nested parser exception.
        raise ImproperlyConfigured(
            "Set REHEARSAL_DATABASE_URL to a dedicated restored PostgreSQL "
            "database on localhost/127.0.0.1/[::1], without query/fragment "
            "or PGHOSTADDR/PGSERVICE/PGSERVICEFILE overrides. "
            "DATABASE_URL is never used as a fallback."
        ) from None


_database = _local_database()
_secret = os.environ.get("REHEARSAL_SECRET_KEY", "")
if len(_secret) < 50:
    raise ImproperlyConfigured(
        "Set a new private REHEARSAL_SECRET_KEY of at least 50 characters; "
        "do not reuse the production secret."
    )

from .settings import *  # noqa: E402,F403

DATABASES = {"default": _database}
SECRET_KEY = _secret
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
SITE_URL = "http://127.0.0.1:8000"
CSRF_TRUSTED_ORIGINS = [SITE_URL, "http://localhost:8000", "http://[::1]:8000"]
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Rehearse data/forms only. Provider acceptance uses separately approved
# sandbox/deployment configuration, never a production binding inherited here.
STRIPE_SECRET_KEY = ""
STRIPE_WEBHOOK_SECRET = ""
STRIPE_LIVE_MODE = False
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "PetWell <noreply@example.test>"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": None, "API_KEY": None, "API_SECRET": None, "SECURE": True,
}
cloudinary.config(cloud_name=None, api_key=None, api_secret=None, secure=True)  # noqa: F405
MEDIA_URL = "/media/"
