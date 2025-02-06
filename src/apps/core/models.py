from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.utils import timezone

# TODO: Este je tu vela prace, ktora sa bude prisposobovat podla potrieb projektu,
# najma SeoModel, ... neskor to vysperkovat...zaklad je fajn...


class SoftDeleteManager(models.Manager):
    """
    Custom manager that filters out soft-deleted objects by default.

    When using `MyModel.objects.all()`, it will only return objects
    that are NOT deleted.
    If you need to access all objects (including deleted ones),
    use `MyModel.all_objects.all()`.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class TimeStampedModel(models.Model):
    """
    Abstract model that provides automatic timestamp fields.

    Fields:
    - `created_at`: Stores the datetime when the object was created.
    - `updated_at`: Updates automatically when the object is modified.
    - `deleted_at`: Stores the datetime when the object was soft-deleted (optional).

    This model is abstract and cannot be used directly.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Created At",
        help_text="Date and time when the object was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Date and time when the object was last updated.",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Deleted At",
        help_text="Date and time when the object was deleted (soft delete).",
    )
    # Use SoftDeleteManager by default to hide deleted objects
    objects = SoftDeleteManager()
    all_objects = (
        models.Manager()
    )  # Allows access to ALL objects, including deleted ones

    def soft_delete(self):
        """Marks the object as deleted instead of removing it from DB."""
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restores a soft-deleted object by setting `deleted_at` to None."""
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True  # Ensures this model is not used to create database tables


class SeoModel(models.Model):
    """
    Abstract model that provides SEO-related fields and methods.

    - SEO metadata (title, description, keywords)
    - Open Graph (Facebook & social media preview metadata)
    - Twitter metadata (Twitter card preview fields)
    - Automatic SEO title & description generation from existing fields
    """

    # Basic SEO fields
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="SEO Title",
        help_text="SEO meta title for the object.",
    )
    seo_description = models.TextField(
        blank=True,
        verbose_name="SEO Description",
        help_text="SEO meta description for the object.",
    )
    seo_keywords = models.TextField(
        blank=True,
        verbose_name="SEO Keywords",
        help_text="SEO meta keywords for the object.",
    )

    # Open Graph fields (Facebook, LinkedIn, etc.)
    og_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Open Graph Title",
        help_text=(
            "Open Graph title for the object. "
            "Title for Facebook and other social media."
        ),
    )
    og_description = models.TextField(
        blank=True,
        verbose_name="Open Graph Description",
        help_text=(
            "Open Graph description for the object. "
            "Description for social media previews."
        ),
    )
    og_image = models.ImageField(
        upload_to="og_images/",
        blank=True,
        verbose_name="Open Graph Image",
        help_text=(
            "Open Graph image for the object. Image used in social media previews."
        ),
    )

    # Twitter metadata fields
    twitter_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Twitter Title",
        help_text="Title for Twitter preview cards.",
    )
    twitter_description = models.TextField(
        blank=True,
        verbose_name="Twitter Description",
        help_text="Description for Twitter preview cards.",
    )
    twitter_image = models.ImageField(
        upload_to="twitter_images/",
        blank=True,
        verbose_name="Twitter Image",
        help_text="Image for Twitter preview cards.",
    )

    class Meta:
        """Meta options for the model."""

        abstract = True  # This model cannot be created directly in the database.

    def get_seo_title(self):
        """
        Returns the best available title for SEO.
        If the SEO title is not set, it generates one from other fields.
        If no valid title exists, returns an empty string.
        """
        possible_titles = ["seo_title", "title", "name", "heading", "label", "og_title"]
        return next(
            (
                getattr(self, field, "").strip()
                for field in possible_titles
                if getattr(self, field, "").strip()
            ),
            "",  # Default empty string if nothing is found
        )[
            :64
        ]  # Limit to 64 characters

    def get_seo_description(self):
        """
        Returns the best available description for SEO.
        If the SEO description is not set, it generates one from other fields.
        If no valid description exists, returns an empty string.
        """
        possible_descriptions = [
            "seo_description",
            "description",
            "content",
            "text",
            "body",
            "summary",
            "information",
            "info",
        ]
        return next(
            (
                getattr(self, field, "").strip()
                for field in possible_descriptions
                if getattr(self, field, "").strip()
            ),
            "",  # Default empty string if nothing is found
        )

    def get_seo_keywords(self):
        """
        Returns the best available keywords for SEO.
        If the SEO keywords are not set, it generates them from other fields.
        If no valid keywords exist, returns an empty string.
        """
        possible_keywords = ["seo_keywords", "keywords", "tags"]
        return next(
            (
                getattr(self, field, "").strip()
                for field in possible_keywords
                if getattr(self, field, "").strip()
            ),
            "",  # Default empty string if nothing is found
        )

    def get_og_image(self):
        """
        Returns the Open Graph image.

        - If `og_image` exists, returns its URL.
        - Otherwise, returns the default image from Django settings.
        """
        if self.og_image:
            return urljoin(settings.MEDIA_URL, self.og_image.name)
        return getattr(
            settings, "DEFAULT_OG_IMAGE", "/static/images/default_og.jpg"
        )  # Default image URL from Django settings

    def get_twitter_image(self):
        """
        Returns the Twitter image.

        - If `twitter_image` exists, returns its URL.
        - Otherwise, returns the default image from Django settings.
        """
        if self.twitter_image:
            return urljoin(settings.MEDIA_URL, self.twitter_image.name)
        return getattr(
            settings, "DEFAULT_TWITTER_IMAGE", "/static/images/default_twitter.jpg"
        )  # Default image URL from Django settings

    def save(self, *args, **kwargs):
        """
        Ensures that SEO fields are set before saving.

        - If `seo_title` is missing, it is generated automatically.
        - If `seo_description` is missing, it is generated automatically.
        - The same logic applies to Open Graph and Twitter metadata.
        """

        seo_title = self.get_seo_title()
        seo_description = self.get_seo_description()

        self.seo_title = self.seo_title or seo_title
        self.seo_description = self.seo_description or seo_description
        self.seo_keywords = self.seo_keywords or self.get_seo_keywords()

        self.og_title = self.og_title or seo_title
        self.og_description = self.og_description or seo_description
        self.twitter_title = self.twitter_title or seo_title
        self.twitter_description = self.twitter_description or seo_description

        super().save(*args, **kwargs)
