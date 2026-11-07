
# Breeding App

## Purpose

Handles annual breeding reports submitted by members.

Stores summary reports per year and detailed records per species.

---

## Models

### BreedingReport

Annual report for a member.

**Fields:**

- member – reference to member profile
- year – reporting year
- status – draft / submitted / approved
- submitted_at – submission timestamp
- approved_at – approval timestamp

**Snapshot fields:**

- full_name – member name at submission time
- address, city, country – location data

**Notes:**

- One report per member per year

---

### BreedingRecord

Detailed record for one species within a report.

**Fields:**

- report – parent breeding report
- species – species reference

**Counts:**

- number_of_males – adult males
- number_of_females – adult females
- pairs_with_chicks – pairs that raised chicks
- number_of_male_offspring – male offspring
- number_of_female_offspring – female offspring
- number_of_unsexed_offspring – offspring of unknown sex

**Computed:**

- total_count_of_species – males + females
- total_count_offspring – offspring summary

**Notes:**

- One record per species per report

---

## Notes

- Reports are versioned by year
- Snapshot fields can preserve historical contact data when populated; they are not automatically copied
- Records are linked to taxonomy (species)

---

## Usage

- Used for member breeding statistics
- Basis for reports, analytics, and exports
- Can be extended with more detailed breeding metrics

## Current implementation limits

Models and admin exist; public/member submission screens, Excel import and analysis
pages are not implemented. Status timestamps are nullable and do not automatically
follow status changes. Counts default to zero; missing values, subspecies and census
line identifiers are not represented separately. Do not treat an unsubmitted report
as a confirmed zero or import section totals as a single member report.
The original individual reporting template is still unconfirmed. No census/model
redesign has been performed. `member` and `species` currently use cascading deletion.
