from django.db import models

from common.models import SEOModel, TimeStampedModel


class Event(SEOModel, TimeStampedModel):
    """
    Represents an event or activity within WPA sections.

    Includes scheduling, location, related species, and visibility settings.
    """
    SECTION_CHOICES = (
        ("cz_sk", "WPA CZ-SK"),
        ("de", "WPA Deutschland"),
        ("uk", "WPA UK"),
        ("at", "WPA Austria"),
        ("benelux", "WPA Benelux"),
        ("fr", "WPA France"),
        ("other", "Jiná sekce"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Název akce",
        help_text="Název události nebo akce.",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="Unikátní URL identifikátor události.",
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        verbose_name="Popis",
        help_text="Detailní popis události.",
    )

    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES,
        default="cz_sk",
        db_index=True,
        verbose_name="Sekce WPA",
        help_text="Sekce WPA, ze které událost pochází.",
    )

    start_date = models.DateTimeField(
        verbose_name="Začátek",
        help_text="Datum a čas začátku události.",
        db_index=True,
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Konec",
        help_text="Datum a čas ukončení události.",
        db_index=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Místo",
        help_text="Místo konání události.",
        db_index=True,
    )
    organizer = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Organizátor",
        help_text="Organizátor nebo pořadatel události.",
        db_index=True,
    )

    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="events",
        verbose_name="Související druhy",
        help_text="Druhy, kterých se událost týká.",
    )

    is_external = models.BooleanField(
        default=False,
        verbose_name="Externí",
        help_text="Určuje, zda je událost převzatá z jiné WPA sekce.",
    )
    source_url = models.URLField(
        blank=True,
        verbose_name="Zdrojová URL",
        help_text="Odkaz na originální stránku události.",
    )
    external_url = models.URLField(
        blank=True,
        verbose_name="Externí odkaz",
        help_text="Odkaz na registraci nebo detail akce.",
    )

    itinerary = models.TextField(
        blank=True,
        verbose_name="Program / itinerář",
        help_text="Detailní program události, harmonogram nebo plán průběhu.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky k události.",
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name="Veřejná",
        help_text="Určuje, zda se má událost zobrazit veřejně.",
        db_index=True,
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Doporučená",
        help_text="Zvýrazněná událost, například na homepage.",
        db_index=True,
    )

    class Meta:
        verbose_name = "Událost"
        verbose_name_plural = "Události"
        ordering = ["start_date"]
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["section"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_featured"]),
        ]

    # Human-readable event title
    def __str__(self):
        return self.title
