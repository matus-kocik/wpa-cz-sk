from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import models, transaction
from django.db.models import F, IntegerField
from django.db.models.functions import Cast
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_countries.fields import CountryField


# New Role model
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Názov")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Role (funkcie)"
        ordering = ["name"]


class MemberProfile(models.Model):
    """
    Core member profile linked to a user account.

    Stores membership data, contact info, and payment status.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
        verbose_name="Uživatel",
        help_text="Propojený uživatelský účet",
        db_index=True,
    )

    icch_number = models.CharField(
        max_length=3,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="ICCH číslo",
        help_text="Unikátní identifikační číslo člena",
    )

    MEMBERSHIP_TYPE_CHOICES = [
        ("regular", "Řádné členství"),
        ("honorary", "Čestné členství"),
        ("junior", "Juniorské členství"),
    ]

    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_TYPE_CHOICES,
        default="regular",
        db_index=True,
        verbose_name="Typ členství",
        help_text="Typ členství v organizaci",
    )

    MEMBER_TYPE_CHOICES = [
        ("person", "Fyzická osoba"),
        ("organization", "Organizace"),
    ]

    member_type = models.CharField(
        max_length=20,
        choices=MEMBER_TYPE_CHOICES,
        default="person",
        db_index=True,
        verbose_name="Typ člena",
        help_text="Určuje, zda jde o fyzickou osobu nebo organizaci (např. ZOO)",
    )

    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="members",
        verbose_name="Role",
        help_text="Funkcie člena v organizaci",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktivní",
        help_text="Zda je člen aktivní",
        db_index=True,
    )

    PAYMENT_STATUS = [
        ("unpaid", "Nezaplatené"),
        ("paid", "Zaplatené"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="unpaid",
        db_index=True,
        verbose_name="Stav platby",
        help_text="Stav členského příspěvku",
    )

    joined_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Datum vstupu",
        help_text="Datum vstupu do organizace",
        db_index=True,
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Platnost do",
        help_text="Datum platnosti členství",
        db_index=True,
    )
    notes = models.TextField(
        blank=True,
        max_length=256,
        verbose_name="Poznámky",
        help_text="Interní poznámky",
    )

    phone_number = models.CharField(
        max_length=24,
        blank=True,
        verbose_name="Telefon",
        help_text="Kontaktní telefon",
    )
    city = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Město",
        help_text="Město bydliště",
        db_index=True,
    )
    street = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Ulice",
        help_text="Ulice",
    )
    house_number = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Číslo domu",
        help_text="Číslo domu",
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="PSČ",
        help_text="Poštovní směrovací číslo",
    )
    district = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Okres",
        help_text="Okres nebo region",
    )
    country = CountryField(
        blank=True,
        verbose_name="Stát",
        help_text="Stát (výběr ze seznamu)",
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Vytvořeno",
        help_text="Datum a čas vytvoření záznamu",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Aktualizováno",
        help_text="Datum a čas poslední aktualizace záznamu",
    )

    def clean(self):
        super().clean()

        if self.phone_number:
            self.phone_number = self.phone_number.strip()
        if self.city:
            self.city = self.city.strip()
        if self.street:
            self.street = self.street.strip()
        if self.house_number:
            self.house_number = self.house_number.strip()
        if self.postal_code:
            self.postal_code = self.postal_code.strip()
        if self.district:
            self.district = self.district.strip()
        if self.notes:
            self.notes = self.notes.strip()
        if self.country:
            self.country = str(self.country).upper()

        # Prevent ICCH changes unless explicitly allowed
        if self.pk:
            old = MemberProfile.objects.filter(pk=self.pk).values("icch_number").first()
            if old and old["icch_number"] != self.icch_number:
                if not getattr(self, "_allow_icch_change", False) and not getattr(self, "_admin_override", False):
                    raise ValueError("ICCH number cannot be changed")

    # Custom save handling for cleaning, ICCH assignment, and payment logic
    def save(self, *args, **kwargs):
        if kwargs.pop("clean", True):
            self.full_clean()

        # detect previous payment_status
        old_payment_status = None
        if self.pk:
            old_payment_status = (
                MemberProfile.objects.filter(pk=self.pk)
                .values_list("payment_status", flat=True)
                .first()
            )

        # Auto-assign ICCH number if not set
        if not self.icch_number:

            last = (
                MemberProfile.objects.exclude(icch_number__isnull=True)
                .filter(icch_number__regex=r"^\d+$")
                .annotate(icch_int=Cast("icch_number", IntegerField()))
                .order_by("-icch_int")
                .first()
            )

            if last and last.icch_number.isdigit():
                next_number = int(last.icch_number) + 1
            else:
                next_number = 1

            self.icch_number = str(next_number).zfill(3)

        # Sync payment status (always keep is_active in sync)
        if self.payment_status == "paid":
            self.is_active = True

            # extend or set validity when transitioning to paid
            if old_payment_status != "paid":
                today = date.today()

                if self.valid_until and self.valid_until >= today:
                    self.valid_until = date(self.valid_until.year + 1, 3, 31)
                else:
                    self.valid_until = date(today.year + 1, 3, 31)
        else:
            self.is_active = False

        from django.db import IntegrityError
        for _ in range(3):
            try:
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                self.icch_number = None

    class Meta:
        ordering = [F("icch_number").asc(nulls_last=True), "created_at"]
        indexes = [
            models.Index(fields=["membership_type"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["is_active"]),
        ]

    # Human-readable member representation
    def __str__(self):
        return f"{self.full_name} ({self.icch_number or 'no ID'})"

    # Checks if membership is currently valid
    @property
    def is_valid(self):
        if not self.valid_until:
            return False
        return self.valid_until >= date.today()

    # Returns best available full name
    @property
    def full_name(self):
        if not self.user:
            return "Unknown member"

        return (
            getattr(self.user, "full_name", "")
            or f"{self.user.first_name} {self.user.last_name}".strip()
            or self.user.email
        )

    @property
    def display_name(self):
        """
        Returns a clean display name for UI.
        - Organizations: use first_name (holds org name)
        - Persons: use full_name
        """
        if self.member_type == "organization":
            return (self.user.first_name or "").strip() or self.full_name
        return self.full_name

    @property
    def has_projects(self):
        """
        Returns True if member is involved in any project.
        """
        return self.projects.exists()


# Clean data before saving
class MembershipApplication(models.Model):
    """
    Application form submitted by a user to become a member.

    Stores personal data, status, and approval workflow.
    """
    # Clean and normalize input data before saving
    def save(self, *args, **kwargs):
        # Clean data
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()
        if self.academic_title:
            self.academic_title = self.academic_title.strip()
        if self.city:
            self.city = self.city.strip().title()
        if self.street:
            self.street = self.street.strip().title()
        if self.house_number:
            self.house_number = self.house_number.strip()
        if self.postal_code:
            self.postal_code = self.postal_code.strip()
        if self.district:
            self.district = self.district.strip().title()
        if self.country:
            # CountryField returns a Country object, use its code
            self.country = str(self.country).upper()
        if self.phone_number:
            self.phone_number = self.phone_number.strip()
        if self.email:
            self.email = self.email.strip().lower()
        if self.notes:
            self.notes = self.notes.strip()
        if self.declaration_place:
            self.declaration_place = self.declaration_place.strip().title()
        if self.declaration_signature:
            self.declaration_signature = self.declaration_signature.strip().title()

        super().save(*args, **kwargs)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applications",
        null=True,
        blank=True,
        verbose_name="Uživatel",
        help_text="Propojený uživatel (pokud existuje)",
        db_index=True,
    )

    first_name = models.CharField(
        max_length=64,
        verbose_name="Jméno",
        help_text="Křestní jméno",
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name="Příjmení",
        help_text="Příjmení",
    )
    academic_title = models.CharField(
        max_length=48,
        blank=True,
        verbose_name="Titul",
        help_text="Akademický titul",
    )

    birth_date = models.DateField(
        verbose_name="Datum narození",
        help_text="Datum narození",
    )

    city = models.CharField(
        max_length=64,
        verbose_name="Město",
        help_text="Město bydliště",
    )
    street = models.CharField(
        max_length=128,
        verbose_name="Ulice",
        help_text="Ulice",
    )
    house_number = models.CharField(
        max_length=32,
        verbose_name="Číslo domu",
        help_text="Číslo domu",
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name="PSČ",
        help_text="Poštovní směrovací číslo",
    )
    district = models.CharField(
        max_length=64,
        verbose_name="Okres",
        help_text="Okres nebo region",
    )
    country = CountryField(
        verbose_name="Stát",
        help_text="Stát (výběr ze seznamu)",
    )

    phone_number = models.CharField(
        max_length=24,
        blank=True,
        verbose_name="Telefon",
        help_text="Kontaktní telefon",
    )
    email = models.EmailField(
        max_length=128,
        db_index=True,
        verbose_name="Email",
        help_text="Emailová adresa",
    )

    notes = models.TextField(
        blank=True,
        max_length=256,
        verbose_name="Poznámky",
        help_text="Doplňující informace",
    )

    declaration_place = models.CharField(
        max_length=128,
        verbose_name="Místo prohlášení",
        help_text="Místo, kde bylo prohlášení podepsáno",
    )
    declaration_date = models.DateField(
        verbose_name="Datum prohlášení",
        help_text="Datum prohlášení",
    )
    declaration_signature = models.CharField(
        max_length=128,
        verbose_name="Podpis",
        help_text="Podpis žadatele",
    )

    STATUS_CHOICES = [
        ("pending", "Čaká"),
        ("approved", "Schválené"),
        ("rejected", "Zamietnuté"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="Stav",
        help_text="Stav žádosti",
    )

    PAYMENT_STATUS = [
        ("unpaid", "Nezaplatené"),
        ("paid", "Zaplatené"),
    ]

    initial_payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="unpaid",
        db_index=True,
        verbose_name="Stav platby",
        help_text="Stav vstupního poplatku",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Vytvořeno",
        help_text="Datum a čas vytvoření záznamu",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Aktualizováno",
        help_text="Datum a čas poslední aktualizace záznamu",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "initial_payment_status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(status__in=["pending", "approved"]),
                name="unique_active_application_per_email",
            )
        ]

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name} ({self.status}, {self.initial_payment_status})"
        )

    # Approves application and creates/updates user and member profile
    @transaction.atomic
    def approve(self):
        # Prevent re-processing already approved applications with user
        if self.user:
            raise ValueError("Application already processed")

        if self.initial_payment_status != "paid":
            raise ValueError("Cannot approve unpaid application")

        self.status = "approved"
        self.save(update_fields=["status"])

        User = get_user_model()

        user = User.objects.filter(email=self.email).first()

        if not user:
            user = User.objects.create_user(
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
            )
        else:
            user.first_name = self.first_name
            user.last_name = self.last_name
            user.save(update_fields=["first_name", "last_name"])

        self.user = user
        self.save(update_fields=["user"])

        # Create or update member profile
        profile, created = MemberProfile.objects.get_or_create(
            user=user,
            defaults={
                "phone_number": self.phone_number,
                "city": self.city,
                "street": self.street,
                "house_number": self.house_number,
                "postal_code": self.postal_code,
                "district": self.district,
                "country": self.country,
                "notes": self.notes,
            },
        )

        if not created:
            # update existing profile with latest data
            for field in [
                "phone_number",
                "city",
                "street",
                "house_number",
                "postal_code",
                "district",
                "country",
                "notes",
            ]:
                setattr(profile, field, getattr(self, field))

        profile.payment_status = self.initial_payment_status

        # Set membership dates
        if not profile.joined_at:
            profile.joined_at = self.declaration_date

        if not profile.valid_until:
            profile.valid_until = date(self.declaration_date.year + 1, 3, 31)

        profile.save()

        # Send password reset email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_path = reverse(
            "password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )

        domain = getattr(settings, "SITE_URL", "http://localhost:8000")
        reset_link = f"{domain}{reset_path}"

        try:
            send_mail(
                subject="Dokončenie registrace",
                message=f"Nastavte si heslo: {reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception:
            pass
