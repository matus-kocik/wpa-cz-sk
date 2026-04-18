from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from common.models import SlugModel, TimeStampedModel


class PublicProfile(TimeStampedModel, SlugModel):
    """
    Public-facing profile of a member.

    Contains contact info, breeding data, and visibility settings.
    """
    member = models.OneToOneField(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="public_profile",
        verbose_name="Člen",
        help_text="Vazba na členský profil"
    )
    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="public_profiles",
        verbose_name="Chované druhy",
        help_text="Druhy, které člen chová"
    )

    other_species = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Další druhy",
        help_text="Např. papoušci, holubi apod.",
    )


    display_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Zobrazované jméno",
        help_text="Jméno zobrazené na veřejném profilu",
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="O chovateli",
        help_text="Informace o chovateli (zobrazené na veřejném profilu)",
    )
    avatar = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
        verbose_name="Profilová fotka",
        help_text="Nahraná profilová fotografie",
    )
    public_email = models.EmailField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Veřejný e-mail",
        help_text="E-mail zobrazený na profilu",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[MinLengthValidator(7)],
        verbose_name="Telefon",
        help_text="Telefonní číslo v mezinárodním formátu",
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Web",
        help_text="Odkaz na webové stránky",
    )
    facebook_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Facebook",
        help_text="Odkaz na Facebook profil",
    )
    instagram_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Instagram",
        help_text="Odkaz na Instagram profil",
    )
    youtube_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="YouTube",
        help_text="Odkaz na YouTube kanál",
    )

    # visibility
    is_public = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Veřejný profil",
        help_text="Zda je profil veřejně viditelný",
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name="Zobrazit e-mail",
        help_text="Zobrazit e-mail na profilu",
    )
    show_phone = models.BooleanField(
        default=False,
        verbose_name="Zobrazit telefon",
        help_text="Zobrazit telefon na profilu",
    )
    show_location = models.BooleanField(
        default=True,
        verbose_name="Zobrazit lokalitu",
        help_text="Zobrazit lokalitu",
    )
    show_website = models.BooleanField(
        default=False,
        verbose_name="Zobrazit web",
        help_text="Zobrazit web na profilu",
    )
    show_social = models.BooleanField(
        default=True,
        verbose_name="Zobrazit sociální sítě",
        help_text="Zobrazit odkazy na sociální sítě",
    )
    show_bio = models.BooleanField(
        default=True,
        verbose_name="Zobrazit bio",
        help_text="Zobrazit bio na profilu",
    )
    show_gallery = models.BooleanField(
        default=True,
        verbose_name="Zobrazit galerii",
        help_text="Zobrazit galerii na profilu",
    )
    show_videos = models.BooleanField(
        default=True,
        verbose_name="Zobrazit videa",
        help_text="Zobrazit videa na profilu",
    )
    show_avatar = models.BooleanField(
        default=True,
        verbose_name="Zobrazit avatar",
        help_text="Zobrazit profilovou fotku",
    )
    show_species = models.BooleanField(
        default=True,
        verbose_name="Zobrazit druhy",
        help_text="Zobrazit chované druhy",
    )
    show_other_species = models.BooleanField(
        default=True,
        verbose_name="Zobrazit další druhy",
        help_text="Zobrazit pole 'další druhy'",
    )

    # extra
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky (neveřejné)",
    )
    additional_info = models.TextField(
        blank=True,
        null=True,
        verbose_name="Doplňující informace",
        help_text="Další informace o chovu, zkušenosti, poznámky apod.",
    )
    show_additional_info = models.BooleanField(
        default=True,
        verbose_name="Zobrazit doplňující informace",
        help_text="Zobrazit sekci doplňujících informací",
    )

    def clean(self):
        # Normalize string fields (strip whitespace, convert empty to None)
        fields_to_clean = [
            "display_name",
            "bio",
            "public_email",
            "phone",
            "website",
            "facebook_url",
            "instagram_url",
            "youtube_url",
            "other_species",
        ]

        for field in fields_to_clean:
            value = getattr(self, field, None)
            if isinstance(value, str):
                value = value.strip()
                setattr(self, field, value or None)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug or self.slug.strip() == "":
            base_slug = slugify(
                f"{self.member.user.first_name}-{self.member.user.last_name}"
            )
            suffix = self.member.icch_number or self.member.id
            self.slug = f"{base_slug}-{suffix}"

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Veřejný profil"
        verbose_name_plural = "Veřejné profily"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["display_name"]),
            models.Index(fields=["is_public"]),
        ]

    @property
    def primary_species(self):
        return self.species.first()

    @property
    def additional_info_display(self):
        """
        Returns additional info for display.
        Priority:
        1. PublicProfile.additional_info
        2. MemberProfile.notes (fallback)
        """
        if self.additional_info:
            return self.additional_info

        member_notes = getattr(self.member, "notes", None)
        return member_notes or ""

    @property
    def location_display(self):
        """
        Returns formatted location from MemberProfile (city + country).
        Replaces deprecated `location` field.
        """
        city = getattr(self.member, "city", None)
        country = getattr(self.member, "country", None)

        if city and country:
            return f"{city}, {country}"
        return city or country or None


    # Display name fallback to member string representation
    def __str__(self):
        return self.display_name or str(self.member)



class ProfileVideo(models.Model):
    """
    YouTube videos related to a public profile.
    Allows multiple videos per user.
    """
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="Profil"
    )
    url = models.URLField(
        verbose_name="YouTube URL",
        help_text="Odkaz na YouTube video nebo kanál"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Název",
        help_text="Volitelný název videa"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videa"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.url


# Gallery images for a public profile.
# Allows multiple photos per user.
class ProfileGallery(models.Model):
    """
    Gallery items (photos) for a public profile.
    Allows multiple photos per user.
    """
    profile = models.ForeignKey(
        PublicProfile,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name="Profil"
    )
    image = models.ImageField(
        upload_to="profiles/gallery/",
        verbose_name="Obrázek"
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Popis",
        help_text="Volitelný popis fotografie"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fotografie"
        verbose_name_plural = "Galerie"
        ordering = ["-created_at"]

    def __str__(self):
        return self.caption or f"Gallery image {self.id}"
