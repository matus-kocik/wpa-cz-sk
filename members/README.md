
# Members App

## Purpose

Handles member profiles and membership applications.

Acts as the central identity layer for all users participating in the WPA system.

---

## Models

### MemberProfile

Core model representing an approved member.

**Fields:**

- user – linked user account
- icch_number – unique member identifier
- membership_type – type of membership
- position – role in organization (optional)

**Status & validity:**

- is_active – whether member is active
- payment_status – paid / unpaid / pending
- joined_at – membership start date
- valid_until – membership validity

**Contact & address:**

- phone_number – contact phone
- city, street, house_number – address
- postal_code – ZIP code
- district – region
- country – country code

**Other:**

- notes – internal notes

**Computed:**

- is_valid – whether membership is currently valid
- full_name – best available name

---

### MembershipApplication

Application submitted by a user to become a member.

**Fields:**

- user – linked user (optional)
- first_name, last_name – applicant name
- academic_title – optional title
- birth_date – date of birth

**Contact & address:**

- phone_number – contact phone
- email – email address
- city, street, house_number – address
- postal_code – ZIP code
- district – region
- country – country code

**Declaration:**

- declaration_place – place of signature
- declaration_date – date of declaration
- declaration_signature – signature text

**Status & payment:**

- status – pending / approved / rejected
- initial_payment_status – payment state

---

## Notes

- MemberProfile is the central model used across the system
- MembershipApplication handles onboarding workflow
- Approval process creates or updates user and member profile

---

## Usage

- User onboarding and registration
- Membership management
- Payment tracking
- Identity reference for other apps (profiles, breeding, projects, studbook)
