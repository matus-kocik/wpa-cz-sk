from django.contrib import admin

from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    autocomplete_fields = ("member",)
    ordering = ("-year",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "coordinator", "start_date", "end_date", "is_public")
    list_filter = ("status", "is_public", "start_date")
    search_fields = ("name", "description", "coordinator__user__email", "coordinator__user__first_name", "coordinator__user__last_name")
    autocomplete_fields = ("coordinator", "species")
    list_select_related = ("coordinator", "coordinator__user")
    filter_horizontal = ("species",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start_date", "name")
    list_per_page = 25

    fieldsets = (
        ("Základní informace", {
            "fields": ("name", "slug", "status", "is_public")
        }),
        ("Popis", {
            "fields": ("description",)
        }),
        ("Organizace", {
            "fields": ("coordinator", "species")
        }),
        ("Termíny", {
            "fields": ("start_date", "end_date")
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )

    inlines = [ProjectMembershipInline]


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("member", "project", "year", "annual_fee", "is_paid", "paid_at")
    list_filter = ("year", "is_paid", "project")
    search_fields = (
        "member__user__email",
        "member__user__first_name",
        "member__user__last_name",
        "project__name",
    )
    autocomplete_fields = ("member", "project")
    list_select_related = ("member", "member__user", "project")
    ordering = ("-year", "project", "member")
    list_per_page = 25

    fieldsets = (
        ("Základní informace", {
            "fields": ("member", "project", "year")
        }),
        ("Platba", {
            "fields": ("annual_fee", "is_paid", "paid_at")
        }),
        ("Poznámky", {
            "fields": ("notes",)
        }),
    )
