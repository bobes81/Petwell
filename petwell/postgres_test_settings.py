"""CI-only PostgreSQL tests; never use these settings to serve the site."""

import os

import dj_database_url

from .test_settings import *  # noqa: F403

# A separate explicit variable prevents using a production DATABASE_URL.
DATABASES = {
    "default": dj_database_url.parse(os.environ["TEST_DATABASE_URL"]),
}
