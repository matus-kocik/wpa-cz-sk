
# Taxonomy App

## Purpose

Defines biological classification used across the system.

Provides hierarchy (Family → Genus → Species → Subspecies) and stores descriptive, biological, and breeding-related data.

---

## Models

### Family

Top-level biological group.

**Fields:**

- latin_name – scientific name
- czech_name – Czech name
- slovak_name – Slovak name
- english_name – English name
- german_name – German name
- slug – URL identifier

---

### Genus

Belongs to a family and groups related species.

**Fields:**

- latin_name – scientific name
- czech_name – Czech name
- slovak_name – Slovak name
- english_name – English name
- german_name – German name
- family – parent family

---

### Species

Main taxonomy entity used across the project.

**Fields:**

- genus – parent genus
- latin_name – scientific name
- czech_name – Czech name
- slovak_name – Slovak name
- english_name – English name
- german_name – German name
- authority – naming authority
- authority_year – year of description
- is_active – active flag

**Biology:**

- maturity – age of maturity
- length_male_min / length_male_max – male length (cm)
- length_female_min / length_female_max – female length (cm)
- weight_male_min / weight_male_max – male weight (g)
- weight_female_min / weight_female_max – female weight (g)
- clutch_min / clutch_max – clutch size (eggs)
- clutch_note – additional clutch info
- incubation_min / incubation_max – incubation period (days)
- incubation_note – additional incubation info

**Conservation:**

- status_in_nature – IUCN status
- status_in_captivity – notes about captive breeding
- population – population in CZ/SK

**Breeding & care:**

- ring_size – ring size (mm)
- breeding_difficulty – breeding difficulty

**Other:**

- distribution – geographic range
- habitat – natural habitat
- subspecies_note – monotypic / polytypic
- notes – additional notes

**Media:**

- main_image – primary image
- links – external links (YouTube, Facebook)

---

### Subspecies

Optional subdivision of a species.

**Fields:**

- species – parent species
- latin_name – scientific name
- czech_name – Czech name
- slovak_name – Slovak name
- english_name – English name
- german_name – German name

---

### SpeciesLink

External links related to a species.

**Fields:**

- species – parent species
- type – link type (YouTube, Facebook)
- url – external URL
- title – optional title

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
