from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ["email", "full_name", "is_active", "is_staff", "date_joined"]
    list_display_links = ["email"]
    list_editable = [
        "is_active",
        "is_staff",
    ]
    search_fields = ["email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "date_joined"]
    readonly_fields = ["date_joined", "last_login"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("date_joined", "last_login")}),
    )
    ordering = ["-date_joined"]
    filter_horizontal = ["groups", "user_permissions"]


admin.site.register(CustomUser, CustomUserAdmin)
