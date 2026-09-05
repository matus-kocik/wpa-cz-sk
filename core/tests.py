from datetime import date, timedelta
from unittest.mock import Mock, patch

import dns.resolver
import pytest
import requests
from django.core.exceptions import ValidationError
from django.urls import reverse

from core.context_processors import frontend_flags, turnstile_site_key
from core.forms import TurnstileField
from core.sitemaps import CoreViewSitemap
from core.validators import (
    validate_academic_title,
    validate_birth_date,
    validate_email_domain,
    validate_house_number,
    validate_human_name,
    validate_location_name,
    validate_message_body,
    validate_notes,
    validate_phone_number,
    validate_plain_text,
    validate_postal_code,
    validate_street,
    validate_subject,
)


def test_turnstile_accepts_successful_response():
    field = TurnstileField(required=True)

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"success": True}

    with patch("core.forms.requests.post", return_value=response):
        field.validate("valid-token")


def test_turnstile_rejects_invalid_token():
    field = TurnstileField(required=True)

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"success": False}

    with patch("core.forms.requests.post", return_value=response):
        with pytest.raises(
            ValidationError,
            match="Ověření proti spamu selhalo.",
        ):
            field.validate("invalid-token")


def test_turnstile_handles_network_error():
    field = TurnstileField(required=True)

    with patch(
        "core.forms.requests.post",
        side_effect=requests.RequestException("Network error"),
    ):
        with pytest.raises(
            ValidationError,
            match="Ověření proti spamu se nepodařilo.",
        ):
            field.validate("token")


def test_turnstile_handles_invalid_json():
    field = TurnstileField(required=True)

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("Invalid JSON")

    with patch("core.forms.requests.post", return_value=response):
        with pytest.raises(
            ValidationError,
            match="Ověření proti spamu se nepodařilo.",
        ):
            field.validate("token")


def test_turnstile_requires_value():
    field = TurnstileField(required=True)

    with pytest.raises(ValidationError):
        field.validate("")


@pytest.mark.parametrize(
    "value",
    [
        "Bc.",
        "Ing.",
        "Mgr.",
        "MUDr.",
        "PhDr.",
        "RNDr.",
        "JUDr.",
        "Ph.D.",
        "doc. Ing.",
    ],
)
def test_academic_title_accepts_valid_titles(value):
    validate_academic_title(value)


@pytest.mark.parametrize(
    "value",
    [
        "Mgr_123",
        "Ing.<script>",
        "PhDr/@",
    ],
)
def test_academic_title_rejects_invalid_titles(value):
    with pytest.raises(ValidationError):
        validate_academic_title(value)


@pytest.mark.parametrize(
    "value",
    [
        "Jan",
        "Ján",
        "Ľuboš",
        "O'Connor",
        "Anna-Mária",
    ],
)
def test_human_name_accepts_valid_values(value):
    validate_human_name(value)


@pytest.mark.parametrize(
    "value",
    [
        "A",
        "Jan123",
        "Jan<script>",
        "",
    ],
)
def test_human_name_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_human_name(value)


def test_email_domain_skips_validation_in_debug(settings):
    settings.DEBUG = True
    validate_email_domain("user@invalid.invalid")


def test_email_domain_allows_allowlisted_domain(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setattr(
        "core.validators.ALLOWED_DOMAINS",
        {"example.com"},
    )

    validate_email_domain("user@example.com")


def test_email_domain_rejects_blocked_domain(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setattr(
        "core.validators.BLOCKED_DOMAINS",
        {"blocked.example"},
    )

    with pytest.raises(ValidationError):
        validate_email_domain("user@blocked.example")


def test_email_domain_accepts_valid_mx(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setattr(
        "core.validators.ALLOWED_DOMAINS",
        set(),
    )
    monkeypatch.setattr(
        "core.validators.BLOCKED_DOMAINS",
        set(),
    )

    with patch("core.validators.dns.resolver.resolve") as resolve:
        resolve.return_value = Mock()
        validate_email_domain("user@example.com")


@pytest.mark.parametrize(
    ("exception", "message"),
    [
        (
            dns.resolver.NXDOMAIN(),
            "Doména e-mailu neexistuje.",
        ),
        (
            dns.resolver.NoAnswer(),
            "Doména e-mailu nemá platný MX záznam.",
        ),
        (
            dns.resolver.NoNameservers(),
            "Doména e-mailu nemá DNS záznamy.",
        ),
    ],
)
def test_email_domain_rejects_dns_errors(
    settings,
    monkeypatch,
    exception,
    message,
):
    settings.DEBUG = False
    monkeypatch.setattr(
        "core.validators.ALLOWED_DOMAINS",
        set(),
    )
    monkeypatch.setattr(
        "core.validators.BLOCKED_DOMAINS",
        set(),
    )

    with patch(
        "core.validators.dns.resolver.resolve",
        side_effect=exception,
    ):
        with pytest.raises(ValidationError, match=message):
            validate_email_domain("user@example.com")


def test_email_domain_handles_unknown_dns_error(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setattr(
        "core.validators.ALLOWED_DOMAINS",
        set(),
    )
    monkeypatch.setattr(
        "core.validators.BLOCKED_DOMAINS",
        set(),
    )

    with patch(
        "core.validators.dns.resolver.resolve",
        side_effect=RuntimeError("DNS failure"),
    ):
        with pytest.raises(
            ValidationError,
            match="Nelze ověřit e-mailovou doménu.",
        ):
            validate_email_domain("user@example.com")


@pytest.mark.parametrize(
    "value",
    [
        "Dotaz",
        "Členství WPA",
        "Ahoj světe",
    ],
)
def test_subject_accepts_valid_values(value):
    validate_subject(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ab",
        "12345",
        "---",
    ],
)
def test_subject_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_subject(value)


@pytest.mark.parametrize(
    "value",
    [
        "Toto je normální zpráva.",
        "Dobrý den, mám dotaz.",
    ],
)
def test_message_body_accepts_valid_values(value):
    validate_message_body(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "krátké",
        "1234567890",
    ],
)
def test_message_body_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_message_body(value)


def test_birth_date_accepts_adult():
    validate_birth_date(date(1990, 1, 1))


def test_birth_date_rejects_future_date():
    with pytest.raises(ValidationError):
        validate_birth_date(date.today() + timedelta(days=1))


def test_birth_date_rejects_too_old_date():
    with pytest.raises(ValidationError):
        validate_birth_date(date(1899, 12, 31))


def test_birth_date_rejects_under_18():
    today = date.today()
    under_18 = date(
        today.year - 17,
        today.month,
        min(today.day, 28),
    )

    with pytest.raises(ValidationError):
        validate_birth_date(under_18)


@pytest.mark.parametrize(
    "value",
    [
        "+420777123456",
        "+421901123456",
    ],
)
def test_phone_number_accepts_valid_values(value):
    validate_phone_number(value)


def test_phone_number_allows_empty_value():
    validate_phone_number("")


@pytest.mark.parametrize(
    "value",
    [
        "123",
        "abc",
        "+420",
    ],
)
def test_phone_number_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_phone_number(value)


@pytest.mark.parametrize(
    "value",
    [
        "Hlavní",
        "Masarykova 12",
        "J. A. Komenského",
        "Nová-Lhota",
    ],
)
def test_street_accepts_valid_values(value):
    validate_street(value)


@pytest.mark.parametrize(
    "value",
    [
        "Street<script>",
        "Test@Street",
        "",
    ],
)
def test_street_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_street(value)


@pytest.mark.parametrize(
    "value",
    [
        "12",
        "12A",
        "123/45",
        "10-b",
    ],
)
def test_house_number_accepts_valid_values(value):
    validate_house_number(value)


@pytest.mark.parametrize(
    "value",
    [
        "12@",
        "<script>",
        "",
    ],
)
def test_house_number_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_house_number(value)


@pytest.mark.parametrize(
    "value",
    [
        "Praha",
        "Bratislava",
        "Nové Město",
        "Košice - Staré Mesto",
        "Praha 4",
    ],
)
def test_location_name_accepts_valid_values(value):
    validate_location_name(value)


@pytest.mark.parametrize(
    "value",
    [
        "Praha<script>",
        "Brno@",
        "",
    ],
)
def test_location_name_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_location_name(value)


@pytest.mark.parametrize(
    "value",
    [
        "11000",
        "110 00",
        "040 01",
        "SW1A 1AA",
    ],
)
def test_postal_code_accepts_valid_values(value):
    validate_postal_code(value)


@pytest.mark.parametrize(
    "value",
    [
        "12",
        "12345678901",
        "110_00",
        "<123>",
    ],
)
def test_postal_code_rejects_invalid_values(value):
    with pytest.raises(ValidationError):
        validate_postal_code(value)


def test_notes_accepts_valid_value():
    validate_notes("Krátká interní poznámka.")


def test_notes_rejects_too_long_value():
    with pytest.raises(ValidationError):
        validate_notes("a" * 257)


@pytest.mark.parametrize(
    "value",
    [
        "<b>text</b>",
        "text > něco",
        "text < něco",
    ],
)
def test_notes_rejects_html_like_content(value):
    with pytest.raises(ValidationError):
        validate_notes(value)


@pytest.mark.parametrize(
    "value",
    [
        "Normální text.",
        "Text s číslem 123.",
        "Poznámka bez HTML.",
    ],
)
def test_plain_text_accepts_valid_values(value):
    assert validate_plain_text(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "<script>alert(1)</script>",
        "<iframe src='x'></iframe>",
        "<b>text</b>",
        "javascript:alert(1)",
        "<object></object>",
        "<embed>",
        "<style>body{}</style>",
        "<link href='x'>",
    ],
)
def test_plain_text_rejects_dangerous_values(value):
    with pytest.raises(ValidationError):
        validate_plain_text(value)


@pytest.mark.django_db
def test_contact_view_sends_emails(client, settings):
    settings.DEBUG = True

    data = {
        "first_name": "Jan",
        "last_name": "Novák",
        "email": "jan@example.com",
        "subject": "Dotaz",
        "message_body": "Toto je testovací dotaz.",
        "agree_gdpr": "on",
        "website": "",
        "turnstile": "test",
    }

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}

        with patch("core.views.EmailMultiAlternatives.send", return_value=1) as send:
            response = client.post(reverse("contact"), data=data)

    assert response.status_code == 302
    assert send.call_count == 2


@pytest.mark.django_db
def test_contact_view_fails_when_email_sending_fails(client, settings):
    settings.DEBUG = True

    data = {
        "first_name": "Jan",
        "last_name": "Novák",
        "email": "jan@example.com",
        "subject": "Dotaz",
        "message_body": "Toto je testovací dotaz.",
        "agree_gdpr": "on",
        "website": "",
        "turnstile": "test",
    }

    with patch("core.forms.requests.post") as turnstile_post:
        turnstile_post.return_value.json.return_value = {"success": True}

        with patch(
            "core.views.EmailMultiAlternatives.send",
            side_effect=Exception("SMTP failure"),
        ):
            response = client.post(reverse("contact"), data=data)

    assert response.status_code == 302
    assert response.url == reverse("contact")


def test_turnstile_site_key_context_processor(settings, rf):
    settings.TURNSTILE_SITE_KEY = "test-site-key"

    request = rf.get("/")

    context = turnstile_site_key(request)

    assert context == {"TURNSTILE_SITE_KEY": "test-site-key"}


def test_frontend_flags_context_processor(settings, rf):
    settings.USE_MINIFIED_JS = True

    request = rf.get("/")

    context = frontend_flags(request)

    assert context == {"USE_MINIFIED_JS": True}


def test_core_sitemap_items():
    sitemap = CoreViewSitemap()

    assert sitemap.items() == [
        "home",
        "contact",
        "membership_application",
        "gdpr",
        "membership_terms",
    ]


@pytest.mark.parametrize(
    "name",
    [
        "home",
        "contact",
        "membership_application",
        "gdpr",
        "membership_terms",
    ],
)
def test_core_sitemap_locations_resolve(name):
    sitemap = CoreViewSitemap()

    assert sitemap.location(name) == reverse(name)
