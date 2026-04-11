# Projects App

## Purpose

Handles projects and member participation within the organization.

Tracks project lifecycle, assigned members, and yearly participation including payments.

---

## Models

### Project

Represents a project or initiative.

**Fields:**

- name – project name
- slug – URL identifier
- description – detailed description
- coordinator – responsible member
- species – related species (optional)

**Dates:**

- start_date – project start
- end_date – project end

**Status & visibility:**

- status – planned / active / finished
- is_public – visible on website

---

### ProjectMembership

Represents a member's participation in a project for a specific year.

**Fields:**

- member – participating member
- project – related project
- year – participation year

**Payment:**

- annual_fee – fee amount
- is_paid – payment status
- paid_at – payment date

**Notes:**

- One record per member, project, and year
- Enables tracking of payments and history

---

## Notes

- Projects can have multiple members
- Membership is tracked per year
- Coordinator manages the project

---

## Usage

- Managing projects and initiatives
- Tracking member participation
- Monitoring payments
- Can be extended with roles or permissions later
