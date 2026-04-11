from django.core.validators import MinValueValidator
from django.db import models

from common.models import SEOModel, TimeStampedModel


class BreedingReport(SEOModel, TimeStampedModel):
    """
    Annual breeding report submitted by a member.

    Contains summary data and snapshot of member info at submission time.
    """
    STATUS_CHOICES = (
        ("draft", "Rozpracováno"),
        ("submitted", "Odesláno"),
        ("approved", "Schváleno"),
    )

    member = models.ForeignKey(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="breeding_reports",
        verbose_name="Člen",
        help_text="Člen organizace, ke kterému patří tento roční výkaz chovu.",
        db_index=True,
    )
    year = models.PositiveIntegerField(
        verbose_name="Rok",
        help_text="Rok, pro který je výkaz chovu veden.",
        validators=[MinValueValidator(1900)],
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Stav",
        help_text="Stav zpracování výkazu chovu.",
        db_index=True,
    )
    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Odesláno",
        help_text="Datum a čas odeslání výkazu členem.",
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Schváleno",
        help_text="Datum a čas schválení výkazu administrátorem.",
    )

    # Snapshot of member data at time of submission
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Jméno a příjmení",
        help_text="Uložené jméno člena v době odeslání výkazu.",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adresa",
        help_text="Uložená adresa člena v době odeslání výkazu.",
    )
    city = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Město",
        help_text="Uložené město člena v době odeslání výkazu.",
    )
    postal_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="PSČ",
        help_text="Uložené PSČ člena v době odeslání výkazu.",
    )
    country = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Země",
        help_text="Uložená země člena v době odeslání výkazu.",
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Telefon",
        help_text="Uložený telefon člena v době odeslání výkazu.",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
        help_text="Uložený e-mail člena v době odeslání výkazu.",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky k výkazu jako celku.",
    )

    class Meta:
        verbose_name = "Výkaz chovu"
        verbose_name_plural = "Výkazy chovu"
        ordering = ["-year", "member"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "year"],
                name="unique_member_year_breeding_report",
            )
        ]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["status"]),
            models.Index(fields=["member"]),
        ]

    # Human-readable representation of report
    def __str__(self):
        return f"{self.member} – {self.year}"


class BreedingRecord(SEOModel, TimeStampedModel):
    """
    Detailed record for a specific species within a breeding report.

    Stores counts of animals and offspring.
    """
    report = models.ForeignKey(
        BreedingReport,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Výkaz chovu",
        help_text="Výkaz chovu, do kterého tento řádek patří.",
        db_index=True,
    )
    species = models.ForeignKey(
        "taxonomy.Species",
        on_delete=models.CASCADE,
        related_name="breeding_records",
        verbose_name="Druh",
        help_text="Druh, který člen v daném roce chová.",
        db_index=True,
    )
    pairs_with_chicks = models.PositiveIntegerField(
        default=0,
        verbose_name="Páry s odchovem",
        help_text="Počet párů, které v daném roce úspěšně odchovaly mláďata.",
    )
    number_of_males = models.PositiveIntegerField(
        default=0,
        verbose_name="Počet samců",
        help_text="Počet dospělých samců chovaného druhu.",
    )
    number_of_females = models.PositiveIntegerField(
        default=0,
        verbose_name="Počet samic",
        help_text="Počet dospělých samic chovaného druhu.",
    )
    number_of_male_offspring = models.PositiveIntegerField(
        default=0,
        verbose_name="Počet samců odchovu",
        help_text="Počet odchovaných samců v daném roce.",
    )
    number_of_female_offspring = models.PositiveIntegerField(
        default=0,
        verbose_name="Počet samic odchovu",
        help_text="Počet odchovaných samic v daném roce.",
    )
    number_of_unsexed_offspring = models.PositiveIntegerField(
        default=0,
        verbose_name="Neurčený odchov",
        help_text="Počet odchovaných kusů neurčeného pohlaví.",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Dodatečné interní poznámky k chovu, odchovu nebo stavu populace.",
    )

    class Meta:
        verbose_name = "Záznam chovu"
        verbose_name_plural = "Záznamy chovu"
        ordering = ["species__latin_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["report", "species"],
                name="unique_report_species_breeding_record",
            )
        ]
        indexes = [
            models.Index(fields=["species"]),
            models.Index(fields=["report"]),
        ]

    # Human-readable representation of record
    def __str__(self):
        return f"{self.report} – {self.species}"

    # Total adult animals of this species
    @property
    def total_count_of_species(self):
        return self.number_of_males + self.number_of_females

    # Total offspring count
    @property
    def total_count_offspring(self):
        return (
            self.number_of_male_offspring
            + self.number_of_female_offspring
            + self.number_of_unsexed_offspring
        )
