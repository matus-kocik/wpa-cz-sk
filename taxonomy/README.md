
# Taxonomy App

## Purpose

Defines biological classification used across the system.

Provides hierarchy (Family → Genus → Species → Subspecies) and stores descriptive, biological, and breeding-related data.

---

## Models

### Family

Top-level biological group.

**Fields:**

- name – common name
- latin_name – scientific name
- slug – URL identifier

---

### Genus

Belongs to a family and groups related species.

**Fields:**

- name – common name
- latin_name – scientific name
- family – parent family

---

### Species

Main taxonomy entity used across the project.

**Fields:**

- genus – parent genus
- latin_name – scientific name
- czech_name – common name
- authority – naming authority

**Biology:**

- maturity – age of maturity
- length – body length
- weight – body weight
- clutch – number of eggs
- incubation – incubation period

**Conservation:**

- status_in_nature – IUCN status
- status_in_captivity – notes about captive breeding

**Breeding & care:**

- ring_size – ring size (mm)
- breeding_difficulty – breeding difficulty

**Other:**

- distribution – geographic range
- habitat – natural habitat
- notes – additional notes

**Media:**

- main_image – primary image
- secondary_image – additional image
- videos – YouTube links
- images_url – external gallery link

---

### Subspecies

Optional subdivision of a species.

**Fields:**

- species – parent species
- latin_name – scientific name
- note – additional info

---

## Notes

- Species is the central model used across multiple apps
- Hierarchy is simple and based on ForeignKeys
- Designed for both scientific and practical breeding use

---

## Usage

- Referenced in studbook, breeding, articles, projects, and events
- Used for filtering, categorization, and linking data
- Supports both educational content and real breeding data
