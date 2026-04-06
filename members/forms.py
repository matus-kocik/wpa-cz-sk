from datetime import date

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from core.forms import TurnstileField
from core.validators import (
    validate_academic_title,
    validate_birth_date,
    validate_email_domain,
    validate_house_number,
    validate_human_name,
    validate_location_name,
    validate_notes,
    validate_phone_number,
    validate_plain_text,
    validate_postal_code,
    validate_street,
)

from .models import MembershipApplication


class MembershipApplicationForm(forms.ModelForm):
    input_style = {
        "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
    }

    first_name = forms.CharField(
        label="Jméno",
        max_length=64,
        validators=[validate_human_name],
        widget=forms.TextInput(attrs={**input_style}),
    )

    last_name = forms.CharField(
        label="Příjmení",
        max_length=64,
        validators=[validate_human_name],
        widget=forms.TextInput(attrs={**input_style}),
    )

    academic_title = forms.CharField(
        label="Titul",
        max_length=48,
        required=False,
        validators=[validate_academic_title, validate_plain_text],
        widget=forms.TextInput(attrs={**input_style}),
    )

    birth_date = forms.DateField(
        label="Datum narození",
        validators=[validate_birth_date],
        widget=forms.DateInput(attrs={**input_style, "type": "date"}),
    )

    city = forms.CharField(
        label="Město/Obec",
        max_length=64,
        validators=[validate_location_name],
        widget=forms.TextInput(attrs={**input_style}),
    )

    street = forms.CharField(
        label="Ulice",
        max_length=128,
        validators=[validate_street],
        widget=forms.TextInput(attrs={**input_style}),
    )

    house_number = forms.CharField(
        label="Číslo domu",
        max_length=32,
        validators=[validate_house_number],
        widget=forms.TextInput(attrs={**input_style}),
    )

    postal_code = forms.CharField(
        label="PSČ",
        max_length=10,
        validators=[validate_postal_code],
        widget=forms.TextInput(attrs={**input_style}),
    )

    district = forms.CharField(
        label="Okres",
        max_length=64,
        validators=[validate_location_name],
        widget=forms.TextInput(attrs={**input_style}),
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
        widget=forms.TextInput(attrs={**input_style}),
    )

    email = forms.EmailField(
        label="Email",
        max_length=128,
        validators=[validate_email_domain],
        widget=forms.EmailInput(attrs={**input_style}),
    )

    notes = forms.CharField(
        label="Poznámky",
        max_length=256,
        required=False,
        validators=[validate_notes, validate_plain_text],
        widget=forms.Textarea(attrs={**input_style}),
    )

    declaration_place = forms.CharField(
        label="V",
        max_length=128,
        validators=[validate_location_name],
        widget=forms.TextInput(attrs={**input_style}),
    )

    declaration_date = forms.DateField(
        label="Dne",
        input_formats=["%d.%m.%Y", "%Y-%m-%d"],
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
        widget=forms.TextInput(attrs={**input_style}),
    )

    agree_membership_terms = forms.BooleanField(required=True)
    agree_gdpr = forms.BooleanField(required=True)

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "hidden"}),
        label=""
    )
    turnstile = TurnstileField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["declaration_date"].initial = date.today()

    def clean_website(self):
        data = self.cleaned_data.get("website")
        if data:
            raise forms.ValidationError("Zachycený spam – odeslání zablokováno.")
        return data

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email:
            email = email.strip().lower()

            if MembershipApplication.objects.filter(
                email__iexact=email,
                status__in=["pending", "approved"],
            ).exists():
                raise forms.ValidationError("Tento email už má aktivní přihlášku.")

        return email

    class Meta:
        model = MembershipApplication
        fields = [
            "first_name",
            "last_name",
            "academic_title",
            "birth_date",
            "city",
            "street",
            "house_number",
            "postal_code",
            "district",
            "country",
            "phone_number",
            "email",
            "notes",
            "declaration_place",
            "declaration_date",
            "declaration_signature",
        ]
