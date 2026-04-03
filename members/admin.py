from django.contrib import admin

from .models import MemberProfile, MembershipApplication


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "registration_number",
        "full_name",
        "status",
        "position",
        "is_active",
        "is_valid_display",
        "valid_until",
        "joined_at",
    )

    list_display_links = ("full_name",)

    list_editable = ("registration_number", "status", "position", "is_active")

    list_filter = (
        "status",
        "position",
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
                    "position",
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


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "user",
        "status",
        "payment_status",
        "created_at",
    )

    list_display_links = ("first_name", "last_name")

    list_editable = ("status", "payment_status")

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"
    list_per_page = 50

    empty_value_display = "-"

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "academic_title",
                    "birth_date",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "email",
                    "phone_number",
                )
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "city",
                    "street",
                    "house_number",
                    "postal_code",
                    "district",
                    "country",
                )
            },
        ),
        (
            "Declaration",
            {
                "fields": (
                    "declaration_place",
                    "declaration_date",
                    "declaration_signature",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "user",
                    "status",
                    "payment_status",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",)
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.approve()
