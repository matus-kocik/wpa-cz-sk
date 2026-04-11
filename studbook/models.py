
from django.core.exceptions import ValidationError
from django.db import models

from common.models import TimeStampedModel


class BirdRecord(TimeStampedModel):
    """
    Core record representing a single bird in the studbook.

    Stores identity, origin, ownership, and lineage data.
    """
    SEX_CHOICES = (
        ("male", "Samec"),
        ("female", "Samice"),
        ("unknown", "Neurčeno"),
    )

    STATUS_CHOICES = (
        ("active", "Aktivní"),
        ("sold", "Prodán"),
        ("gifted", "Darován"),
        ("loaned", "Zapůjčen"),
        ("deceased", "Uhynul"),
        ("missing", "Neznámý"),
        ("archived", "Archivován"),
    )

    member = models.ForeignKey(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="birds",
        verbose_name="Člen",
        help_text="Člen organizace, kterému je jedinec aktuálně přiřazen.",
        db_index=True,
    )
    species = models.ForeignKey(
        "taxonomy.Species",
        on_delete=models.CASCADE,
        related_name="birds",
        verbose_name="Druh",
        help_text="Druh evidovaného jedince.",
    )
    subspecies = models.ForeignKey(
        "taxonomy.Subspecies",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="birds",
        verbose_name="Poddruh",
        help_text="Poddruh evidovaného jedince, pokud je známý.",
    )

    name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Jméno / označení",
        help_text="Volitelné jméno nebo interní označení jedince.",
    )
    ring_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        verbose_name="Číslo kroužku",
        help_text="Jedinečné číslo kroužku, pokud je známé.",
    )
    sex = models.CharField(
        max_length=20,
        choices=SEX_CHOICES,
        default="unknown",
        verbose_name="Pohlaví",
        help_text="Pohlaví jedince.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
        verbose_name="Stav",
        help_text="Aktuální stav jedince v evidenci.",
    )

    hatch_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum vylíhnutí / narození",
        help_text="Datum vylíhnutí nebo narození jedince, pokud je známé.",
    )
    acquisition_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum získání",
        help_text="Datum, kdy byl jedinec získán do chovu.",
    )
    death_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum úhynu",
        help_text="Datum úhynu nebo vyřazení jedince, pokud nastalo.",
    )

    father = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="offspring_from_father",
        verbose_name="Otec",
        help_text="Otec evidovaného jedince, pokud je známý.",
    )
    mother = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="offspring_from_mother",
        verbose_name="Matka",
        help_text="Matka evidovaného jedince, pokud je známá.",
    )

    source = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Původ / zdroj",
        help_text="Odkud jedinec pochází, například vlastní odchov, nákup, dar nebo výměna.",
    )
    current_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Aktuální umístění",
        help_text="Voliéra, farma, chovné zařízení nebo jiné aktuální umístění jedince.",
    )
    breeder_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Chovatel původu",
        help_text="Jméno původního chovatele nebo organizace, pokud je známé.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Obecné interní poznámky k jedinci.",
    )

    class Meta:
        verbose_name = "Jedinec"
        verbose_name_plural = "Jedinci"
        ordering = ["species__latin_name", "ring_number", "name"]
        indexes = [
            models.Index(fields=["species"]),
            models.Index(fields=["member"]),
            models.Index(fields=["status"]),
            models.Index(fields=["ring_number"]),
        ]

    def __str__(self):
        label = self.ring_number or self.name or f"ID {self.pk}"
        return f"{self.species} – {label}"

    # Validation to ensure logical parent relationships
    def clean(self):
        if self.father_id and self.father_id == self.pk:
            raise ValidationError({"father": "Jedinec nemůže být sám sobě otcem."})

        if self.mother_id and self.mother_id == self.pk:
            raise ValidationError({"mother": "Jedinec nemůže být sám sobě matkou."})

        if self.father and self.father.sex == "female":
            raise ValidationError({"father": "Vybraný otec má v evidenci pohlaví samice."})

        if self.mother and self.mother.sex == "male":
            raise ValidationError({"mother": "Vybraná matka má v evidenci pohlaví samec."})


class BirdEvent(TimeStampedModel):
    """
    Timeline event related to a specific bird.

    Used to track lifecycle events such as birth, transfer, or death.
    """
    EVENT_TYPE_CHOICES = (
        ("note", "Poznámka"),
        ("birth", "Vylíhnutí / narození"),
        ("transfer", "Přesun / převod"),
        ("sale", "Prodej"),
        ("gift", "Darování"),
        ("death", "Úhyn"),
        ("observation", "Pozorování"),
        ("breeding", "Chovná událost"),
    )

    bird = models.ForeignKey(
        BirdRecord,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Jedinec",
        help_text="Jedinec, ke kterému se událost vztahuje.",
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default="note",
        db_index=True,
        verbose_name="Typ události",
        help_text="Typ záznamu v životní historii jedince.",
    )
    event_date = models.DateField(
        verbose_name="Datum události",
        help_text="Datum, kdy událost nastala.",
        db_index=True,
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Název události",
        help_text="Krátký nadpis záznamu, například Prodej, Pozorování nebo Přesun.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Popis",
        help_text="Detailní popis události.",
    )

    class Meta:
        verbose_name = "Událost jedince"
        verbose_name_plural = "Události jedince"
        ordering = ["-event_date", "-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["event_date"]),
        ]

    # Human-readable event representation
    def __str__(self):
        return f"{self.bird} – {self.get_event_type_display()} ({self.event_date})"


class HealthRecord(TimeStampedModel):
    """
    Health-related record for a bird.

    Stores diagnosis, treatment, and veterinary info.
    """
    bird = models.ForeignKey(
        BirdRecord,
        on_delete=models.CASCADE,
        related_name="health_records",
        verbose_name="Jedinec",
        help_text="Jedinec, ke kterému se zdravotní záznam vztahuje.",
    )
    record_date = models.DateField(
        verbose_name="Datum záznamu",
        help_text="Datum vyšetření, léčby nebo zdravotní události.",
        db_index=True,
    )
    diagnosis = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Diagnóza",
        help_text="Diagnóza nebo stručné označení zdravotního problému.",
    )
    treatment = models.TextField(
        blank=True,
        verbose_name="Léčba",
        help_text="Použitá léčba, léky nebo doporučený postup.",
    )
    veterinarian = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Veterinář",
        help_text="Jméno veterináře nebo pracoviště, pokud je známé.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Další interní poznámky ke zdravotnímu záznamu.",
    )

    class Meta:
        verbose_name = "Zdravotní záznam"
        verbose_name_plural = "Zdravotní záznamy"
        ordering = ["-record_date", "-created_at"]
        indexes = [
            models.Index(fields=["record_date"]),
        ]

    # Human-readable health record
    def __str__(self):
        return f"{self.bird} – {self.record_date}"


class CareRecord(TimeStampedModel):
    """
    Routine care record for a bird.

    Includes feeding, treatments, and scheduled care.
    """
    CARE_TYPE_CHOICES = (
        ("feeding", "Krmení"),
        ("deworming", "Odčervení"),
        ("vaccination", "Vakcinace"),
        ("supplement", "Doplněk"),
        ("care", "Péče"),
    )

    bird = models.ForeignKey(
        BirdRecord,
        on_delete=models.CASCADE,
        related_name="care_records",
        verbose_name="Jedinec",
        help_text="Jedinec, ke kterému se záznam péče vztahuje.",
    )
    care_type = models.CharField(
        max_length=20,
        choices=CARE_TYPE_CHOICES,
        verbose_name="Typ péče",
        help_text="Typ péče, například krmení, odčervení nebo vakcinace.",
        db_index=True,
    )
    care_date = models.DateField(
        verbose_name="Datum",
        help_text="Datum provedené péče.",
        db_index=True,
    )
    product = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Přípravek / krmivo",
        help_text="Použitý přípravek, krmivo nebo doplněk.",
    )
    dosage = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dávkování",
        help_text="Dávkování nebo množství, pokud je relevantní.",
    )
    next_due = models.DateField(
        blank=True,
        null=True,
        verbose_name="Další termín",
        help_text="Datum dalšího plánovaného úkonu, pokud je známé.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Další interní poznámky k provedené péči.",
    )

    class Meta:
        verbose_name = "Záznam péče"
        verbose_name_plural = "Záznamy péče"
        ordering = ["-care_date", "-created_at"]
        indexes = [
            models.Index(fields=["care_type"]),
            models.Index(fields=["care_date"]),
        ]

    # Human-readable care record
    def __str__(self):
        return f"{self.bird} – {self.get_care_type_display()} ({self.care_date})"


class TransferRecord(TimeStampedModel):
    """
    Record of ownership transfer or movement of a bird.

    Tracks sales, gifts, exchanges, and relocations.
    """
    TRANSFER_TYPE_CHOICES = (
        ("sale", "Prodej"),
        ("gift", "Darování"),
        ("exchange", "Výměna"),
        ("move", "Přesun"),
        ("loan", "Zapůjčení"),
        ("return", "Vrácení"),
    )

    bird = models.ForeignKey(
        BirdRecord,
        on_delete=models.CASCADE,
        related_name="transfer_records",
        verbose_name="Jedinec",
        help_text="Jedinec, kterého se převod nebo přesun týká.",
    )
    transfer_type = models.CharField(
        max_length=20,
        choices=TRANSFER_TYPE_CHOICES,
        verbose_name="Typ převodu",
        help_text="Typ převodu nebo přesunu jedince.",
        db_index=True,
    )
    transfer_date = models.DateField(
        verbose_name="Datum převodu",
        help_text="Datum, kdy k převodu nebo přesunu došlo.",
        db_index=True,
    )
    partner_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Protistrana",
        help_text="Jméno osoby, organizace nebo chovatele, ke kterému jedinec směřuje nebo od kterého přišel.",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Místo",
        help_text="Místo nebo lokalita spojená s převodem či přesunem.",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Cena",
        help_text="Cena převodu nebo prodeje, pokud je relevantní.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Další interní poznámky k převodu nebo přesunu.",
    )

    class Meta:
        verbose_name = "Záznam převodu"
        verbose_name_plural = "Záznamy převodů"
        ordering = ["-transfer_date", "-created_at"]
        indexes = [
            models.Index(fields=["transfer_type"]),
            models.Index(fields=["transfer_date"]),
        ]

    # Human-readable transfer record
    def __str__(self):
        return f"{self.bird} – {self.get_transfer_type_display()} ({self.transfer_date})"
