from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from events.models import Event
from profiles.models import PublicProfile
from taxonomy.models import Species


class CoreViewSitemap(Sitemap):
    protocol = "https"
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "contact",
            "membership_application",
            "wpa_world",
            "projects",
            "projekt-bazant-vietnamsky",
            "projekt-bazant-zlaty",
            "projekt-koroptve-polni",
            "documents",
            "chovatelske_rady",
            "zaciname",
            "liahnutie",
            "voliery",
            "krmivo",
            "veterina",
            "krouzky",
            "gdpr",
            "membership_terms",
            "statutes",
            "members",
            "species_list",
            "support",
            "event_list",
        ]

    def location(self, item):
        return reverse(item)


class SpeciesSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"

    def items(self):
        return Species.objects.filter(is_active=True).exclude(slug="").order_by("pk")

    def location(self, item):
        return reverse("species_detail", args=[item.slug])

    def lastmod(self, item):
        return item.updated_at


class EventSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Event.objects.filter(is_public=True).exclude(slug="").order_by("pk")

    def location(self, item):
        return reverse("event_detail", args=[item.slug])

    def lastmod(self, item):
        return item.updated_at


class PublicProfileSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"

    def items(self):
        return (
            PublicProfile.objects.filter(is_public=True).exclude(slug="").order_by("pk")
        )

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at
