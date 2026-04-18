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
- public_email – visible email
- phone – contact phone number
- website – external website link
- additional_info – additional public information about the breeder
- other_species – other animals bred (free text, e.g. pigeons, parrots)

- species – related species (ManyToMany)

**Social:**

- facebook_url – Facebook profile
- youtube_url – YouTube channel
- instagram_url – Instagram profile

**Visibility settings:**

- is_public – profile is visible
- show_email – display email
- show_phone – display phone
- show_location – display location
- show_avatar – display profile image
- show_bio – display bio
- show_social – display social links
- show_species – display species list
- show_other_species – display other species
- show_additional_info – display additional information
- show_website – display website

**Other:**

- notes – internal notes (not public)

---

## Notes

- Each member has exactly one public profile
- Each data section has a corresponding visibility flag (show_*) controlling frontend display
- Designed for public directory of breeders

---

## Usage

- Used for public member listings
- Connected with taxonomy (species)
- Can be extended with more social or contact fields later
