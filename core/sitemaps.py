from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class CoreViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "contact",
            "membership_application",
            "gdpr",
            "membership_terms",
        ]

    def location(self, item):
        return reverse(item)
