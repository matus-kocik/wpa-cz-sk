"""
Articles app models.

Provides categories, contributors, and articles with SEO and publishing support.
"""

from django.core.exceptions import ValidationError
from django.db import models

from common.models import (
    PublishableModel,
    SEOModel,
    SlugModel,
    TimeStampedModel,
)


class Category(SlugModel):
    """
    Article category used for grouping and ordering in listings.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Název",
        help_text="Název kategorie",
        db_index=True,
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Pořadí",
        help_text="Pořadí zobrazení (nižší = dříve)",
        db_index=True,
    )

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorie"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Contributor(models.Model):
    """
    Contributor to an article.

    Can be linked to a member or defined by name.
    """
    ROLE_CHOICES = (
        ("author", "Autor"),
        ("photographer", "Fotograf"),
        ("translator", "Překladatel"),
        ("other", "Jiné"),
    )

    name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Jméno",
        help_text="Jméno přispěvatele (pokud není člen)",
        db_index=True,
    )
    member = models.ForeignKey(
        "members.MemberProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contributions",
        verbose_name="Člen",
        help_text="Odkaz na člena, pokud je přispěvatelem",
        db_index=True,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="Role",
        help_text="Role přispěvatele u článku",
        db_index=True,
    )

    # Ensure at least one of member or name is provided
    def clean(self):
        if not self.member and not self.name:
            raise ValidationError("Musí být vyplněno jméno nebo člen.")

    class Meta:
        verbose_name = "Přispěvatel"
        verbose_name_plural = "Přispěvatelé"

    def __str__(self):
        if self.member:
            return f"{self.member} ({self.get_role_display()})"
        return f"{self.name} ({self.get_role_display()})"


class Article(
    TimeStampedModel,
    SlugModel,
    SEOModel,
    PublishableModel,
):
    """
    Main article model.

    Supports SEO, publishing workflow, and relations to species and contributors.
    """
    title = models.CharField(
        max_length=200,
        verbose_name="Titulek",
        help_text="Název článku",
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
        db_index=True,
        help_text="Kategorie článku",
    )

    summary = models.TextField(
        blank=True,
        verbose_name="Shrnutí",
        help_text="Krátké shrnutí článku",
    )

    pdf_file = models.FileField(
        upload_to="articles/pdf/",
        blank=True,
        null=True,
        verbose_name="PDF soubor",
        help_text="Volitelný PDF soubor článku",
    )

    pdf_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Název PDF",
        help_text="Popis nebo název PDF souboru",
    )

    main_image = models.ImageField(
        upload_to="articles/images/",
        blank=True,
        null=True,
        verbose_name="Hlavní obrázek",
        help_text="Hlavní ilustrační obrázek článku",
    )


    contributors = models.ManyToManyField(
        Contributor,
        blank=True,
        related_name="articles",
        verbose_name="Přispěvatelé",
        help_text="Autoři, fotografové a další",
    )
    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="articles",
        verbose_name="Druhy",
        help_text="Související druhy",
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name="Související články",
        help_text="Další související obsah",
    )
    publication_date = models.DateField(
        db_index=True,
        verbose_name="Datum publikace",
        help_text="Datum publikace článku",
    )

    published_in = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Publikováno v",
        help_text="Název publikace nebo zdroje",
    )
    published_in_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum vydání",
        help_text="Datum vydání v externím zdroji",
    )
    published_in_url = models.URLField(
        blank=True,
        verbose_name="Odkaz na zdroj",
        help_text="Externí odkaz na publikovaný článek",
    )

    note = models.TextField(
        blank=True,
        verbose_name="Poznámka",
        help_text="Interní poznámka",
    )

    class Meta:
        ordering = ["-publication_date"]
        verbose_name = "Článek"
        verbose_name_plural = "Články"
        indexes = [
            models.Index(fields=["publication_date"]),
            models.Index(fields=["category"]),
        ]

    # Human-readable article title
    def __str__(self):
        return self.title
