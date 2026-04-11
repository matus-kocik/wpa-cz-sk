
# Users App

## Purpose

Provides custom user model and authentication logic.

Replaces Django default user with email-based authentication and extended validation.

---

## Models

### CustomUser

Custom user model used across the system.

**Fields:**

- email – unique user email (used for login)
- first_name – first name
- last_name – last name
- email_verified – whether email is verified

**Permissions & status:**

- is_active – active account
- is_staff – admin access
- is_superuser – full permissions

**Timestamps:**

- date_joined – account creation date

**Computed:**

- full_name – combined first and last name

---

## Notes

- Uses email as USERNAME_FIELD
- Email is normalized to lowercase
- Model validation is enforced via full_clean() on save
- Case-insensitive email lookup via database index

---

## Usage

- Authentication and login
- Linked to MemberProfile (members app)
- Used as identity layer for all users
- Can be extended with additional auth features (2FA, OAuth, etc.)
