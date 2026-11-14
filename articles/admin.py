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
    search_fields = (
        "name",
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
    )
    ordering = ("name",)
    autocomplete_fields = ("member",)
    list_select_related = ("member", "member__user")
    list_per_page = 25


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("contributors__member__user")
        )

    def contributors_list(self, obj):
        names = []
        for c in obj.contributors.all()[:3]:
            if c.name:
                names.append(c.name)
            elif c.member:
                names.append(str(c.member))
        return ", ".join(names)

    contributors_list.short_description = "Přispěvatelé"

    list_display = (
        "title",
        "category",
        "contributors_list",
        "publication_date",
        "is_published",
    )
    list_filter = ("is_published", "category", "publication_date", "species")
    search_fields = (
        "title",
        "summary",
        "pdf_title",
        "published_in",
        "contributors__name",
        "contributors__member__user__first_name",
        "contributors__member__user__last_name",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "published_at")
    autocomplete_fields = ("contributors", "category", "species")
    list_select_related = ("category",)
    ordering = ("-publication_date",)
    list_per_page = 25
    date_hierarchy = "publication_date"

    fieldsets = (
        (
            "Základní informace",
            {"fields": ("title", "slug", "category", "publication_date")},
        ),
        ("Druhy", {"fields": ("species",)}),
        ("Obsah", {"fields": ("summary", "pdf_title", "pdf_file", "main_image")}),
        ("Přispěvatelé", {"fields": ("contributors",)}),
        (
            "Publikace jinde",
            {"fields": ("published_in", "published_in_date", "published_in_url")},
        ),
        ("Stav a poznámky", {"fields": ("note", "is_published", "published_at")}),
        (
            "SEO",
            {
                "fields": ("meta_title", "meta_description", "meta_keywords"),
                "classes": ("collapse",),
            },
        ),
    )
