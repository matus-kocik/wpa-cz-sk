from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from core.sitemaps import CoreViewSitemap
from core.views import ContactView, MembershipApplicationView

sitemaps = {
    "core": CoreViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("kontakt/", ContactView.as_view(), name="contact"),
    path(
        "prihlaska/",
        MembershipApplicationView.as_view(),
        name="membership_application",
    ),
    path(
        "wpa-ve-svete/",
        TemplateView.as_view(template_name="wpa_world.html"),
        name="wpa_world",
    ),
    path(
        "dokumenty/",
        TemplateView.as_view(template_name="documents.html"),
        name="documents",
    ),
    path("gdpr/", TemplateView.as_view(template_name="gdpr.html"), name="gdpr"),
    path(
        "podminky-prihlasky/",
        TemplateView.as_view(template_name="membership_terms.html"),
        name="membership_terms",
    ),
    path(
        "stanovy/",
        TemplateView.as_view(template_name="statutes.html"),
        name="statutes",
    ),
    path(
        "clenove/", TemplateView.as_view(template_name="members.html"), name="members"
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]
