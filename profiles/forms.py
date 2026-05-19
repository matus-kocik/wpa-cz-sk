from django import forms
from django.forms import inlineformset_factory

from .models import ProfileGallery, ProfileVideo, PublicProfile

INPUT_CLASS = "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600"
TEXTAREA_CLASS = INPUT_CLASS + " min-h-[140px]"
CHECKBOX_CLASS = "h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500"


class PublicProfileForm(forms.ModelForm):
    class Meta:
        model = PublicProfile
        fields = [
            "display_name",
            "bio",
            "avatar",
            "species",
            "other_species",
            "public_email",
            "phone",
            "website",
            "facebook_url",
            "instagram_url",
            "youtube_url",
            "additional_info",
            "is_public",
            "show_email",
            "show_phone",
            "show_location",
            "show_website",
            "show_social",
            "show_bio",
            "show_gallery",
            "show_videos",
            "show_avatar",
            "show_species",
            "show_other_species",
            "show_additional_info",
        ]

        labels = {
            "display_name": "Zobrazované jméno",
            "bio": "O mně",
            "avatar": "Profilová fotka",
            "species": "Chované druhy",
            "other_species": "Další druhy",
            "public_email": "E-mail",
            "phone": "Telefon",
            "website": "Web",
            "facebook_url": "Facebook",
            "instagram_url": "Instagram",
            "youtube_url": "YouTube",
            "additional_info": "Další informace",

            # visibility labels
            "is_public": "Profil je veřejný",
            "show_email": "Veřejně zobrazit e-mail",
            "show_phone": "Veřejně zobrazit telefon",
            "show_location": "Veřejně zobrazit lokalitu",
            "show_website": "Veřejně zobrazit web",
            "show_social": "Veřejně zobrazit sociální sítě",
            "show_bio": "Veřejně zobrazit bio",
            "show_gallery": "Veřejně zobrazit galerii",
            "show_videos": "Veřejně zobrazit videa",
            "show_avatar": "Veřejně zobrazit profilovou fotku",
            "show_species": "Veřejně zobrazit chované druhy",
            "show_other_species": "Veřejně zobrazit další druhy",
            "show_additional_info": "Veřejně zobrazit další informace",
        }

        help_texts = {
            "public_email": "Pokud není zveřejněno, uvidí e-mail pouze přihlášení členové.",
            "phone": "Pokud není zveřejněno, uvidí telefon pouze přihlášení členové.",
            "website": "Odkaz na vaše webové stránky.",
            "facebook_url": "Odkaz na váš Facebook profil.",
            "instagram_url": "Odkaz na váš Instagram profil.",
            "youtube_url": "Odkaz na YouTube kanál nebo video.",

            # visibility explanation
            "is_public": "Pokud vypnete, profil nebude veřejně dostupný.",
            "show_email": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_phone": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_location": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_website": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_social": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_bio": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_gallery": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_videos": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_avatar": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_species": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_other_species": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
            "show_additional_info": "Nezaškrtnuté = viditelné pouze pro přihlášené členy.",
        }

        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Zobrazované jméno"
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "Informace o chovateli..."
                }
            ),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": INPUT_CLASS
                }
            ),
            "species": forms.SelectMultiple(
                attrs={
                    "class": INPUT_CLASS
                }
            ),
            "other_species": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Další druhy (např. papoušci, holubi...)"
                }
            ),
            "public_email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Veřejný e-mail"
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "+420..."
                }
            ),
            "website": forms.URLInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "https://..."
                }
            ),
            "facebook_url": forms.URLInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Facebook profil"
                }
            ),
            "instagram_url": forms.URLInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Instagram profil"
                }
            ),
            "youtube_url": forms.URLInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "YouTube kanál nebo video"
                }
            ),
            "additional_info": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "rows": 4,
                    "placeholder": "Další informace o chovu..."
                }
            ),

            # CHECKBOXES
            "is_public": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_email": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_phone": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_location": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_website": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_social": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_bio": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_gallery": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_videos": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_avatar": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_species": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_other_species": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "show_additional_info": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
        }


# =========================
# Custom ModelForms for Gallery and Video with proper widgets
# =========================

class ProfileGalleryForm(forms.ModelForm):
    class Meta:
        model = ProfileGallery
        fields = ["image", "caption"]
        widgets = {
            "image": forms.FileInput(attrs={"class": INPUT_CLASS}),
            "caption": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Popis obrázku"
            }),
        }


class ProfileVideoForm(forms.ModelForm):
    class Meta:
        model = ProfileVideo
        fields = ["url", "title"]
        widgets = {
            "url": forms.URLInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "https://youtube.com/..."
            }),
            "title": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Název videa"
            }),
        }


# =========================
# Inline formsets
# =========================

GalleryFormSet = inlineformset_factory(
    PublicProfile,
    ProfileGallery,
    form=ProfileGalleryForm,
    extra=6,
    max_num=6,
    can_delete=True,
    validate_max=True
)

VideoFormSet = inlineformset_factory(
    PublicProfile,
    ProfileVideo,
    form=ProfileVideoForm,
    extra=3,
    max_num=3,
    can_delete=True,
    validate_max=True
)
