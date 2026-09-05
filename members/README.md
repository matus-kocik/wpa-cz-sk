# Members App

## Purpose

Handles member profiles, membership applications, roles, membership validity,
and the approval workflow for new WPA CZ-SK members.

The app acts as the central membership layer connecting user accounts with
profiles and other member-related functionality.

---

## Models

### Role

Represents a function or role held by a member in the organization.

**Fields:**

- `name` – role name
- `slug` – unique slug

A member can have multiple roles.

---

### MemberProfile

Core model representing an approved member.

**Identity:**

- `user` – linked user account (`OneToOneField`)
- `icch_number` – unique three-digit member identifier
- `membership_type` – regular / honorary / junior
- `member_type` – person / organization
- `roles` – organizational roles (`ManyToManyField`)

**Status and validity:**

- `payment_status` – paid / unpaid
- `is_active` – automatically synchronized with payment status
- `joined_at` – original membership start date
- `valid_until` – membership validity date

**Contact and address:**

- `phone_number`
- `city`
- `street`
- `house_number`
- `postal_code`
- `district`
- `country`

**Other:**

- `notes` – internal notes
- `created_at`
- `updated_at`

**Computed properties:**

- `is_valid` – whether membership is currently valid
- `full_name` – best available member name
- `display_name` – display name for persons or organizations
- `has_projects` – whether the member participates in projects

---

## ICCH Numbers

ICCH numbers are assigned automatically when a new `MemberProfile` is created.

Numbers are generated sequentially:

- `001`
- `002`
- `003`
- etc.

The database enforces uniqueness.

Existing ICCH numbers cannot normally be changed. Manual correction is allowed
only through explicitly authorized workflows such as superuser administration.

---

## Membership Validity

`MemberProfile.save()` manages membership payment and validity.

When membership is unpaid:

- `is_active` is set to `False`.

When payment changes to paid:

- `is_active` is set to `True`.
- expired or missing membership validity is reset to March 31 of the following year.
- an existing still-valid membership can be extended by another membership period.

The validity logic is centralized in `MemberProfile`.

---

### MembershipApplication

Represents an application submitted by a prospective member.

**Applicant:**

- `first_name`
- `last_name`
- `academic_title`
- `birth_date`

**Contact and address:**

- `phone_number`
- `email`
- `city`
- `street`
- `house_number`
- `postal_code`
- `district`
- `country`

**Declaration:**

- `declaration_place`
- `declaration_date`
- `declaration_signature`

**Status:**

- `status` – pending / approved / rejected
- `initial_payment_status` – paid / unpaid
- `user` – linked user after successful approval

Only one active (`pending` or `approved`) application can exist for the same
email address.

---

## Approval Workflow

Calling `MembershipApplication.approve()`:

1. Stops immediately if the application was already processed.
2. Requires the initial payment to be marked as paid.
3. Sets the application status to `approved`.
4. Creates a new user account or reuses an existing account with the same email.
5. Creates or updates the corresponding `MemberProfile`.
6. Copies contact and address information from the application.
7. Sets the membership payment status to paid.
8. Sets `joined_at` if it has not already been set.
9. Saves the member profile, which applies membership validity rules.
10. Links the application to the user.
11. Sends the member a password setup/reset link.

The workflow is transactional and idempotent: repeated processing does not
create duplicate users or member profiles.

Creating a `MemberProfile` also triggers creation of the related
`PublicProfile` through the profiles app signal.

---

## Membership Application Form

The public application form includes:

- field validation
- email normalization
- duplicate active application protection
- Cloudflare Turnstile protection
- honeypot spam protection
- rate limiting by email and IP address
- required membership terms and GDPR consent

If email notification delivery fails after the application has been saved,
the application remains stored and the failure is logged instead of returning
an error to the applicant.

---

## Admin

Django Admin supports:

- member management
- payment status changes
- membership types
- member roles
- application approval
- initial payment status
- ICCH management for authorized superusers

Changing payment status uses the same model-level membership validity logic.

---

## Integration

The app is used by:

- `users` – authentication and user accounts
- `profiles` – public member profiles
- `projects` – project membership
- `breeding` – breeder/member relationships
- `studbook` – member-related records

---

## Tests

Tests cover the main membership workflow, including:

- paid and unpaid application approval
- idempotent approval
- reuse of existing users
- automatic ICCH assignment
- ICCH sequencing and change protection
- automatic public profile creation
- paid/unpaid active state synchronization
- initial membership validity
- expired membership renewal
- early membership renewal
- correct approval validity dates
- failed email delivery after application submission

---

## Notes

`MemberProfile` is the authoritative membership record.

`MembershipApplication` is an onboarding record and should not be treated as
an active membership until it has been paid and successfully approved.
