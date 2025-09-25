import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from django.utils.log import DEFAULT_LOGGING

# Načítaj .env zo základného adresára (dva úrovne hore nad settings.py)
BASE_DIR = Path(__file__).resolve().parent.parent
# Uisti sa, že load_dotenv hľadá .env v BASE_DIR
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

def get_env(name: str, default=None, required: bool = False):
    """Získa hodnotu z prostredia, alebo vyvolá výnimku ak required."""
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise ImproperlyConfigured(f"Environment variable {name} is required but not set.")
    return val

# ------- Základné nastavenia -------

# Pre vývoj: fallback, ak nie je definovaný v prostredí, aby si mohol spustiť server
_secret = get_env("DJANGO_SECRET_KEY", None)
if not _secret:
    # upozorni, že bežíš v nebezpečnom móde
    # v produkcii by si toto mal zakázať / odstrániť
    import warnings
    warnings.warn("DJANGO_SECRET_KEY not found. Using fallback insecure secret key.")
    SECRET_KEY = "insecure-dev-key-fallback-1234567890"
else:
    SECRET_KEY = _secret

DEBUG = get_env("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", "").split(",")

# ------- Aplikácie, middleware, šablóny -------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "tasks",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "tasker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tasker.wsgi.application"

# ------- Databáza -------

import dj_database_url
DATABASES = {
    "default": dj_database_url.config(default=get_env("DATABASE_URL", "sqlite:///db.sqlite3"))
}

# ------- Heslovanie, validátory, medzinárodné -------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------- Statické / mediá súbory -------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------- Bezpečnostné nastavenia pre produkciu -------

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"

# ------- Logging -------

LOGGING = DEFAULT_LOGGING




AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth nastavení
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Pro jednoduchost
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_USERNAME_REQUIRED = True

# Default auto field (opraví warning)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'