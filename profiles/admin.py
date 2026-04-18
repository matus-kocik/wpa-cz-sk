from django.contrib import admin

from .models import ProfileGallery, ProfileVideo, PublicProfile


class ProfileVideoInline(admin.TabularInline):
    model = ProfileVideo
    extra = 1
    fields = ("url", "title", "created_at")
    readonly_fields = ("created_at",)


class ProfileGalleryInline(admin.TabularInline):
    model = ProfileGallery
    extra = 1
    fields = ("image", "caption", "created_at")
    readonly_fields = ("created_at",)


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "member",
        "location_display",
        "is_public",
        "show_email",
        "show_phone",
        "show_location",
        "show_website",
        "show_avatar",
        "show_species",
        "show_other_species",
        "show_additional_info",
        "updated_at",
    )

    list_filter = (
        "is_public",
        "show_email",
        "show_phone",
        "show_website",
        "show_avatar",
        "show_species",
        "show_additional_info",
        "show_other_species",
        "show_gallery",
        "show_videos",
    )

    search_fields = (
        "display_name",
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
        "website",
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
            "fields": ("bio", "additional_info")
        }),
        ("Kontakt", {
            "fields": ("public_email", "phone", "website")
        }),
        ("Chov", {
            "fields": (
                "species",
                "other_species",
            )
        }),
        ("Sociální sítě", {
            "fields": ("facebook_url", "instagram_url", "youtube_url")
        }),
        ("Viditelnost", {
            "fields": (
                "is_public",
                "show_avatar",
                "show_bio",
                "show_additional_info",
                "show_species",
                "show_other_species",
                "show_email",
                "show_phone",
                "show_location",
                "show_website",
                "show_social",
                "show_gallery",
                "show_videos",
            )
        }),
        ("Systémové informace", {
            "fields": ("created_at", "updated_at")
        }),
    )

    ordering = ("-updated_at",)
    list_per_page = 25
    inlines = [ProfileVideoInline, ProfileGalleryInline]
