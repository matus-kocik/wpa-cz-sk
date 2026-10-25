from pathlib import Path

from decouple import Config, RepositoryEnv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

config = Config(RepositoryEnv(BASE_DIR.parent / ".env"))

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
USE_MINIFIED_JS = not DEBUG

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="", cast=lambda v: [h.strip() for h in v.split(",") if h]
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [h.strip() for h in v.split(",") if h],
)
if DEBUG:
    ALLOWED_HOSTS += ["127.0.0.1", "localhost"]
ADMIN_URL = config("ADMIN_URL", default="admin/")
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Local apps
    "users",
    "common",
    "core",
    "members",
    "profiles.apps.ProfilesConfig",
    "articles",
    "taxonomy",
    "breeding",
    "studbook",
    "projects",
    "events",
    "dashboard",
    # Third-party apps
    "django_countries",
]

if DEBUG:
    INSTALLED_APPS += ["django_extensions"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Custom User Model
AUTH_USER_MODEL = "users.CustomUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"

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
                "core.context_processors.turnstile_site_key",
                "core.context_processors.frontend_flags",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DB_ENGINE = config(
    "DB_ENGINE",
    default="django.db.backends.sqlite3" if DEBUG else "django.db.backends.postgresql",
)

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR.parent / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
        }
    }

email_host_user = config("EMAIL_HOST_USER", default="")

MAILERS = {
    "default": {
        "BACKEND": config(
            "EMAIL_BACKEND",
            default="django.core.mail.backends.smtp.EmailBackend",
        ),
        "OPTIONS": {
            "host": config("EMAIL_HOST", default=""),
            "port": config("EMAIL_PORT", cast=int, default=587),
            "username": email_host_user,
            "password": config("EMAIL_HOST_PASSWORD", default=""),
            "use_tls": config("EMAIL_USE_TLS", cast=bool, default=True),
            "use_ssl": config("EMAIL_USE_SSL", cast=bool, default=False),
        },
    },
}

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=email_host_user,
)

CONTACT_RECEIVER_EMAIL = config(
    "CONTACT_RECEIVER_EMAIL",
    default=email_host_user,
)

APPLICATION_RECEIVER_EMAIL = config(
    "APPLICATION_RECEIVER_EMAIL",
    default=CONTACT_RECEIVER_EMAIL,
)

# Site URL for building absolute links (e.g. password reset)
SITE_URL = config("SITE_URL", default="http://127.0.0.1:8000")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "cs"

TIME_ZONE = "Europe/Prague"

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Cloudflare Turnstile
TURNSTILE_SITE_KEY = config("TURNSTILE_SITE_KEY", default="")
TURNSTILE_SECRET_KEY = config("TURNSTILE_SECRET_KEY", default="")

# Security headers

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_DOMAIN = None

SESSION_ENGINE = "django.contrib.sessions.backends.db"

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Auth redirects

LOGIN_REDIRECT_URL = "dashboard_home"
LOGOUT_REDIRECT_URL = "home"
