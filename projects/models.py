
from django.core.validators import MinValueValidator
from django.db import models

from common.models import SEOModel, TimeStampedModel


class Project(SEOModel, TimeStampedModel):
    """
    Represents a project or initiative within the organization.

    Includes members, related species, and lifecycle status.
    """
    STATUS_CHOICES = (
        ("planned", "Plánovaný"),
        ("active", "Aktivní"),
        ("paused", "Pozastavený"),
        ("finished", "Ukončený"),
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Název projektu",
        help_text="Plný název projektu nebo iniciativy.",
        db_index=True,
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="Unikátní URL identifikátor projektu.",
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        verbose_name="Popis projektu",
        help_text="Detailní popis projektu včetně hlavních cílů a očekávaných výsledků.",
    )

    coordinator = models.ForeignKey(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="coordinated_projects",
        verbose_name="Koordinátor projektu",
        help_text="Člen odpovědný za vedení a koordinaci projektu.",
        db_index=True,
    )
    members = models.ManyToManyField(
        "members.MemberProfile",
        through="ProjectMembership",
        related_name="projects",
        verbose_name="Členové projektu",
        help_text="Členové zapojení do projektu.",
    )

    species = models.ManyToManyField(
        "taxonomy.Species",
        blank=True,
        related_name="projects",
        verbose_name="Související druhy",
        help_text="Druhy, kterých se projekt týká.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        db_index=True,
        verbose_name="Stav",
        help_text="Aktuální stav projektu.",
    )

    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum začátku",
        help_text="Datum zahájení projektu.",
        db_index=True,
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum ukončení",
        help_text="Plánované nebo skutečné datum ukončení projektu.",
        db_index=True,
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name="Veřejný",
        help_text="Určuje, zda může být projekt zobrazen veřejně na webu.",
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky k projektu.",
    )

    class Meta:
        verbose_name = "Projekt"
        verbose_name_plural = "Projekty"
        ordering = ["-start_date", "name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["is_public"]),
        ]

    # Human-readable project name
    def __str__(self):
        return self.name


class ProjectMembership(TimeStampedModel):
    """
    Membership of a member in a project for a specific year.

    Includes payment tracking and participation data.
    """
    member = models.ForeignKey(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="project_memberships",
        verbose_name="Člen",
        help_text="Člen zapojený do projektu.",
        db_index=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Projekt",
        help_text="Projekt, ke kterému člen patří.",
        db_index=True,
    )

    year = models.PositiveIntegerField(
        verbose_name="Rok",
        help_text="Rok účasti v projektu.",
        db_index=True,
        validators=[MinValueValidator(1900)],
    )

    annual_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Roční poplatek",
        help_text="Roční poplatek za účast v projektu pro daný rok.",
    )

    is_paid = models.BooleanField(
        default=False,
        verbose_name="Zaplaceno",
        help_text="Určuje, zda byl poplatek uhrazen.",
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Datum platby",
        help_text="Datum a čas, kdy byla platba provedena.",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Poznámky",
        help_text="Interní poznámky k účasti člena v projektu.",
    )

    class Meta:
        verbose_name = "Účast v projektu"
        verbose_name_plural = "Účasti v projektu"
        ordering = ["-year", "project", "member"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "project", "year"],
                name="unique_member_project_year",
            )
        ]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["is_paid"]),
        ]

    # Human-readable membership representation
    def __str__(self):
        return f"{self.member} – {self.project} ({self.year})"
