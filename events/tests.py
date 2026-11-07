from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from .models import Event


@pytest.fixture
def event_factory():
    def create(slug, **kwargs):
        data = {
            "title": slug,
            "slug": slug,
            "start_date": timezone.now() + timedelta(days=2),
        }
        data.update(kwargs)
        return Event.objects.create(**data)

    return create


@pytest.mark.django_db
def test_event_list_visibility_dates_and_archive(client, event_factory):
    future = event_factory("future")
    ongoing = event_factory(
        "ongoing",
        start_date=timezone.now() - timedelta(days=1),
        end_date=timezone.now() + timedelta(days=1),
    )
    past = event_factory("past", start_date=timezone.now() - timedelta(days=3))
    event_factory("private", is_public=False)
    event_factory("")
    response = client.get(reverse("event_list"))
    assert response.status_code == 200
    assert list(response.context["events"]) == [ongoing, future]
    response = client.get(reverse("event_list"), {"archive": "1"})
    assert list(response.context["events"]) == [past]


@pytest.mark.django_db
def test_event_detail_hides_private_data_and_escapes_content(client, event_factory):
    event = event_factory(
        "external",
        title="<script>alert(1)</script>",
        notes="internal secret",
        is_external=True,
        source_url="https://example.com/event",
        description="Original description",
        itinerary="Programme",
    )
    response = client.get(reverse("event_detail", args=[event.slug]))
    assert response.status_code == 200
    html = response.content.decode()
    assert "internal secret" not in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert 'rel="noopener noreferrer"' in html
    assert 'href="https://example.com/event"' in html
    assert "Original description" in html and "Programme" in html
    private = event_factory("private", is_public=False)
    assert client.get(reverse("event_detail", args=[private.slug])).status_code == 404
    assert client.get(reverse("event_detail", args=["missing"])).status_code == 404


@pytest.mark.django_db
def test_event_list_empty_and_pagination(client, event_factory):
    response = client.get(reverse("event_list"))
    assert "Aktuálně nejsou zveřejněny" in response.content.decode()
    for i in range(13):
        event_factory(f"event-{i}", start_date=timezone.now() - timedelta(days=3))
    response = client.get(reverse("event_list"), {"archive": "1"})
    assert len(response.context["events"]) == 12
    assert "archive=1&amp;page=2" in response.content.decode()


@pytest.mark.django_db
def test_date_only_event_stays_upcoming_until_end_of_day(client, event_factory):
    from datetime import datetime
    from unittest.mock import patch
    from zoneinfo import ZoneInfo

    now = datetime(2027, 2, 7, 15, tzinfo=ZoneInfo("Europe/Prague"))
    event = event_factory(
        "dates-only",
        dates_only=True,
        start_date=now.replace(day=6, hour=0),
        end_date=now.replace(hour=0),
    )
    with patch("events.views.timezone.now", return_value=now):
        response = client.get(reverse("event_list"))
        assert event in response.context["events"]
        archive = client.get(reverse("event_list"), {"archive": "1"})
        assert event not in archive.context["events"]
    response = client.get(reverse("event_detail", args=[event.slug]))
    html = response.content.decode()
    assert "00:00" not in html
    assert 'datetime="2027-02-06"' in html


@pytest.mark.django_db
def test_own_events_stand_out_without_changing_date_order(client, event_factory):
    external = event_factory("earlier", section="de", is_external=True)
    own = event_factory("own", start_date=timezone.now() + timedelta(days=4))
    assert own.is_own_event
    assert not external.is_own_event
    assert not Event(section="cz_sk", is_external=True).is_own_event
    response = client.get(reverse("event_list"))
    assert list(response.context["events"]) == [external, own]
    html = response.content.decode()
    assert html.count("Akce WPA CZ-SK") == 1
    assert "border-2 border-green-600" in html
    assert (
        "Akce WPA CZ-SK"
        in client.get(reverse("event_detail", args=[own.slug])).content.decode()
    )


@pytest.mark.django_db
def test_reviewed_import_is_repeatable_and_preserves_existing_records(event_factory):
    from django.core.management import call_command

    existing = event_factory(
        "wpa-uk-cbag-2027", title="Upraveno ručně", is_public=False
    )
    call_command("import_reviewed_events")
    assert Event.objects.count() == 12
    assert Event.objects.filter(is_public=True).count() == 11
    call_command("import_reviewed_events")
    assert Event.objects.count() == 12
    existing.refresh_from_db()
    assert existing.title == "Upraveno ručně" and not existing.is_public
