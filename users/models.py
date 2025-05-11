from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Concat


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.

    This manager is responsible for handling user creation, including regular users
    and superusers, and provides additional authentication-related methods.

    Methods:
        - create_user(email, password=None, **extra_fields): Creates a regular user.
        - create_superuser(email, password=None, **extra_fields): Creates a superuser.
        - get_by_natural_key(email): Retrieves a user by their email.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given email and password.

        This method ensures that every user has a unique email and that the email
        is properly formatted before storing it in the database.

        Args:
            email (str): The unique email address of the user.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields for the user model.

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If the email is missing.
        """
        if not email:
            raise ValueError("The Email field is required and must be set")

        # Normalize email to lowercase
        email = self.normalize_email(email)
        # Ensure users are active by default
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)

        if password:
            # Securely set hash the user's password
            user.set_password(password)
        else:
            # Set an unusable password (e.g., for OAuth users...)
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a new superuser with the given email and password.
        Extra fields are added to indicate that the user is staff, active,
        and indeed a superuser.

        Superusers have full permissions (`is_staff=True` and `is_superuser=True`).
        If these flags are not explicitly set, the method will raise an error.

        Args:
            email (str): The unique email address of the superuser.
            password (str, optional): The superuser's password. Defaults to None.
            **extra_fields: Additional fields for the superuser model.

        Returns:
            CustomUser: Created superuser instance with admin privileges

        Raises:
            ValueError: If `is_staff` or `is_superuser` is not set to True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields["is_staff"]:
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        """
        Retrieves a user instance by their natural key (email).

        This method is used by Django's authentication system to find users
        during login or permission checks.

        Args:
            email (str): The email of the user.

        Returns:
            CustomUser: The user instance.

        Raises:
            ValueError: If the email is not provided.
        """
        if not email:
            raise ValueError("Natural key (email) must be provided")
        # Case-insensitive lookup
        return self.get(email__iexact=email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that replaces Django's default User model.

    This model extends Django's AbstractBaseUser and PermissionsMixin to create
    a fully featured user model with admin-compliant permissions.

    Fields:
        - email (EmailField): The user's unique email address.
        - first_name (CharField): The user's first name.
        - last_name (CharField): The user's last name.
        - full_name (GeneratedField): The user's full name (first + last name).
        - is_active (BooleanField): Indicates whether the account is active.
        - is_staff (BooleanField): Determines if the user has admin privileges.
        - date_joined (DateTimeField): Timestamp of when the account was created.

    Authentication:
        - `USERNAME_FIELD` is set to `email` (instead of `username`).
        - `REQUIRED_FIELDS` include `first_name` and `last_name`.
    """

    email = models.EmailField(
        unique=True,
        db_index=True,  # Optimizes queries involving email searches
        verbose_name="Email Address",  # Display name in Django Admin and forms
        # Appears in Django Admin as field description
        help_text="User's unique email address.",
    )
    first_name = models.CharField(
        max_length=64, verbose_name="First Name", help_text="User's first name."
    )
    last_name = models.CharField(
        max_length=64, verbose_name="Last Name", help_text="User's last name."
    )
    full_name = models.GeneratedField(
        expression=Concat(
            models.F("first_name"), models.Value(" "), models.F("last_name")
        ),
        output_field=models.CharField(max_length=128),
        # Ensures that the full name is stored in the database for optimized queries
        db_persist=True,
        verbose_name="Full Name",
        help_text="User's full name (first + last name).",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active User",
        help_text="Indicates whether the user account is active.",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff User",
        help_text="Indicates whether the user has admin privileges.",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Joined",
        help_text="Timestamp when the user registered.",
    )

    objects = CustomUserManager()

    # Django authentication settings
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        """
        Returns a string representation of the user.

        This method formats the user's full name and email in a readable way.
        """
        return f"{self.full_name} ({self.email})"

    class Meta:
        """
        Meta options for the CustomUser model.

        - `db_table`: Defines the database table name (`users`).
        - `verbose_name`: Defines the singular name for the model in the admin.
        - `verbose_name_plural`: Defines the plural name for the model in the admin.
        - `ordering`: Ensures that users are ordered by their registration date
            (newest first).
        """

        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def clean(self):
        """
        Custom validation for the user model.

        This method:
        - Ensures that the email is always stored in lowercase.
        - Validates that first and last names are not empty.
        - Prevents duplicate emails from being registered.

        Raises:
            ValidationError: If any validation rule fails.
        """
        super().clean()

        # Ensure email is lowercase and stripped of whitespace
        if self.email:
            self.email = self.email.lower().strip()

        if not self.first_name:
            raise ValidationError({"first_name": "The First Name field is required"})

        if not self.last_name:
            raise ValidationError({"last_name": "The Last Name field is required"})

        # Ensure email uniqueness (Django already enforces unique=True,
        # but this prevents case-sensitive issues)

        if CustomUser.objects.exclude(pk=self.pk).filter(email=self.email).exists():
            raise ValidationError({"email": "A user with this email already exists."})
