from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    slug = models.SlugField(unique=True, blank=True, db_index=True)

    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
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
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, hard=False, *args, **kwargs):
        if hard:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
