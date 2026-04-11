from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "start_date",
        "end_date",
        "location",
        "is_external",
        "is_public",
        "is_featured",
    )

    list_filter = (
        "section",
        "is_external",
        "is_public",
        "is_featured",
        "start_date",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "organizer",
    )

    autocomplete_fields = ("species",)

    list_select_related = ("section",)

    filter_horizontal = ("species",)

    prepopulated_fields = {"slug": ("title",)}

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-start_date",)

    list_per_page = 25

    date_hierarchy = "start_date"

    fieldsets = (
        ("Základní informace", {
            "fields": (
                "title",
                "slug",
                "section",
                "is_external",
                "is_public",
                "is_featured",
            )
        }),
        ("Popis", {
            "fields": ("description", "itinerary")
        }),
        ("Termíny", {
            "fields": ("start_date", "end_date")
        }),
        ("Místo a organizace", {
            "fields": ("location", "organizer")
        }),
        ("Odkazy", {
            "fields": ("source_url", "external_url")
        }),
        ("Taxonomie", {
            "fields": ("species",)
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )
