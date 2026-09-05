# Users App

## Purpose

Provides the custom user model and authentication layer for WPA CZ-SK.

The app replaces Django's default username-based user model with email-based authentication and provides custom login, password reset, password setup, and Django Admin integration.

---

## Models

### CustomUser

Custom authentication model used across the project.

**Identity fields:**

- `email` – unique email address used for authentication
- `first_name` – first name
- `last_name` – last name
- `email_verified` – whether the email address has been verified

**Permissions and status:**

- `is_active` – whether the account can authenticate
- `is_staff` – whether the user can access Django Admin
- `is_superuser` – full Django permissions

**Timestamps:**

- `date_joined` – account creation timestamp
- `last_login` – last successful authentication timestamp

**Computed properties and methods:**

- `full_name` – combined first and last name
- `get_full_name()` – returns the full name
- `get_short_name()` – returns the first name

---

## Authentication

The model uses:

`USERNAME_FIELD = "email"`

`REQUIRED_FIELDS = ["first_name", "last_name"]`

Users therefore authenticate using their email address instead of a username.

Email addresses are normalized to lowercase before they are stored.

Authentication lookups through `get_by_natural_key()` are case-insensitive.

---

## User Manager

### create_user()

Creates a regular user.

The manager:

- requires an email address
- normalizes and lowercases the email
- creates active users by default
- securely hashes supplied passwords
- assigns an unusable password when no password is supplied

Users without first or last names are rejected by model validation.

### create_superuser()

Creates a Django superuser.

Superusers must have:

- `is_staff=True`
- `is_superuser=True`

Invalid privilege flags raise a `ValueError`.

---

## Validation

`CustomUser.save()` normalizes the email before running full model validation.

Every save calls `full_clean()`.

This ensures:

- valid email format
- lowercase and trimmed email storage
- required first name
- required last name
- model and uniqueness validation

A lowercase functional database index is also available for efficient case-insensitive email lookups.

---

## Forms

### LoginForm

Custom Django authentication form using an email field.

Browser autocomplete is configured for:

- email
- current password

### CustomPasswordResetForm

Custom password reset form using the user's email address.

Browser autocomplete is configured for the email field.

### CustomSetPasswordForm

Custom password setup/change form used during password reset and initial account setup.

Browser autocomplete is configured for new passwords.

Django password validation remains active.

---

## Views

### CustomLoginView

Uses the custom login template and displays a success message after successful authentication.

### CustomLogoutView

Processes logout through POST and displays a success message after successful logout.

---

## Django Admin

The custom user admin supports:

- user creation
- user editing
- activation and deactivation
- email verification
- groups and permissions
- staff and superuser privileges
- password changes

New passwords entered through the admin creation form are checked using Django password validators.

Only superusers can modify privileged permission fields:

- `is_staff`
- `is_superuser`
- `groups`
- `user_permissions`

Regular staff users cannot elevate privileges through the user admin.

---

## Integration

The users app is the authentication identity layer for the whole project.

It is directly connected with:

- `members` – membership records and onboarding
- `profiles` – public member profiles through `MemberProfile`
- Django authentication
- Django Admin
- password reset and account setup workflow

---

## Tests

Tests cover:

- regular user creation
- email normalization
- password hashing
- unusable passwords
- missing email validation
- required first and last names
- superuser creation
- invalid superuser flags
- case-insensitive natural key lookup
- full name behavior
- direct-save email normalization
- full model validation on save

---

## Notes

`CustomUser` represents authentication identity only.

Membership-specific information belongs in `MemberProfile` in the `members` app.
