from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700",
            "placeholder": "vas@email.cz",
        })
    )

    password = forms.CharField(
        label="Heslo",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700",
            "placeholder": "••••••••",
        })
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700",
            "placeholder": "vas@email.cz",
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Nové heslo",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700",
            "placeholder": "••••••••",
        })
    )

    new_password2 = forms.CharField(
        label="Potvrzení hesla",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-700",
            "placeholder": "••••••••",
        })
    )
