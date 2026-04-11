"""
Common abstract models and utilities shared across the project.

Includes:
- TimeStampedModel: created/updated timestamps
- SlugModel: automatic unique slug generation
- SEOModel: basic SEO fields
- SoftDeleteModel: soft deletion support with managers
- PublishableModel: publication state handling
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created and updated timestamps.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Vytvořeno",
        help_text="Datum a čas vytvoření záznamu",
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Upraveno",
        help_text="Datum a čas poslední úpravy",
    )

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """
    Abstract model that provides an auto-generated unique slug field.
    """
    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug",
        help_text="URL identifikátor (automaticky generovaný pokud není vyplněn)",
    )

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        # Automatically generate slug from available name-like fields
        if not self.slug:
            source = None

            if hasattr(self, "title") and self.title:
                source = self.title
            elif hasattr(self, "latin_name") and self.latin_name:
                source = self.latin_name
            elif hasattr(self, "name") and self.name:
                source = self.name

            # ensure source is not empty or whitespace
            if source and str(source).strip():
                base_slug = slugify(source)
                slug = base_slug
                counter = 1

                ModelClass = self.__class__
                while ModelClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                self.slug = slug

        super().save(*args, **kwargs)


class SEOModel(models.Model):
    """
    Abstract model providing basic SEO metadata fields.
    """
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta titulek",
        help_text="Titulek pro SEO (HTML <title>)",
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name="Meta popis",
        help_text="Krátký popis pro vyhledávače",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Meta klíčová slova",
        help_text="Klíčová slova oddělená čárkou",
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted records by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    Abstract model implementing soft delete functionality.
    """
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Smazáno",
        help_text="Označuje záznam jako soft smazaný",
    )
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Smazáno dne",
        help_text="Datum a čas soft smazání",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    # Soft delete by default, hard delete only if explicitly requested
    def delete(self, hard=False, *args, **kwargs):
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()


class PublishableModel(models.Model):
    """
    Abstract model handling publication state and timestamps.
    """
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Publikováno",
        help_text="Určuje, zda je záznam veřejně viditelný",
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Publikováno dne",
        help_text="Datum a čas publikace",
    )

    class Meta:
        abstract = True

    # Automatically set published_at when publishing for the first time
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
