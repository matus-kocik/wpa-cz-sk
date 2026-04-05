from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import F


class MemberProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )

    registration_number = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )

    STATUS_CHOICES = [
        ("member", "Člen"),
        ("honorary", "Čestný člen"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="member",
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

    class Meta:
        ordering = [F("registration_number").asc(nulls_last=True), "created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.registration_number or 'no ID'})"

    @property
    def is_valid(self):
        if not self.valid_until:
            return True
        return self.valid_until >= date.today()

    @property
    def full_name(self):
        return (
            getattr(self.user, "full_name", "")
            or f"{self.user.first_name} {self.user.last_name}".strip()
            or self.user.email
        )


# MembershipApplication model
class MembershipApplication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applications",
        null=True,
        blank=True,
    )

    # základ
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    academic_title = models.CharField(max_length=48, blank=True)

    birth_date = models.DateField()

    # adresa
    city = models.CharField(max_length=64)
    street = models.CharField(max_length=128)
    house_number = models.CharField(max_length=32)
    postal_code = models.CharField(max_length=10)
    district = models.CharField(max_length=64)
    country = models.CharField(max_length=2)

    # kontakt
    phone_number = models.CharField(max_length=24, blank=True)
    email = models.EmailField(max_length=128, db_index=True)

    # poznámky
    notes = models.TextField(blank=True, max_length=256)

    # deklarácia
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

    payment_status = models.CharField(
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
            models.Index(fields=["status", "payment_status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status}, {self.payment_status})"

    def approve(self):
        if self.status != "approved":
            return

        if self.payment_status != "paid":
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Create or get user
        user, created = User.objects.get_or_create(
            email=self.email,
            defaults={
                "first_name": self.first_name,
                "last_name": self.last_name,
            },
        )

        if not created:
            # Update basic info if user already exists
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
            profile.save()
