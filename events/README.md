
# Events App

## Purpose

Handles events and activities within WPA sections.

Stores event details such as schedule, location, organizer, and visibility.

---

## Models

### Event

Represents a single event.

**Fields:**

- title – event title
- slug – URL identifier
- description – event description

**Dates:**

- start_date – start date and time
- end_date – end date and time

**Location & organizer:**

- location – place of the event
- organizer – organizer name

**Classification:**

- section – WPA section (CZ-SK, DE, etc.)
- species – related species (optional)

**Visibility:**

- is_public – visible on website
- is_featured – highlighted event

---

## Notes

- Events can be filtered by section and date
- Featured events can be displayed on homepage
- Supports both local and international activities

---

## Usage

- Event listings and calendar
- Homepage highlights
- Filtering by region or species
- Can be extended with registration or attendance tracking later
