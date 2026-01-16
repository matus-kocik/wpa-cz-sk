from django.conf import settings


def turnstile_site_key(request):
    return {
        "TURNSTILE_SITE_KEY": settings.TURNSTILE_SITE_KEY
    }
