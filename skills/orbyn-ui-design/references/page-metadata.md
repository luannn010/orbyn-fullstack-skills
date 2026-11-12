# Page metadata

Use when adding or auditing titles, descriptions, canonical URLs, indexing,
social cards, icons, structured data or locale alternates. Web only; framework
neutral. Keep the diff to metadata.

## Order of work

1. Find pages with missing or wrong metadata.
2. Fix duplicates and indexing first, then the rest in the order below.
3. Make title, description, canonical and `og:url` agree.
4. Check cards on a real public URL; localhost cannot be fetched by crawlers.

## Rules

**Correctness and duplicates (critical)**
- One metadata system per page. Follow the project's existing one (framework
  metadata API, head manager, hand-written head).
- No repeated title, description, canonical or robots tag.
- Values are deterministic: no random or time-based strings.
- Escape dynamic and user-supplied text. Every page has a safe default title and
  description.

**Title and description**
- Every page has a title, in one site-wide format. Short, readable, no stuffing.
- Lead with the words people search for. Results pages cut long titles by display
  width, so keep the part that matters short (roughly 50 to 60 characters is a
  common guide). A page's title, heading, description and address should all point at one topic.
- Titles are unique and say what the page is: never "Home", "Products" or a bare
  category. Do not change a slug only to chase a year or number.
- Shareable or searchable pages have a plain-text description. No markdown, no
  quote spam.

**Images**
- Descriptive `alt` for meaningful images, empty `alt` for decoration; explicit
  `width` and `height`; a modern compressed format; lazy-load below the first
  screen, never the main image above it. Search visibility beyond this:
  [orbyn-seo](../../orbyn-seo/SKILL.md).

**Canonical and indexing**
- Canonical is the preferred URL of that page; paginated pages get their own.
- `noindex` only for private, duplicate or non-public pages. Robots tags match
  the real access intent.
- Previews and staging default to `noindex`.

**Social cards**
- Shareable pages set Open Graph title, description and image; add `twitter:card`
  (`summary_large_image` by default).
- Image URLs are absolute, with stable dimensions and aspect ratio.
- `og:url` equals the canonical. `og:type` is `website` or `article` unless
  something fits better.

**Icons and manifest**
- At least one favicon that works across browsers; an apple-touch icon where
  relevant.
- A manifest is valid and linked when used. `theme-color` is a choice, so it does
  not clash with the UI chrome.
- Icon paths are stable and cacheable.

**Structured data**
- Add JSON-LD only where it maps to content the page renders. It must be valid.
- Never invent ratings, reviews, prices or organisation details. One block per
  page unless a type needs more.

**Locale**
- Correct `lang` on the html element. `og:locale` when localised.
- `hreflang` alternates only for pages that exist; each locale canonicalises to
  itself. See [localization and RTL](localization-rtl.md).

## Boundaries

- Do not refactor unrelated code or swap SEO libraries or frameworks unless asked.
- Prefer boring, stable values over clever dynamic ones.
- A check of rendered tags is evidence for tags only; it says nothing about how
  search or social platforms will rank or display the page.
