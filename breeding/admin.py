from django.contrib import admin

from .models import BreedingRecord, BreedingReport


class BreedingRecordInline(admin.TabularInline):
    model = BreedingRecord
    extra = 0
    show_change_link = True
    autocomplete_fields = ("species",)
    ordering = ("species",)


@admin.register(BreedingReport)
class BreedingReportAdmin(admin.ModelAdmin):
    list_display = ("member", "year", "status", "submitted_at", "approved_at", "updated_at")
    list_filter = ("year", "status", "submitted_at", "approved_at")
    search_fields = (
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
        "full_name",
        "email",
    )
    autocomplete_fields = ("member",)
    readonly_fields = ("created_at", "updated_at", "submitted_at", "approved_at")
    list_select_related = ("member", "member__user")
    list_per_page = 25
    ordering = ("-year", "member")
    inlines = [BreedingRecordInline]

    fieldsets = (
        ("Základní informace", {
            "fields": ("member", "year", "status")
        }),
        ("Údaje člena", {
            "fields": (
                "full_name",
                "address",
                "city",
                "postal_code",
                "country",
                "phone",
                "email",
            )
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
        ("Stav odeslání", {
            "fields": ("submitted_at", "approved_at")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    list_display = (
        "report",
        "species",
        "pairs_with_chicks",
        "number_of_males",
        "number_of_females",
        "total_count_of_species",
        "total_count_offspring",
    )
    list_filter = ("report__year", "species")
    search_fields = (
        "report__member__user__email",
        "report__member__user__first_name",
        "report__member__user__last_name",
        "species__latin_name",
        "species__czech_name",
    )
    autocomplete_fields = ("report", "species")
    list_select_related = ("report", "report__member", "species")
    list_per_page = 25
    ordering = ("report", "species")

    fieldsets = (
        ("Základní informace", {
            "fields": ("report", "species")
        }),
        ("Chov", {
            "fields": ("pairs_with_chicks", "number_of_males", "number_of_females")
        }),
        ("Odchov", {
            "fields": (
                "number_of_male_offspring",
                "number_of_female_offspring",
                "number_of_unsexed_offspring",
            )
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
    )
