from django.core.validators import MinLengthValidator
from django.db import models

from common.models import SlugModel, TimeStampedModel


class PublicProfile(TimeStampedModel, SlugModel):
    """
    Public-facing profile of a member.

    Contains contact info, breeding focus, and visibility settings.
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
    display_name = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Zobrazované jméno",
        help_text="Jméno zobrazené na veřejném profilu",
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Bio",
        help_text="Krátké představení chovatele",
    )
    avatar = models.ImageField(
        upload_to="profiles/avatars/",
        blank=True,
        null=True,
        verbose_name="Profilová fotka",
        help_text="Nahraná profilová fotografie",
    )
    location = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Lokalita",
        help_text="Město nebo oblast",
    )
    public_email = models.EmailField(
        blank=True,
        db_index=True,
        verbose_name="Veřejný e-mail",
        help_text="E-mail zobrazený na profilu",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        validators=[MinLengthValidator(7)],
        verbose_name="Telefon",
        help_text="Telefonní číslo v mezinárodním formátu",
    )
    website = models.URLField(
        blank=True,
        verbose_name="Web",
        help_text="Odkaz na webové stránky",
    )
    specialization = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Specializace",
        help_text="Na co se chovatel zaměřuje",
    )
    breeding_focus = models.TextField(
        blank=True,
        verbose_name="Chovatelské zaměření",
        help_text="Detailní popis chovu",
    )
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Roky zkušeností",
        help_text="Počet let zkušeností s chovem",
    )
    facebook_url = models.URLField(
        blank=True,
        verbose_name="Facebook",
        help_text="Odkaz na Facebook profil",
    )
    youtube_url = models.URLField(
        blank=True,
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
    show_breeding = models.BooleanField(
        default=True,
        verbose_name="Zobrazit chov",
        help_text="Zobrazit chovatelské informace",
    )

    # extra
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky (neveřejné)",
    )

    class Meta:
        verbose_name = "Veřejný profil"
        verbose_name_plural = "Veřejné profily"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["display_name"]),
            models.Index(fields=["location"]),
            models.Index(fields=["is_public"]),
        ]

    # Display name fallback to member string representation
    def __str__(self):
        return self.display_name or str(self.member)
