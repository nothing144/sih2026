"""
Django settings for config project.

Production-ready configuration:
- All secrets/credentials come from environment variables (see .env.example).
- DEBUG defaults to False.
- Static files served by WhiteNoise (collectstatic -> staticfiles/).
- Database points to Supabase PostgreSQL via environment variables.
"""

import os
from pathlib import Path

import dotenv

# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if present (gitignored). Never commit real secrets.
dotenv.load_dotenv(BASE_DIR / ".env")

# ============================================================
# HELPERS
# ============================================================


def _env(name, default=None):
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


def _env_bool(name, default="False"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes", "on")


def _env_list(name):
    raw = os.environ.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


# ============================================================
# SECURITY
# ============================================================

DEBUG = _env_bool("DEBUG", "False")

SECRET_KEY = _env("SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        # Development-only fallback so a missing .env does not block local work.
        SECRET_KEY = "django-insecure-dev-only-key-do-not-use-in-production"
    else:
        raise RuntimeError(
            "SECRET_KEY is required in production. Set it as an environment variable."
        )

ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [

    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "corsheaders",
    "whitenoise.runserver_nostatic",

    # Our apps
    "users",
    "batteries",
    "analysis",
    "passport",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    # Allows React frontend to communicate with Django backend
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise serves collectstatic output directly from Django
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================================
# HTTPS / SECURITY HEADERS (production only)
# ============================================================

SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", "False")
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", str(not DEBUG))
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", str(not DEBUG))
SECURE_HSTS_SECONDS = int(_env("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if _env_bool("USE_PROXY_SSL_HEADER", "False") else None

# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# DATABASE - SUPABASE POSTGRESQL
# Credentials come from environment variables (.env locally,
# platform env vars in production). Never committed to source.
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",

        "NAME": _env("DB_NAME", "postgres"),

        "USER": _env("DB_USER", "postgres"),

        "PASSWORD": _env("DB_PASSWORD", ""),

        "HOST": _env("DB_HOST", "localhost"),

        "PORT": _env("DB_PORT", "5432"),

        # Supabase requires SSL connections.
        "OPTIONS": {} if _env_bool("DB_DISABLE_SSL", "True" if DEBUG else "False") else {"sslmode": "require"},

        "CONN_MAX_AGE": int(_env("DB_CONN_MAX_AGE", "60")),
    }
}


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "users.User"


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = _env("TIME_ZONE", "Asia/Kolkata")

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES (WhiteNoise)
# collectstatic gathers everything into staticfiles/.
# ============================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# MEDIA FILES
# BMS CSV uploads are stored on disk under media/.
# NOTE: for multi-instance production deployments, move this to
# object storage (e.g. Supabase Storage/S3); single-instance
# deployments serve it from the same host (see config/urls.py).
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {

    # JWT authentication
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    # By default, API requires login
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(_env("JWT_ACCESS_MINUTES", "1440"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(_env("JWT_REFRESH_DAYS", "7"))),
}

# ============================================================
# CORS / CSRF
# Comma-separated frontend origins, e.g.
# CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
# ============================================================

CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS")

CORS_ALLOW_ALL_ORIGINS = _env_bool("CORS_ALLOW_ALL_ORIGINS", "True" if DEBUG else "False")

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS")


# ============================================================
# EMAIL
# Console backend by default; override via env for production SMTP.
# ============================================================

EMAIL_BACKEND = _env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
