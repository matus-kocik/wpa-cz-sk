from datetime import date

import requests
from django import forms
from django.conf import settings
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .validators import (
    validate_academic_title,
    validate_birth_date,
    validate_email_domain,
    validate_house_number,
    validate_human_name,
    validate_location_name,
    validate_message_body,
    validate_notes,
    validate_phone_number,
    validate_plain_text,
    validate_postal_code,
    validate_street,
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


class MembershipApplicationForm(forms.Form):
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
    academic_title = forms.CharField(
        label="Titul",
        max_length=48,
        required=False,
        validators=[validate_academic_title, validate_plain_text],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "48",
                "autocomplete": "off",
                "placeholder": "např. Mgr.",
                "title": "Pouze písmena, tečky a mezery (např. Ing., Ph.D.)",
                "aria-describedby": "academic-title-error",
            }
        ),
    )
    birth_date = forms.DateField(
        label="Datum narození",
        validators=[validate_birth_date],
        widget=forms.DateInput(
            attrs={
                **input_style,
                "autocomplete": "bday",
                "type": "date",
                "title": "Vyberte platný datum narození. Musíte mít alespoň 18 let.",
                "aria-describedby": "birth-date-error",
            }
        ),
        required=True,
    )

    city = forms.CharField(
        label="Město/Obec",
        max_length=64,
        validators=[validate_location_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "64",
                "autocomplete": "address-level2",
                "placeholder": "např. Brno",
                "title": "Pouze písmena, mezery, pomlčky nebo apostrof",
                "aria-describedby": "city-error",
            }
        ),
    )
    street = forms.CharField(
        label="Ulice",
        max_length=128,
        validators=[validate_street],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "128",
                "autocomplete": "address-line1",
                "placeholder": "např. 1. máje",
                "title": "Ulice může obsahovat písmena, čísla, mezery, pomlčky, tečky a lomítka.",
                "aria-describedby": "street-error",
            }
        ),
    )
    house_number = forms.CharField(
        label="Číslo domu",
        max_length=32,
        validators=[validate_house_number],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "32",
                "autocomplete": "address-line2",
                "placeholder": "např. 1, 12A nebo 12/4",
                "title": "Pouze čísla, písmena, mezery, lomítka a pomlčky.",
                "aria-describedby": "house-number-error",
            }
        ),
    )
    postal_code = forms.CharField(
        label="PSČ",
        max_length=10,
        validators=[validate_postal_code],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "10",
                "autocomplete": "postal-code",
                "placeholder": "např. 123 45",
                "title": "Zadejte platné PSČ – např. 12345 nebo 123 45",
                "aria-describedby": "postal-code-error",
            }
        ),
    )

    district = forms.CharField(
        label="Okres",
        max_length=64,
        validators=[validate_location_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "64",
                "autocomplete": "address-level1",
                "placeholder": "např. Brno-město",
                "title": "Pouze písmena, čísla, pomlčky a mezery",
                "aria-describedby": "district-error",
            }
        ),
    )

    country = CountryField(blank_label="(Zvolte stát)").formfield(
        label="Stát",
        widget=CountrySelectWidget(attrs=input_style),
    )
    phone_number = forms.CharField(
        label="Telefon",
        max_length=24,
        required=False,
        validators=[validate_phone_number],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "24",
                "autocomplete": "tel",
                "placeholder": "např. +420901234567",
                "title": "Zadejte telefonní číslo v mezinárodním formátu, např. +420123456789",
                "inputmode": "tel",
                "aria-describedby": "phone-number-error",
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

    notes = forms.CharField(
        label="Poznámky",
        max_length=256,
        required=False,
        validators=[validate_notes, validate_plain_text],
        widget=forms.Textarea(
            attrs={
                **input_style,
                "placeholder": "Zde můžete uvést další informace (max. 256 znaků)...",
                "rows": 5,
                "maxlength": 256,
                "title": "Nepovinné pole pro doplňující informace (max. 256 znaků)",
                "aria-describedby": "notes-error",
            }
        ),
    )

    declaration_place = forms.CharField(
        label="V",
        max_length=128,
        validators=[validate_location_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "128",
                "autocomplete": "off",
                "placeholder": "např. Praha",
                "title": "Zadejte město, kde byla přihláška podepsána",
                "aria-describedby": "declaration-place-error",
            }
        ),
    )

    declaration_date = forms.CharField(
        label="Dne",
        initial=date.today().strftime("%d.%m.%Y"),
        widget=forms.TextInput(
            attrs={
                **input_style,
                "readonly": "readonly",
            }
        ),
    )

    declaration_signature = forms.CharField(
        label="Podpis",
        max_length=128,
        validators=[validate_human_name],
        widget=forms.TextInput(
            attrs={
                **input_style,
                "maxlength": "128",
                "autocomplete": "off",
                "placeholder": "např. Jan Novák",
                "title": "Zadejte jméno a příjmení jako podpis",
                "aria-describedby": "declaration-signature-error",
            }
        ),
    )

    agree_membership_terms = forms.BooleanField(
        label="Souhlasím s podmínkami přihlášky a členství ve spolku WPA CZ-SK",
        required=True,
        error_messages={
            "required": "Musíte souhlasit s podmínkami přihlášky a členství."
        },
        widget=forms.CheckboxInput(
            attrs={"class": "form-checkbox rounded text-green-600 focus:ring-green-500"}
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
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        label="Nechejte prázdné",
    )
    turnstile = TurnstileField(required=True)

    def clean_honeypot(self):
        data = self.cleaned_data.get("honeypot")
        if data:
            raise forms.ValidationError("Zachycený spam – odeslání zablokováno.")
        return data
