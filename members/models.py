from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F, IntegerField
from django.db.models.functions import Cast


class MemberProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )

    icch_number = models.CharField(
        max_length=4,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
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
    )

    POSITION_CHOICES = [
        ("president", "Předseda"),
        ("vice_president", "Místopředseda"),
        ("treasurer", "Pokladník"),
        ("registrar", "Registrátor"),
        ("web_admin", "Správce webu"),
        ("manager", "Jednatel"),
    ]

    position = models.CharField(
        max_length=24,
        choices=POSITION_CHOICES,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    PAYMENT_STATUS = [
        ("unpaid", "Nezaplatené"),
        ("paid", "Zaplatené"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="unpaid",
        db_index=True,
    )

    joined_at = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, max_length=256)

    phone_number = models.CharField(max_length=24, blank=True)
    city = models.CharField(max_length=64, blank=True)
    street = models.CharField(max_length=128, blank=True)
    house_number = models.CharField(max_length=32, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    district = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Clean data before saving
    def save(self, *args, **kwargs):
        # Clean data
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
        if self.country:
            self.country = self.country.strip().upper()
        if self.notes:
            self.notes = self.notes.strip()

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

            self.icch_number = str(next_number).zfill(4)

        # Sync payment status ONLY on change
        if self.payment_status == "paid" and old_payment_status != "paid":
            self.is_active = True

            today = date.today()

            if self.valid_until and self.valid_until >= today:
                self.valid_until = date(self.valid_until.year + 1, 3, 31)
            else:
                self.valid_until = date(today.year + 1, 3, 31)

        elif self.payment_status == "unpaid" and old_payment_status == "paid":
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

    def __str__(self):
        return f"{self.full_name} ({self.icch_number or 'no ID'})"

    @property
    def is_valid(self):
        if not self.valid_until:
            return False
        return self.valid_until >= date.today()

    @property
    def full_name(self):
        if not self.user:
            return "Unknown member"

        return (
            getattr(self.user, "full_name", "")
            or f"{self.user.first_name} {self.user.last_name}".strip()
            or self.user.email
        )


# Clean data before saving
class MembershipApplication(models.Model):
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
            self.country = self.country.strip().upper()
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
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    academic_title = models.CharField(max_length=48, blank=True)

    birth_date = models.DateField()

    city = models.CharField(max_length=64)
    street = models.CharField(max_length=128)
    house_number = models.CharField(max_length=32)
    postal_code = models.CharField(max_length=10)
    district = models.CharField(max_length=64)
    country = models.CharField(max_length=2)

    phone_number = models.CharField(max_length=24, blank=True)
    email = models.EmailField(max_length=128, db_index=True)

    notes = models.TextField(blank=True, max_length=256)

    declaration_place = models.CharField(max_length=128)
    declaration_date = models.DateField()
    declaration_signature = models.CharField(max_length=128)

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
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    @transaction.atomic
    def approve(self):
        if self.status != "approved":
            return

        if self.initial_payment_status != "paid":
            return

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
