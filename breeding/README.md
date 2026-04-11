
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
- status – draft / submitted / approved / rejected
- submitted_at – submission timestamp
- approved_at – approval timestamp

**Snapshot fields:**

- full_name – member name at submission time
- organization – organization name
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
- offspring_count – total offspring

**Computed:**

- total_count_of_species – males + females
- total_count_offspring – offspring summary

**Notes:**

- One record per species per report

---

## Notes

- Reports are versioned by year
- Snapshot fields preserve historical data
- Records are linked to taxonomy (species)

---

## Usage

- Used for member breeding statistics
- Basis for reports, analytics, and exports
- Can be extended with more detailed breeding metrics
