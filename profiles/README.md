# Profiles App

## Purpose

Handles public profiles of members in the WPA CZ-SK system.

The app stores public breeder information, contact details, breeding focus, media, and visibility settings for each member.

---

## Models

### PublicProfile

Public-facing profile linked one-to-one with `MemberProfile`.

**Main fields:**

- `member` – reference to member profile (`OneToOneField`)
- `display_name` – name shown on the public profile
- `bio` – information about the breeder
- `avatar` – profile image
- `species` – related species (`ManyToManyField`)
- `other_species` – other bred species stored as free text
- `additional_info` – additional public information
- `notes` – internal notes, not intended for public display

**Contact fields:**

- `public_email` – public contact email
- `phone` – contact phone number
- `website` – external website

**Social links:**

- `facebook_url` – Facebook profile
- `instagram_url` – Instagram profile
- `youtube_url` – YouTube channel or video

**Visibility settings:**

- `is_public` – controls whether the profile itself is publicly accessible
- `show_email`
- `show_phone`
- `show_location`
- `show_website`
- `show_social`
- `show_bio`
- `show_gallery`
- `show_videos`
- `show_avatar`
- `show_species`
- `show_other_species`
- `show_additional_info`

**Computed properties:**

- `primary_species` – returns the first associated species
- `additional_info_display` – returns profile additional info with member notes as fallback
- `location_display` – returns city and country from `MemberProfile`

The profile URL is generated from its unique slug.

---

### ProfileGallery

Stores gallery images belonging to a public profile.

**Fields:**

- `profile` – related `PublicProfile`
- `image` – uploaded gallery image
- `caption` – optional image description
- `is_primary` – marks the main gallery image
- `created_at` – creation timestamp

A profile can contain a maximum of **6 gallery images**.

Only one image per profile can be marked as primary.

When an image is replaced or deleted, the old image file is removed from storage.

---

### ProfileVideo

Stores YouTube links belonging to a public profile.

**Fields:**

- `profile` – related `PublicProfile`
- `url` – YouTube URL
- `title` – optional title
- `created_at` – creation timestamp

A profile can contain a maximum of **3 videos**.

---

## Forms

`PublicProfileForm` provides editing of profile information and visibility settings.

Gallery and video management use inline formsets:

- `GalleryFormSet` – maximum 6 images
- `VideoFormSet` – maximum 3 videos

---

## Views

### Public profile detail

Public profiles are accessible through their slug.

- Anonymous visitors can access public profiles.
- Owners can access their own profile even when it is private.
- Other users cannot access a private profile.

### Profile editing

Profile editing requires authentication.

A member edits their own `PublicProfile`.

The edit view also handles gallery and video formsets.

### Member listing

The app provides the member listing view used by the public member directory.

---

## Profile creation

A `PublicProfile` is automatically created for a member through the profiles signal handling.

Each member is expected to have exactly one public profile.

---

## Integration

The app is connected with:

- `members` – member identity, location, and membership data
- `taxonomy` – species associated with breeders
- Django Admin – profile, gallery, and video management

---

## Tests

The app contains tests covering core profile behavior, including:

- automatic profile creation
- profile model behavior
- gallery limits
- video limits
- primary gallery image constraints
- public/private profile access
- owner access to private profiles
- protection against access to another member's private profile

---

## Notes

- Private member data remains in `MemberProfile`.
- `PublicProfile` controls information intended for the public-facing breeder directory.
- Visibility is controlled independently for individual profile sections.
- Gallery and video limits are enforced both by forms and model validation.
