from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import CustomUser


# Custom admin forms
class CustomUserCreationForm(forms.ModelForm):
    """
    Form for creating new users in the Django admin.
    """
    password1 = forms.CharField(label="Heslo", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Potvrzení hesla", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hesla se neshodují.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    Form for updating users in the Django admin.
    """
    password = ReadOnlyPasswordHashField(
        help_text=(
            "Hesla nejsou ukládána v čitelné podobě, proto není možné je zobrazit. Heslo můžete změnit pomocí <a href=\"../password/\">tohoto formuláře</a>."
        )
    )

    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ["email", "full_name", "email_verified", "is_active", "is_staff", "date_joined"]
    list_display_links = ["email", "full_name"]
    list_editable = ["is_active", "is_staff"]
    search_fields = ["email__icontains", "first_name__icontains", "last_name__icontains"]
    list_filter = ["email_verified", "is_active", "is_staff", "date_joined"]
    ordering = ["-date_joined"]
    list_per_page = 25
    list_select_related = ()  # no FK, kept for consistency
    date_hierarchy = "date_joined"
    readonly_fields = ["date_joined", "last_login"]
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Osobní údaje", {"fields": ("first_name", "last_name", "email_verified")}),
        (
            "Oprávnění",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Důležité údaje", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            "Nový uživatel",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
