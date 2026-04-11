"""
Taxonomy models.

Defines biological hierarchy (Family → Genus → Species → Subspecies)
and stores descriptive data used across the project.
"""

from django.db import models

from common.models import SEOModel, SlugModel, TimeStampedModel


class Family(SlugModel):
    """
    Biological family grouping multiple genera.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Název",
        help_text="Název čeledi",
        db_index=True,
    )
    latin_name = models.CharField(
        max_length=100,
        verbose_name="Latinský název",
        help_text="Latinský název čeledi",
        db_index=True,
    )

    class Meta:
        verbose_name = "Čeľaď"
        verbose_name_plural = "Čeľade"
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name"]),
        ]

    def __str__(self):
        return self.latin_name


class Genus(SlugModel):
    """
    Biological genus belonging to a family.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Název",
        help_text="Název rodu",
        db_index=True,
    )
    latin_name = models.CharField(
        max_length=100,
        verbose_name="Latinský název",
        help_text="Latinský název rodu",
        db_index=True,
    )

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="genera",
        verbose_name="Čeľaď",
        help_text="Nadřazená čeľaď",
        db_index=True,
    )

    class Meta:
        verbose_name = "Rod"
        verbose_name_plural = "Rody"
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name"]),
            models.Index(fields=["family"]),
        ]

    def __str__(self):
        return self.latin_name


class Species(TimeStampedModel, SEOModel, SlugModel):
    """
    Represents a species with taxonomy, biology, and breeding data.
    """
    genus = models.ForeignKey(
        Genus,
        on_delete=models.CASCADE,
        related_name="species",
        verbose_name="Rod",
        help_text="Rod, do kterého druh patří",
        db_index=True,
    )

    latin_name = models.CharField(
        max_length=150,
        verbose_name="Latinský název",
        help_text="Latinský název druhu",
        db_index=True,
    )
    czech_name = models.CharField(
        max_length=150,
        verbose_name="Český název",
        help_text="Český název druhu",
        db_index=True,
    )
    authority = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Autor",
        help_text="Autor vědeckého názvu",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Aktivní",
        help_text="Zda je druh aktivně používán",
    )

    subspecies_note = models.TextField(
        blank=True,
        verbose_name="Poznámka poddruhů",
        help_text="Poznámky k poddruhům",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Doplňující informace o druhu",
    )

    distribution = models.TextField(
        blank=True,
        verbose_name="Rozšíření",
        help_text="Geografické rozšíření druhu",
    )
    habitat = models.TextField(
        blank=True,
        verbose_name="Biotop",
        help_text="Typy biotopu, kde druh žije",
    )

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
        blank=True,
        verbose_name="Stav v přírodě",
        help_text="Ochranný status dle IUCN",
        db_index=True,
    )

    status_in_captivity = models.TextField(
        blank=True,
        verbose_name="Stav v zajetí",
        help_text="Informace o chovu v zajetí",
    )

    maturity = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Dospělost",
        help_text="Doba dosažení pohlavní dospělosti",
    )
    length = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Délka",
        help_text="Průměrná délka jedince",
    )
    weight = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Hmotnost",
        help_text="Průměrná hmotnost jedince",
    )
    clutch = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Snůška",
        help_text="Počet vajec ve snůšce",
    )
    incubation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Inkubační doba",
        help_text="Doba inkubace vajec",
    )

    ring_size = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Velikost kroužku",
        help_text="Velikost identifikačního kroužku v mm",
    )
    population = models.TextField(
        blank=True,
        verbose_name="Populace",
        help_text="Odhad populace",
    )
    breeding_difficulty = models.TextField(
        blank=True,
        verbose_name="Obtížnost chovu",
        help_text="Náročnost chovu",
    )

    main_image = models.ImageField(
        upload_to="taxonomy/species/",
        blank=True,
        null=True,
        verbose_name="Hlavní obrázek",
        help_text="Hlavní obrázek druhu",
    )

    secondary_image = models.ImageField(
        upload_to="taxonomy/species/",
        blank=True,
        null=True,
        verbose_name="Doplňkový obrázek",
        help_text="Doplňkový obrázek druhu",
    )

    videos = models.TextField(
        blank=True,
        verbose_name="Videa",
        help_text="YouTube odkazy (1 na řádek)",
    )  # YouTube links (1 per line)
    images_url = models.URLField(
        blank=True,
        verbose_name="URL obrázků",
        help_text="Odkaz na album na Facebooku",
    )  # FB album

    class Meta:
        verbose_name = "Druh"
        verbose_name_plural = "Druhy"
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name"]),
            models.Index(fields=["czech_name"]),
            models.Index(fields=["is_active"]),
        ]

    # Human-readable species name
    def __str__(self):
        return self.latin_name


class Subspecies(models.Model):
    """
    Represents a subspecies of a species.
    """
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="subspecies",
        verbose_name="Druh",
        help_text="Nadřazený druh",
        db_index=True,
    )

    latin_name = models.CharField(
        max_length=150,
        verbose_name="Latinský název",
        help_text="Latinský název poddruhu",
        db_index=True,
    )
    note = models.TextField(
        blank=True,
        verbose_name="Poznámka",
        help_text="Doplňující informace",
    )

    # optional override (future)
    length = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Délka",
        help_text="Specifická délka pro poddruh",
    )

    class Meta:
        verbose_name = "Poddruh"
        verbose_name_plural = "Poddruhy"
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name"]),
            models.Index(fields=["species"]),
        ]

    # Human-readable subspecies name
    def __str__(self):
        return self.latin_name
