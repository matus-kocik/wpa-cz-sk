from django.contrib import admin

from .models import PublicProfile


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "member",
        "is_public",
        "updated_at",
    )

    list_filter = (
        "is_public",
    )

    search_fields = (
        "display_name",
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
    )

    autocomplete_fields = ("member",)

    filter_horizontal = ("species",)

    readonly_fields = ("slug", "created_at", "updated_at")

    fieldsets = (
        ("Základ", {
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
        ("Sociálne siete", {
            "fields": ("facebook_url", "youtube_url")
        }),
        ("Viditeľnosť", {
            "fields": (
                "is_public",
                "show_email",
                "show_phone",
                "show_location",
                "show_breeding",
            )
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at")
        }),
    )

    ordering = ("-updated_at",)
