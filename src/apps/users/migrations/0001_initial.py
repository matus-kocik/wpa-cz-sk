# Generated by Django 5.1.5 on 2025-02-05 08:21

import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions "
                            "without explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Email Address",
                        max_length=254,
                        unique=True,
                        verbose_name="Email Address",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        help_text="First Name", max_length=64, verbose_name="First Name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        help_text="Last Name", max_length=64, verbose_name="Last Name"
                    ),
                ),
                (
                    "full_name",
                    models.GeneratedField(
                        db_persist=True,
                        expression=django.db.models.functions.text.Concat(
                            models.F("first_name"),
                            models.Value(" "),
                            models.F("last_name"),
                        ),
                        help_text="Full Name",
                        output_field=models.CharField(max_length=128),
                        verbose_name="Full Name",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Active User",
                        verbose_name="Active User",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False, help_text="Staff User", verbose_name="Staff User"
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date Joined",
                        verbose_name="Date Joined",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "The groups this user belongs to. A user will get all "
                            "permissions granted to each of their groups."
                        ),
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "db_table": "users",
                "ordering": ["-date_joined"],
            },
        ),
    ]
