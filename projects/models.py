
from django.db import models

from common.models import SEOModel, TimeStampedModel


class Project(SEOModel, TimeStampedModel):
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
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="Unikátní URL identifikátor projektu.",
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
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Datum ukončení",
        help_text="Plánované nebo skutečné datum ukončení projektu.",
    )

    is_public = models.BooleanField(
        default=True,
        verbose_name="Veřejný",
        help_text="Určuje, zda může být projekt zobrazen veřejně na webu.",
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

    def __str__(self):
        return self.name


class ProjectMembership(TimeStampedModel):
    member = models.ForeignKey(
        "members.MemberProfile",
        on_delete=models.CASCADE,
        related_name="project_memberships",
        verbose_name="Člen",
        help_text="Člen zapojený do projektu.",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Projekt",
        help_text="Projekt, ke kterému člen patří.",
    )

    year = models.PositiveIntegerField(
        verbose_name="Rok",
        help_text="Rok účasti v projektu.",
        db_index=True,
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

    def __str__(self):
        return f"{self.member} – {self.project} ({self.year})"
