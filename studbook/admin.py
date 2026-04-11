from django.contrib import admin

from .models import (
    BirdEvent,
    BirdRecord,
    CareRecord,
    HealthRecord,
    TransferRecord,
)


class BirdEventInline(admin.TabularInline):
    model = BirdEvent
    extra = 0
    ordering = ("-event_date",)


class HealthRecordInline(admin.TabularInline):
    model = HealthRecord
    extra = 0
    ordering = ("-record_date",)


class CareRecordInline(admin.TabularInline):
    model = CareRecord
    extra = 0
    ordering = ("-care_date",)


class TransferRecordInline(admin.TabularInline):
    model = TransferRecord
    extra = 0
    ordering = ("-transfer_date",)


@admin.register(BirdRecord)
class BirdRecordAdmin(admin.ModelAdmin):
    list_display = (
        "ring_number",
        "species",
        "name",
        "sex",
        "status",
        "member",
        "current_location",
    )

    list_filter = (
        "species",
        "sex",
        "status",
        "member",
    )

    search_fields = (
        "ring_number",
        "name",
        "species__latin_name",
        "species__czech_name",
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
    )

    autocomplete_fields = (
        "member",
        "species",
        "subspecies",
        "father",
        "mother",
    )

    list_select_related = ("member", "member__user", "species", "subspecies", "father", "mother")

    date_hierarchy = "hatch_date"

    list_per_page = 25

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Základní informace", {
            "fields": (
                "member",
                "species",
                "subspecies",
                "name",
                "ring_number",
                "sex",
                "status",
            )
        }),
        ("Původ a rodokmen", {
            "fields": (
                "father",
                "mother",
                "source",
                "breeder_name",
            )
        }),
        ("Životní údaje", {
            "fields": (
                "hatch_date",
                "acquisition_date",
                "death_date",
                "current_location",
            )
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )

    inlines = [
        BirdEventInline,
        HealthRecordInline,
        CareRecordInline,
        TransferRecordInline,
    ]


@admin.register(BirdEvent)
class BirdEventAdmin(admin.ModelAdmin):
    list_display = ("bird", "event_type", "event_date")
    list_filter = ("event_type", "event_date")
    search_fields = (
        "bird__ring_number",
        "bird__name",
    )
    autocomplete_fields = ("bird",)
    list_select_related = ("bird",)
    list_per_page = 25
    date_hierarchy = "event_date"


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("bird", "record_date", "diagnosis")
    list_filter = ("record_date",)
    search_fields = ("bird__ring_number", "diagnosis")
    autocomplete_fields = ("bird",)
    list_select_related = ("bird",)
    list_per_page = 25
    date_hierarchy = "record_date"


@admin.register(CareRecord)
class CareRecordAdmin(admin.ModelAdmin):
    list_display = ("bird", "care_type", "care_date")
    list_filter = ("care_type", "care_date")
    search_fields = ("bird__ring_number", "product")
    autocomplete_fields = ("bird",)
    list_select_related = ("bird",)
    list_per_page = 25
    date_hierarchy = "care_date"


@admin.register(TransferRecord)
class TransferRecordAdmin(admin.ModelAdmin):
    list_display = ("bird", "transfer_type", "transfer_date", "partner_name")
    list_filter = ("transfer_type", "transfer_date")
    search_fields = ("bird__ring_number", "partner_name")
    autocomplete_fields = ("bird",)
    list_select_related = ("bird",)
    list_per_page = 25
    date_hierarchy = "transfer_date"
