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
    czech_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Český název",
        help_text="Český název čeledi",
        db_index=True,
    )
    slovak_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Slovenský názov",
        help_text="Slovenský názov čeledi",
        db_index=True,
    )
    english_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Anglický název",
        help_text="Anglický název čeledi",
        db_index=True,
    )
    german_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Německý název",
        help_text="Německý název čeledi",
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
    czech_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Český název",
        help_text="Český název rodu",
        db_index=True,
    )
    slovak_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Slovenský názov",
        help_text="Slovenský názov rodu",
        db_index=True,
    )
    english_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Anglický název",
        help_text="Anglický název rodu",
        db_index=True,
    )
    german_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Německý název",
        help_text="Německý název rodu",
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
    slovak_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Slovenský názov",
        help_text="Slovenský názov druhu",
        db_index=True,
    )
    english_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Anglický název",
        help_text="Anglický název druhu",
        db_index=True,
    )
    german_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Německý název",
        help_text="Německý název druhu",
        db_index=True,
    )
    authority = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Autor",
        help_text="Autor vědeckého názvu",
    )

    authority_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Rok popisu",
        help_text="Rok, kdy byl druh vědecky popsán",
        db_index=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Aktivní",
        help_text="Zda je druh aktivně používán",
    )

    SUBSPECIES_TYPE_CHOICES = [
        ("mono", "Monotypický"),
        ("poly", "Polytypický"),
    ]

    subspecies_note = models.CharField(
        max_length=10,
        choices=SUBSPECIES_TYPE_CHOICES,
        blank=True,
        verbose_name="Typ druhu",
        help_text="Zda je druh monotypický nebo polytypický",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Doplňující informace o druhu",
    )

    distribution = models.TextField(
        blank=True,
        verbose_name="Výskyt",
        help_text="Geografické rozšíření druhu",
    )
    habitat = models.TextField(
        blank=True,
        verbose_name="Obývá",
        help_text="Typy biotopu, kde druh žije",
    )

    CONSERVATION_CHOICES = [
        ("LC", "Málo dotknutý"),
        ("NT", "Takmer ohrozený"),
        ("VU", "Zraniteľný"),
        ("EN", "Ohrozený"),
        ("CR", "Kriticky ohrozený"),
        ("EW", "Vyhynutý v prírode"),
        ("EX", "Vyhynutý"),
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
    length_male_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Délka samec (min)",
        help_text="Minimální délka samce v cm",
    )
    length_male_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Délka samec (max)",
        help_text="Maximální délka samce v cm",
    )
    length_female_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Délka samice (min)",
        help_text="Minimální délka samice v cm",
    )
    length_female_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Délka samice (max)",
        help_text="Maximální délka samice v cm",
    )
    weight_male_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Hmotnost samec (min)",
        help_text="Minimální hmotnost samce v g",
    )
    weight_male_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Hmotnost samec (max)",
        help_text="Maximální hmotnost samce v g",
    )
    weight_female_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Hmotnost samice (min)",
        help_text="Minimální hmotnost samice v g",
    )
    weight_female_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Hmotnost samice (max)",
        help_text="Maximální hmotnost samice v g",
    )
    clutch_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Snůška (min)",
        help_text="Minimální počet vajec ve snůšce",
    )
    clutch_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Snůška (max)",
        help_text="Maximální počet vajec ve snůšce",
    )
    clutch_note = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Snůška – poznámka",
        help_text="Doplňující informace (např. konec dubna apod.)",
    )
    incubation_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Inkubace (min)",
        help_text="Minimální doba inkubace ve dnech",
    )
    incubation_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Inkubace (max)",
        help_text="Maximální doba inkubace ve dnech",
    )
    incubation_note = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Inkubace – poznámka",
        help_text="Doplňující informace (např. závislost na podmínkách apod.)",
    )

    ring_size = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Velikost kroužku",
        help_text="Velikost identifikačního kroužku v mm",
    )
    population = models.TextField(
        blank=True,
        verbose_name="Populace (CZ/SK)",
        help_text="Odhad populace v ČR a SR",
    )
    breeding_difficulty = models.CharField(
        max_length=100,
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


    class Meta:
        verbose_name = "Druh"
        verbose_name_plural = "Druhy"
        ordering = ["latin_name"]
        indexes = [
            models.Index(fields=["latin_name"]),
            models.Index(fields=["czech_name"]),
            models.Index(fields=["slovak_name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["english_name"]),
            models.Index(fields=["german_name"]),
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
    czech_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Český název",
        help_text="Český název poddruhu",
        db_index=True,
    )
    slovak_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Slovenský názov",
        help_text="Slovenský název poddruhu",
        db_index=True,
    )
    english_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Anglický název",
        help_text="Anglický název poddruhu",
        db_index=True,
    )
    german_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Německý název",
        help_text="Německý název poddruhu",
        db_index=True,
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


# External links related to a species (YouTube videos, Facebook albums, etc.).
class SpeciesLink(models.Model):
    """
    External links related to a species (YouTube videos, Facebook albums, etc.).
    """
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="links",
        verbose_name="Druh",
        help_text="Přiřazený druh",
        db_index=True,
    )

    TYPE_CHOICES = [
        ("yt", "YouTube"),
        ("fb", "Facebook"),
    ]

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Typ",
        help_text="Typ odkazu",
    )

    url = models.URLField(
        verbose_name="URL",
        help_text="Odkaz na video nebo album",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Název",
        help_text="Volitelný název odkazu (např. Tokání samce)",
    )

    class Meta:
        verbose_name = "Odkaz"
        verbose_name_plural = "Odkazy"
        ordering = ["type"]

    def __str__(self):
        return self.title or self.url
