from datetime import date, timedelta
from urllib.parse import urlsplit
from xml.etree import ElementTree

import pytest
from django.urls import resolve, reverse
from django.utils import timezone

from core.sitemaps import CoreViewSitemap
from events.models import Event
from members.models import MemberProfile
from taxonomy.models import Family, Genus, Species
from users.models import CustomUser


@pytest.mark.django_db
def test_sitemap_contains_only_public_resolvable_urls(client):
    family = Family.objects.create(latin_name="Sitemapidae")
    genus = Genus.objects.create(latin_name="Sitemapus", family=family)
    active = Species.objects.create(latin_name="Sitemapus publicus", genus=genus)
    hidden = Species.objects.create(
        latin_name="Sitemapus privatus", genus=genus, is_active=False
    )
    public = Event.objects.create(
        title="Public", slug="public", start_date=timezone.now() + timedelta(days=2)
    )
    private = Event.objects.create(
        title="Private", slug="private", start_date=timezone.now(), is_public=False
    )
    user = CustomUser.objects.create_user(
        email="sitemap@example.com", first_name="Test", last_name="User"
    )
    member = MemberProfile.objects.create(user=user, joined_at=date(2024, 1, 1))
    profile = member.public_profile
    profile.is_public = False
    profile.save()
    response = client.get(reverse("sitemap"))
    assert response.status_code == 200
    tree = ElementTree.fromstring(response.content)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in tree.findall("s:url/s:loc", namespace)]
    assert len(urls) == len(set(urls))
    paths = {urlsplit(url).path for url in urls}
    assert {reverse(name) for name in CoreViewSitemap().items()} <= paths
    assert reverse("species_detail", args=[active.slug]) in paths
    assert reverse("species_detail", args=[hidden.slug]) not in paths
    assert reverse("event_detail", args=[public.slug]) in paths
    assert reverse("event_detail", args=[private.slug]) not in paths
    assert profile.get_absolute_url() not in paths
    assert all(url.startswith("https://") for url in urls)
    for path in paths:
        resolve(path)
        assert client.get(path).status_code == 200, path
    profile.is_public = True
    profile.save()
    assert profile.get_absolute_url() in client.get(reverse("sitemap")).content.decode()


@pytest.mark.parametrize("name", ["dashboard_home", "public_profile_edit"])
def test_protected_pages_redirect_to_existing_login(client, name):
    response = client.get(reverse(name))
    assert response.status_code == 302
    assert response.url == reverse("login") + "?next=" + reverse(name)
    assert client.get(response.url).status_code == 200


def test_robots_points_to_sitemap_on_current_host(client, settings):
    settings.ALLOWED_HOSTS = ["wpacz-sk.com"]
    response = client.get("/robots.txt", secure=True, HTTP_HOST="wpacz-sk.com")
    assert response.status_code == 200
    assert "Sitemap: https://wpacz-sk.com/sitemap.xml" in response.content.decode()
