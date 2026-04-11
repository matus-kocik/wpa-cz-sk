
# Articles App

## Purpose

Handles articles, educational content, and publications.

Supports categorization, contributors, SEO, and publishing workflow.

---

## Models

### Category

Used for grouping articles.

**Fields:**

- name – category name
- order – display order
- slug – URL identifier

---

### Contributor

Represents an author or contributor.

**Fields:**

- name – contributor name (if not a member)
- member – linked member (optional)
- role – author / photographer / editor / etc.

**Notes:**

- At least one of name or member must be set

---

### Article

Main content model.

**Fields:**

- title – article title
- category – article category
- summary – short description

**Content & media:**

- main_image – main image
- pdf_file – optional PDF version
- pdf_title – description of PDF

**Relations:**

- contributors – authors and collaborators
- species – related species
- related_articles – linked articles

**Publishing:**

- publication_date – publish date
- is_published – visibility (from PublishableModel)
- published_at – timestamp (auto set)

**External source:**

- published_in – source name
- published_in_date – external publish date
- published_in_url – external link

---

## Notes

- Articles support SEO via SEOModel
- Publishing is handled via PublishableModel
- Designed for blog, guides, and expert content

---

## Usage

- Website articles and blog
- Educational content and guides
- Linking species to content
- Can be extended with comments or ratings later
