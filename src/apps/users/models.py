from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Concat


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field is required and must be set")
        if not password:
            raise ValueError("A password is required to create a user")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True, verbose_name="Email Address", help_text="Email Address"
    )
    first_name = models.CharField(
        max_length=64, verbose_name="First Name", help_text="First Name"
    )
    last_name = models.CharField(
        max_length=64, verbose_name="Last Name", help_text="Last Name"
    )
    full_name = models.GeneratedField(
        expression=Concat(
            models.F("first_name"), models.Value(" "), models.F("last_name")
        ),
        output_field=models.CharField(max_length=128),
        db_persist=True,
        verbose_name="Full Name",
        help_text="Full Name",
    )
    is_active = models.BooleanField(
        default=True, help_text="Active User", verbose_name="Active User"
    )
    is_staff = models.BooleanField(
        default=False, help_text="Staff User", verbose_name="Staff User"
    )
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Date Joined", help_text="Date Joined"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def clean(self):
        super().clean()
        if not self.first_name:
            raise ValidationError({"first_name": "The First Name field is required"})
        if not self.last_name:
            raise ValidationError({"last_name": "The Last Name field is required"})
