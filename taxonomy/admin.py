from django.contrib import admin

from .models import Family, Genus, Species, Subspecies


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "name", "slug")
    list_filter = ()
    ordering = ("latin_name",)
    list_per_page = 25
    search_fields = ("latin_name", "name")
    prepopulated_fields = {"slug": ("latin_name",)}


@admin.register(Genus)
class GenusAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "name", "family")
    list_filter = ("family",)
    search_fields = ("latin_name", "name")
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


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "czech_name", "genus", "status_in_nature", "is_active")
    list_filter = ("genus", "status_in_nature", "is_active")
    search_fields = ("latin_name", "czech_name", "authority")
    ordering = ("latin_name",)
    list_select_related = ("genus", "genus__family")
    list_per_page = 25
    autocomplete_fields = ("genus",)
    prepopulated_fields = {"slug": ("latin_name",)}

    inlines = [SubspeciesInline]

    fieldsets = (
        ("Základní informace", {
            "fields": ("latin_name", "authority", "czech_name", "slug", "genus", "is_active")
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
            "fields": ("maturity", "length", "weight", "clutch", "incubation")
        }),
        ("Chov", {
            "fields": ("ring_size", "population", "breeding_difficulty")
        }),
        ("Média", {
            "fields": ("main_image", "secondary_image")
        }),
        ("Externé odkazy", {
            "fields": ("videos", "images_url")
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
    list_display = ("latin_name", "species")
    list_filter = ("species",)
    search_fields = ("latin_name", "species__latin_name")
    ordering = ("latin_name",)
    list_select_related = ("species",)
    list_per_page = 25
    autocomplete_fields = ("species",)
