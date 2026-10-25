import os
from pathlib import Path

from decouple import config
import dj_database_url


# ============================================================
# BASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# ENVIRONMENT
# ============================================================

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-local-development-only",
)

DEBUG = config(
    "DEBUG",
    default=True,
    cast=bool,
)


# ============================================================
# HOSTS
# ============================================================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

RENDER_EXTERNAL_HOSTNAME = config(
    "RENDER_EXTERNAL_HOSTNAME",
    default="",
)

CUSTOM_DOMAIN = config(
    "CUSTOM_DOMAIN",
    default="",
)

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

if CUSTOM_DOMAIN:
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = []

RENDER_EXTERNAL_URL = config(
    "RENDER_EXTERNAL_URL",
    default="",
)

if RENDER_EXTERNAL_URL:
    CSRF_TRUSTED_ORIGINS.append(
        RENDER_EXTERNAL_URL.rstrip("/")
    )

if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{CUSTOM_DOMAIN}"
    )


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # ArtistHub
    "core.apps.CoreConfig",

    # Supabase / S3-compatible storage
    "storages",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Static files
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI / ASGI
# ============================================================

ROOT_URLCONF = "artisthub.urls"

WSGI_APPLICATION = "artisthub.wsgi.application"

ASGI_APPLICATION = "artisthub.asgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

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
# DATABASE
#
# LOCAL:
#     SQLite
#
# RENDER:
#     Neon PostgreSQL through DATABASE_URL
# ============================================================


DATABASE_URL = config(
    "DATABASE_URL",
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=0,
        conn_health_checks=True,
        ssl_require=DATABASE_URL.startswith(
            (
                "postgres://",
                "postgresql://",
            )
        ),
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Harare"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
#
# Static files remain on Render and are handled by WhiteNoise.
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# SUPABASE STORAGE CONFIGURATION
# ============================================================

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default="")

# Check whether Supabase storage has been configured.
SUPABASE_STORAGE_ENABLED = all([
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_ENDPOINT_URL,
])

# ============================================================
# STORAGE BACKENDS
# ============================================================


if SUPABASE_STORAGE_ENABLED:
    # --------------------------------------------------------
    # PRODUCTION / SUPABASE STORAGE
    # --------------------------------------------------------

    STORAGES = {
        "default": {
            "BACKEND": "core.storage_backends.SupabasePublicMediaStorage",
            "OPTIONS": {
                "access_key": AWS_ACCESS_KEY_ID,
                "secret_key": AWS_SECRET_ACCESS_KEY,
                "bucket_name": AWS_STORAGE_BUCKET_NAME,
                "region_name": AWS_S3_REGION_NAME,
                "endpoint_url": AWS_S3_ENDPOINT_URL,
                "addressing_style": "path",
                "signature_version": "s3v4",
                "querystring_auth": False,
               
            },
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }

else:
    # --------------------------------------------------------
    # LOCAL DEVELOPMENT STORAGE
    # --------------------------------------------------------

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }


    # --------------------------------------------------------
    # LOCAL DEVELOPMENT
    # --------------------------------------------------------

    STORAGES = {
        "default": {
            "BACKEND": (
                "django.core.files.storage."
                "FileSystemStorage"
            ),
        },

        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }


# ============================================================
# LOCAL MEDIA CONFIGURATION
#
# This is used only when Supabase credentials are NOT present.
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DJANGO DEFAULTS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# AUTHENTICATION REDIRECTS
# ============================================================

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "feed"

LOGOUT_REDIRECT_URL = "feed"


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True


# ============================================================
# SUPABASE URL SETTINGS
#
# These are optional but useful if the application needs
# the public Supabase bucket URL.
# ============================================================

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "",
)

SUPABASE_BUCKET = AWS_STORAGE_BUCKET_NAME or ""


# ============================================================
# OPTIONAL S3 SETTINGS
# ============================================================

AWS_QUERYSTRING_AUTH = False

AWS_DEFAULT_ACL = None

AWS_S3_FILE_OVERWRITE = False

AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_S3_ADDRESSING_STYLE = "path"
