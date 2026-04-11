# Common App

## Purpose

Provides reusable abstract base models and utilities used across the whole project.

This app helps keep code consistent, clean, and avoids duplication.

---

## Included Models

### TimeStampedModel

Adds automatic timestamps to models.

**Fields:**

- created_at – date and time when object was created
- updated_at – date and time of last update

---

### SlugModel

Provides an auto-generated unique slug field.

**Fields:**

- slug – URL-friendly unique identifier

**Behavior:**

- If slug is empty, it is generated automatically from name-like fields

---

### SEOModel

Adds basic SEO fields.

**Fields:**

- meta_title – SEO title
- meta_description – SEO description
- meta_keywords – comma-separated keywords

---

### SoftDeleteModel

Implements soft delete functionality.

**Fields:**

- is_deleted – marks object as deleted
- deleted_at – timestamp of deletion

**Behavior:**

- Default queries return only non-deleted records
- Hard delete is still possible when explicitly requested

---

### PublishableModel

Handles publication state.

**Fields:**

- is_published – controls visibility
- published_at – publication timestamp

**Behavior:**

- Automatically sets published_at when publishing for the first time

---

## Notes

- All models are abstract and meant to be inherited
- Designed for consistency across all apps
- Keeps business logic centralized and reusable
