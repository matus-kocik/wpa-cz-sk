from django.contrib import admin

from .models import Article, Category, Contributor


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "slug")
    search_fields = ("name",)
    list_filter = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    list_per_page = 25


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "member")
    list_filter = ("role",)
    search_fields = ("name", "member__username", "member__first_name", "member__last_name")
    ordering = ("name",)
    autocomplete_fields = ("member",)
    list_select_related = ("member",)
    list_per_page = 25


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    def contributors_list(self, obj):
        names = []
        for c in obj.contributors.all()[:3]:
            if c.name:
                names.append(c.name)
            elif c.member:
                names.append(str(c.member))
        return ", ".join(names)

    contributors_list.short_description = "Přispěvatelé"

    list_display = ("title", "category", "contributors_list", "publication_date", "is_published")
    list_filter = ("is_published", "category", "publication_date", "species")
    search_fields = ("title", "summary", "pdf_title", "published_in", "contributors__name")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug",)
    autocomplete_fields = ("contributors", "category", "species")
    filter_horizontal = ("contributors", "species")
    list_select_related = ("category",)
    ordering = ("-publication_date",)
    list_per_page = 25
    date_hierarchy = "publication_date"

    fieldsets = (
        ("Základní informace", {
            "fields": ("title", "slug", "category", "publication_date")
        }),
        ("Druhy", {
            "fields": ("species",)
        }),
        ("Obsah", {
            "fields": ("summary", "pdf_title", "pdf_file", "main_image")
        }),
        ("Přispěvatelé", {
            "fields": ("contributors",)
        }),
        ("Publikace jinde", {
            "fields": ("published_in", "published_in_date", "published_in_url")
        }),
        ("Stav a poznámky", {
            "fields": ("note", "is_published")
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "meta_keywords"),
            "classes": ("collapse",),
        }),
    )
