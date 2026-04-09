from django.db import models

from common.models import SEOModel, SlugModel, TimeStampedModel


class Family(SlugModel):
    name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Čeľaď"
        verbose_name_plural = "Čeľade"
        ordering = ["latin_name"]

    def __str__(self):
        return self.latin_name


class Genus(SlugModel):
    name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="genera"
    )

    class Meta:
        verbose_name = "Rod"
        verbose_name_plural = "Rody"
        ordering = ["latin_name"]

    def __str__(self):
        return self.latin_name


class Species(TimeStampedModel, SEOModel, SlugModel):
    genus = models.ForeignKey(
        Genus,
        on_delete=models.CASCADE,
        related_name="species"
    )

    latin_name = models.CharField(max_length=150)
    czech_name = models.CharField(max_length=150)
    authority = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    subspecies_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    distribution = models.TextField(blank=True)
    habitat = models.TextField(blank=True)

    CONSERVATION_CHOICES = [
        ("LC", "Málo dotknutý"),
        ("NT", "Takmer ohrozený"),
        ("VU", "Zraniteľný"),
        ("EN", "Ohrozený"),
        ("CR", "Kriticky ohrozený"),
    ]

    status_in_nature = models.CharField(
        max_length=10,
        choices=CONSERVATION_CHOICES,
        blank=True
    )

    status_in_captivity = models.TextField(blank=True)

    maturity = models.CharField(max_length=50, blank=True)
    length = models.CharField(max_length=50, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    clutch = models.CharField(max_length=50, blank=True)
    incubation = models.CharField(max_length=50, blank=True)

    ring_size = models.FloatField(blank=True, null=True)
    population = models.TextField(blank=True)
    breeding_difficulty = models.TextField(blank=True)

    main_image = models.ImageField(
        upload_to="taxonomy/species/",
        blank=True,
        null=True
    )

    secondary_image = models.ImageField(
        upload_to="taxonomy/species/",
        blank=True,
        null=True
    )

    videos = models.TextField(blank=True)  # YouTube links (1 per line)
    images_url = models.URLField(blank=True)  # FB album

    class Meta:
        verbose_name = "Druh"
        verbose_name_plural = "Druhy"
        ordering = ["latin_name"]

    def __str__(self):
        return self.latin_name


class Subspecies(models.Model):
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="subspecies"
    )

    latin_name = models.CharField(max_length=150)
    note = models.TextField(blank=True)

    # optional override (future)
    length = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Poddruh"
        verbose_name_plural = "Poddruhy"
        ordering = ["latin_name"]

    def __str__(self):
        return self.latin_name
