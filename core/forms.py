import requests
from django import forms
from django.conf import settings

from .validators import (
    validate_email_domain,
    validate_human_name,
    validate_message_body,
    validate_plain_text,
    validate_subject,
)


class TurnstileField(forms.Field):
    def validate(self, value):
        super().validate(value)
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": settings.TURNSTILE_SECRET_KEY,
                "response": value,
            },
            timeout=5,
        ).json()
        if not response.get("success"):
            raise forms.ValidationError("Ověření proti spamu selhalo.")


class ContactForm(forms.Form):
    input_style = {
        "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
    }
    first_name = forms.CharField(
        label="Jméno",
        max_length=64,
        validators=[validate_human_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "64",
                "autocomplete": "given-name",
                "placeholder": "např. Jan",
                "title": "Pouze písmena, mezery, pomlčky nebo apostrof",
                "aria-describedby": "first-name-error",
            }
        ),
    )

    last_name = forms.CharField(
        label="Příjmení",
        max_length=64,
        validators=[validate_human_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "64",
                "autocomplete": "family-name",
                "placeholder": "např. Novák",
                "title": "Pouze písmena, mezery, pomlčky nebo apostrof",
                "aria-describedby": "last-name-error",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        max_length=128,
        validators=[validate_email_domain],
        widget=forms.EmailInput(
            attrs={
                **input_style,
                "maxlength": "128",
                "autocomplete": "email",
                "placeholder": "např. jan.novak@example.com",
                "title": "Zadejte platnou e-mailovou adresu ve tvaru jméno@domena.cz",
                "aria-describedby": "email-error",
            }
        ),
    )

    subject = forms.CharField(
        label="Předmět",
        max_length=64,
        validators=[validate_subject, validate_plain_text],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "64",
                "autocomplete": "off",
                "placeholder": "např. Dotaz ohledně členství",
                "title": "Stručně popište, čeho se zpráva týká",
                "aria-describedby": "subject-error",
            }
        ),
    )

    message_body = forms.CharField(
        label="Zpráva",
        max_length=512,
        validators=[validate_message_body, validate_plain_text],
        widget=forms.Textarea(
            attrs={
                **input_style,
                "maxlength": "512",
                "autocomplete": "off",
                "placeholder": "např. Dobrý den, rád bych se zeptal na...",
                "title": "Napište svou zprávu, dotaz nebo vzkaz.",
                "rows": 5,
                "aria-describedby": "message_body-error",
            }
        ),
    )
    agree_gdpr = forms.BooleanField(
        label="Souhlasím se zpracováním osobních údajů",
        required=True,
        error_messages={
            "required": "Pro pokračování musíte souhlasit se zpracováním údajů."
        },
        widget=forms.CheckboxInput(
            attrs={"class": "form-checkbox rounded text-green-600 focus:ring-green-500"}
        ),
    )

    honeypot = forms.CharField(required=False, widget=forms.HiddenInput, label="")

    turnstile = TurnstileField(required=True)

    def clean_honeypot(self):
        value = self.cleaned_data.get("honeypot")
        if value:
            raise forms.ValidationError("Neplatný pokus o odeslání formuláře.")
        return value
