from pathlib import Path

# Import base settings and override DATABASES for faster, isolated tests.
from config import settings as base_settings


# Minimal adjustments for tests
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = base_settings.SECRET_KEY
DEBUG = True

INSTALLED_APPS = base_settings.INSTALLED_APPS
MIDDLEWARE = base_settings.MIDDLEWARE

ROOT_URLCONF = base_settings.ROOT_URLCONF
TEMPLATES = base_settings.TEMPLATES

# Use in-memory SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = getattr(
    base_settings, "DEFAULT_AUTO_FIELD", "django.db.models.BigAutoField"
)

LOGIN_REDIRECT_URL = base_settings.LOGIN_REDIRECT_URL
LOGOUT_REDIRECT_URL = base_settings.LOGOUT_REDIRECT_URL
LOGIN_URL = base_settings.LOGIN_URL
