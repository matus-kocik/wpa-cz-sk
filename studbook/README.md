
# Studbook App

## Purpose

Core registry of individual birds.

Tracks identity, lineage (parents), ownership, and full lifecycle history.

---

## Models

### BirdRecord

Represents a single bird.

**Fields:**

- species – species reference
- member – current owner (member)
- name – optional name
- ring_number – identification ring
- sex – male / female / unknown
- status – active / sold / dead / etc.

**Lineage:**

- father – reference to male parent
- mother – reference to female parent

**Notes:**

- Core entity of the system
- Parents are optional but validated when provided

---

### BirdEvent

Timeline event for a bird.

**Fields:**

- bird – related bird
- event_type – type of event (birth, death, transfer, etc.)
- event_date – date of event
- notes – optional description

**Usage:**

- Builds full lifecycle timeline

---

### HealthRecord

Health-related entry for a bird.

**Fields:**

- bird – related bird
- record_date – date of record
- diagnosis – health issue
- treatment – applied treatment
- veterinarian – optional vet info

---

### CareRecord

Routine care entry.

**Fields:**

- bird – related bird
- care_type – feeding, treatment, check, etc.
- care_date – date of care
- notes – optional description

---

### TransferRecord

Ownership or location transfer.

**Fields:**

- bird – related bird
- transfer_type – sale / gift / exchange / move
- transfer_date – date of transfer
- from_member – previous owner
- to_member – new owner

---

## Notes

- BirdRecord is the central model
- Other models extend it with timeline and domain data
- Lineage enables basic genealogy tracking

---

## Usage

- Studbook registry for all birds
- Tracking ownership and movement
- Recording health and care history
- Basis for genealogy and reporting
