from django.contrib import admin

from .models import MemberProfile, MembershipApplication


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "icch_number",
        "full_name",
        "payment_status",
        "membership_type",
        "member_type",
        "country",
        "is_active",
        "is_valid_display",
        "valid_until",
        "joined_at",
    )

    list_display_links = ("full_name",)

    list_editable = ("payment_status", "membership_type", "is_active")

    list_filter = (
        "payment_status",
        "membership_type",
        "member_type",
        "is_active",
        "joined_at",
        "valid_until",
        "country",
        "roles",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "icch_number",
    )

    ordering = ("icch_number", "user__last_name")

    list_select_related = ("user",)

    date_hierarchy = "joined_at"
    list_per_page = 50

    empty_value_display = "-"


    autocomplete_fields = ("user",)
    filter_horizontal = ("roles",)

    fieldsets = (
        (
            "Člen",
            {
                "fields": (
                    "user",
                    "icch_number",
                    "payment_status",
                    "membership_type",
                    "member_type",
                    "is_active",
                    "roles",
                )
            },
        ),
        (
            "Členství",
            {
                "fields": (
                    "valid_until",
                )
            },
        ),
        (
            "Kontakt a adresa",
            {
                "fields": (
                    "phone_number",
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
            "Poznámky",
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

    @admin.display(boolean=True, description="Platné")
    def is_valid_display(self, obj):
        return obj.is_valid

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ("created_at", "updated_at", "joined_at")
        return ("created_at", "updated_at", "joined_at", "icch_number")


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "country",
        "user",
        "status",
        "initial_payment_status",
        "created_at",
    )

    list_display_links = ("first_name", "last_name")

    list_editable = ("status", "initial_payment_status")

    list_filter = (
        "status",
        "initial_payment_status",
        "created_at",
        "country",
    )

    search_fields = (
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
        "country__icontains",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"
    list_per_page = 50

    empty_value_display = "-"

    readonly_fields = ("created_at", "updated_at")

    autocomplete_fields = ("user",)

    fieldsets = (
        (
            "Základní informace",
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
            "Kontakt",
            {
                "fields": (
                    "email",
                    "phone_number",
                )
            },
        ),
        (
            "Adresa",
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
            "Prohlášení",
            {
                "fields": (
                    "declaration_place",
                    "declaration_date",
                    "declaration_signature",
                )
            },
        ),
        (
            "Stav",
            {
                "fields": (
                    "user",
                    "status",
                    "initial_payment_status",
                )
            },
        ),
        (
            "Poznámky",
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
        # First save normally
        super().save_model(request, obj, form, change)

        # Then handle approval logic safely (only on change)
        if (
            change
            and obj.status == "approved"
            and obj.initial_payment_status == "paid"
            and not obj.user
        ):
            try:
                obj.approve()
            except Exception as e:
                self.message_user(
                    request,
                    f"Approve failed: {e}",
                    level="error",
                )
