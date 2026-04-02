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
        editable=False,
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

    ROLE_CHOICES = [
        ("president", "Predseda"),
        ("vice_president", "Miestopredseda"),
        ("treasurer", "Pokladník"),
        ("registrar", "Registrátor"),
        ("web_admin", "Správca webu"),
        ("manager", "Jednateľ"),
    ]

    role = models.CharField(
        max_length=24,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    joined_at = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [F("registration_number").asc(nulls_last=True), "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                name="unique_member_per_user",
            )
        ]

    def __str__(self):
        name = self.full_name or self.user.email
        return f"{name} ({self.registration_number or 'no ID'})"

    @property
    def is_valid(self):
        if not self.valid_until:
            return True
        return self.valid_until >= date.today()

    @property
    def full_name(self):
        return self.user.full_name

    def save(self, *args, **kwargs):
        creating = self.pk is None

        super().save(*args, **kwargs)

        if creating and not self.registration_number:
            self.registration_number = str(self.id).zfill(3)
            super().save(update_fields=["registration_number"])
