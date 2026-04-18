from django.contrib import admin

from .models import Family, Genus, Species, SpeciesLink, Subfamily, Subspecies


class SpeciesLinkInline(admin.TabularInline):
    model = SpeciesLink
    extra = 1


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "slug")
    list_filter = ()
    ordering = ("latin_name",)
    list_per_page = 25
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name")
    readonly_fields = ("slug",)


@admin.register(Subfamily)
class SubfamilyAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "family", "slug")
    list_filter = ("family",)
    ordering = ("latin_name",)
    list_per_page = 25
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name")
    autocomplete_fields = ("family",)
    readonly_fields = ("slug",)


@admin.register(Genus)
class GenusAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "subfamily")
    list_filter = ("subfamily",)
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name")
    ordering = ("latin_name",)
    list_select_related = ("subfamily", "subfamily__family")
    list_per_page = 25
    autocomplete_fields = ("subfamily",)
    readonly_fields = ("slug",)


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "authority_year", "genus", "status_in_nature", "is_active")
    list_filter = ("genus", "status_in_nature", "is_active")
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "authority", "authority_year")
    ordering = ("latin_name",)
    list_select_related = ("genus", "genus__subfamily", "genus__subfamily__family")
    list_per_page = 25
    autocomplete_fields = ("genus",)
    readonly_fields = ("slug",)
    inlines = [SpeciesLinkInline]

    fieldsets = (
        ("Základní informace", {
            "fields": (
                "latin_name",
                "authority",
                "authority_year",
                "czech_name",
                "slovak_name",
                "english_name",
                "german_name",
                "genus",
                "is_active",
                "slug",
            )
        }),
        ("Poddruhy", {
            "fields": ("subspecies_note",)
        }),
        ("Výskyt", {
            "fields": ("distribution", "habitat")
        }),
        ("Stav", {
            "fields": ("status_in_nature", "status_in_captivity")
        }),
        ("Biologie", {
            "fields": (
                "maturity",
                "length_male_min",
                "length_male_max",
                "length_female_min",
                "length_female_max",
                "weight_male_min",
                "weight_male_max",
                "weight_female_min",
                "weight_female_max",
                "clutch_min",
                "clutch_max",
                "clutch_note",
                "incubation_min",
                "incubation_max",
                "incubation_note",
            )
        }),
        ("Chov", {
            "fields": ("ring_size", "population", "breeding_difficulty")
        }),
        ("Média", {
            "fields": ("main_image",)
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
    )


@admin.register(Subspecies)
class SubspeciesAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "species")
    list_filter = ("species",)
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "species__latin_name")
    ordering = ("latin_name",)
    list_select_related = ("species",)
    list_per_page = 25
    autocomplete_fields = ("species",)
