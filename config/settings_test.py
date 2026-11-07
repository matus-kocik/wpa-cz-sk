from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    },
}

# Django 6.0 uses the legacy backend; tests must never use real SMTP.
if DJANGO_VERSION < (6, 1):  # noqa: F405
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
