# Profiles App

## Purpose

Handles public profiles of members in the WPA system.

Stores contact information, breeding focus, and visibility settings for each member.

---

## Models

### PublicProfile

Public-facing profile linked to a member.

**Fields:**

- member – reference to member profile (OneToOne)
- display_name – name shown publicly
- bio – short introduction
- avatar – profile image
- location – city or region
- public_email – visible email
- phone – contact phone number
- website – external website link
- specialization – breeding specialization
- breeding_focus – detailed breeding info
- years_of_experience – number of years in breeding

- species – related species (ManyToMany)

**Social:**

- facebook_url – Facebook profile
- youtube_url – YouTube channel

**Visibility settings:**

- is_public – profile is visible
- show_email – display email
- show_phone – display phone
- show_location – display location
- show_breeding – display breeding info

**Other:**

- notes – internal notes (not public)

---

## Notes

- Each member has exactly one public profile
- Visibility flags control what is shown on the frontend
- Designed for public directory of breeders

---

## Usage

- Used for public member listings
- Connected with taxonomy (species)
- Can be extended with more social or contact fields later
