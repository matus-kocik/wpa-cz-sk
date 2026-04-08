from django.core.exceptions import ValidationError
from django.db import models

from common.models import (
    PublishableModel,
    SEOModel,
    SlugModel,
    TimeStampedModel,
)


class Category(SlugModel):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorie"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Contributor(models.Model):
    ROLE_CHOICES = (
        ("author", "Autor"),
        ("photographer", "Fotograf"),
        ("translator", "Překladatel"),
        ("other", "Jiné"),
    )

    name = models.CharField(max_length=150, blank=True)
    member = models.ForeignKey(
        "members.MemberProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contributions",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

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
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
        db_index=True
    )

    summary = models.TextField(blank=True)

    pdf_file = models.FileField(upload_to="articles/pdf/", blank=True, null=True)

    pdf_title = models.CharField(max_length=255, blank=True)

    main_image = models.ImageField(
        upload_to="articles/images/",
        blank=True,
        null=True
    )


    contributors = models.ManyToManyField(
        Contributor,
        blank=True,
        related_name="articles"
    )
    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="articles"
    )
    related_articles = models.ManyToManyField(
        "self",
        blank=True
    )
    publication_date = models.DateField(db_index=True)

    published_in = models.CharField(max_length=255, blank=True)
    published_in_date = models.DateField(blank=True, null=True)
    published_in_url = models.URLField(blank=True)

    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-publication_date"]
        verbose_name = "Článek"
        verbose_name_plural = "Články"

    def __str__(self):
        return self.title
