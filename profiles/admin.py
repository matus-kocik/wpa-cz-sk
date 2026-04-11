from django.contrib import admin

from .models import PublicProfile


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "member",
        "location",
        "is_public",
        "show_email",
        "updated_at",
    )

    list_filter = (
        "is_public",
        "show_email",
        "show_phone",
        "show_location",
    )

    search_fields = (
        "display_name",
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
        "location",
    )

    list_select_related = ("member", "member__user")

    autocomplete_fields = ("member", "species")

    filter_horizontal = ("species",)

    readonly_fields = ("slug", "created_at", "updated_at")

    fieldsets = (
        ("Základní informace", {
            "fields": ("member", "display_name", "slug", "avatar")
        }),
        ("Popis", {
            "fields": ("bio",)
        }),
        ("Kontakt", {
            "fields": ("public_email", "phone", "website", "location")
        }),
        ("Chov", {
            "fields": ("species", "specialization", "breeding_focus", "years_of_experience")
        }),
        ("Sociální sítě", {
            "fields": ("facebook_url", "youtube_url")
        }),
        ("Viditelnost", {
            "fields": (
                "is_public",
                "show_email",
                "show_phone",
                "show_location",
                "show_breeding",
            )
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )

    ordering = ("-updated_at",)
    list_per_page = 25
