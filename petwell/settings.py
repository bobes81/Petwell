import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-with-a-random-key')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']


# ------------------------------
# Database configuration (Heroku PostgreSQL)
# ------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}


# ------------------------------
# Static & Media files
# ------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ------------------------------
# Email settings (SendGrid)
# ------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ivan.kimpl@email.cz'
