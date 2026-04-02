from django.contrib import admin

from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "registration_number",
        "full_name",
        "status",
        "role",
        "is_active",
        "is_valid_display",
        "valid_until",
        "joined_at",
    )

    list_display_links = ("registration_number", "full_name")

    list_editable = ("status", "role", "is_active")

    list_filter = (
        "status",
        "role",
        "is_active",
        "joined_at",
        "valid_until",
    )

    search_fields = (
        "user__email__icontains",
        "user__first_name__icontains",
        "user__last_name__icontains",
        "registration_number__icontains",
    )

    ordering = ("registration_number", "joined_at")

    list_select_related = ("user",)

    date_hierarchy = "joined_at"
    list_per_page = 50

    empty_value_display = "-"

    readonly_fields = (
        "registration_number",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = ("user",)

    fieldsets = (
        (
            "Member",
            {
                "fields": (
                    "user",
                    "registration_number",
                    "status",
                    "role",
                    "is_active",
                )
            },
        ),
        (
            "Membership Dates",
            {
                "fields": (
                    "joined_at",
                    "valid_until",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": ("note",)
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(boolean=True, description="Valid")
    def is_valid_display(self, obj):
        return obj.is_valid
