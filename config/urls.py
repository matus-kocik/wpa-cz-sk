from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from core.sitemaps import CoreViewSitemap
from core.views import ContactView
from members.views import MembershipApplicationView
from users.forms import CustomPasswordResetForm, CustomSetPasswordForm, LoginForm
from users.views import CustomLoginView, CustomLogoutView

sitemaps = {
    "core": CoreViewSitemap,
}

if settings.DEBUG:
    admin_url = "admin/"
else:
    admin_url = getattr(settings, "ADMIN_URL", "admin/")

urlpatterns = [
    path(admin_url, admin.site.urls),
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
        "projekty/",
        TemplateView.as_view(template_name="projects.html"),
        name="projects",
    ),
    path(
        "projekty/bazant-vietnamsky/",
        TemplateView.as_view(template_name="bazant-vietnamsky.html"),
        name="projekt-bazant-vietnamsky",
    ),
    path(
        "projekty/bazant-zlaty/",
        TemplateView.as_view(template_name="bazant-zlaty.html"),
        name="projekt-bazant-zlaty",
    ),
    path(
        "projekty/koroptve-polni/",
        TemplateView.as_view(template_name="koroptve-polni.html"),
        name="projekt-koroptve-polni",
    ),
    path(
        "dokumenty/",
        TemplateView.as_view(template_name="documents.html"),
        name="documents",
    ),
    path(
        "chovatelske-rady/",
        TemplateView.as_view(template_name="chovatelske_rady.html"),
        name="chovatelske_rady",
    ),
    path(
        "zaciname/",
        TemplateView.as_view(template_name="zaciname.html"),
        name="zaciname",
    ),
    path(
        "liahnutie/",
        TemplateView.as_view(template_name="liahnutie.html"),
        name="liahnutie",
    ),
    path(
        "voliery/",
        TemplateView.as_view(template_name="voliery.html"),
        name="voliery",
    ),
    path(
        "krmivo/",
        TemplateView.as_view(template_name="krmivo.html"),
        name="krmivo",
    ),
    path(
        "veterina/",
        TemplateView.as_view(template_name="veterina.html"),
        name="veterina",
    ),
    path(
        "krouzky/",
        TemplateView.as_view(template_name="velikosti-krouzku.html"),
        name="krouzky",
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
    path(
        "podpora/",
        TemplateView.as_view(template_name="support.html"),
        name="support",
    ),
    path(
        "login/",
        CustomLoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            form_class=CustomPasswordResetForm,
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
