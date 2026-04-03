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
    note = models.TextField(blank=True, max_length=256)

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
