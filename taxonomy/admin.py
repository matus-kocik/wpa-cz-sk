from django.contrib import admin

from .models import Family, Genus, Species, SpeciesLink, Subspecies


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "slug")
    list_filter = ()
    ordering = ("latin_name",)
    list_per_page = 25
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name")
    prepopulated_fields = {"slug": ("latin_name",)}


@admin.register(Genus)
class GenusAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "family")
    list_filter = ("family",)
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name")
    ordering = ("latin_name",)
    list_select_related = ("family",)
    list_per_page = 25
    autocomplete_fields = ("family",)
    prepopulated_fields = {"slug": ("latin_name",)}


class SubspeciesInline(admin.TabularInline):
    model = Subspecies
    extra = 0
    show_change_link = True
    ordering = ("latin_name",)


class SpeciesLinkInline(admin.TabularInline):
    model = SpeciesLink
    extra = 0
    show_change_link = True
    ordering = ("type",)


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "authority_year", "genus", "status_in_nature", "is_active")
    list_filter = ("genus", "status_in_nature", "is_active")
    search_fields = ("latin_name", "czech_name", "slovak_name", "english_name", "german_name", "authority", "authority_year")
    ordering = ("latin_name",)
    list_select_related = ("genus", "genus__family")
    list_per_page = 25
    autocomplete_fields = ("genus",)
    prepopulated_fields = {"slug": ("latin_name",)}

    inlines = [SubspeciesInline, SpeciesLinkInline]

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
                "slug",
                "genus",
                "is_active",
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
                ("length_male_min", "length_male_max"),
                ("length_female_min", "length_female_max"),
                ("weight_male_min", "weight_male_max"),
                ("weight_female_min", "weight_female_max"),
                ("clutch_min", "clutch_max"),
                "clutch_note",
                ("incubation_min", "incubation_max"),
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
        ("SEO", {
            "fields": ("meta_title", "meta_description", "meta_keywords")
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
