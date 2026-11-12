# Pages that answer engines can quote

Search snippets and AI answers tend to quote a passage that makes sense without the
rest of the page. Each section of a page that should be quoted needs to carry its
own subject, claim and evidence.

- **Lead with the conclusion.** The opening of the page, and of each section, says
  what the reader came for; background and history come after. A roundup names its
  recommended option where the page begins.
- **Ask the reader's question.** When a heading is phrased the way people search
  ("How long does a domain transfer take?"), put a short direct reply right under
  it, then the detail. Keep heading levels in order and in sentence case.
- **Give every compared item the same fields.** On a page that compares products,
  each entry restates the product's name with its verdict, who it suits, its
  strengths and limits, and its price. A reader, or an answer engine, that sees one
  entry alone must not attribute another product's price or gap to it.
- **Facts as text.** Prices, limits and specs in the HTML as plain text, matching
  the structured data ([page metadata](../../orbyn-ui-design/references/page-metadata.md)).
- **One number, one source.** The same count or price everywhere on the site, from
  one constant.
- **Name entities plainly:** the product, the company and what it is, in the words
  people search with; after a rebrand, mention the former name too.
- **`llms.txt` is optional.** If the site has one, generate it from the same data as
  the pages so it never disagrees with them; it does not replace crawlable pages.
- **Specific over generic.** Measurements you took, dated tests and concrete examples
  give an answer something to cite; filler intros and repeated boilerplate do not.
  For prose clean-up, use [unslop](../../unslop/SKILL.md).

Whether a page is cited is decided elsewhere and over weeks: report the structure
you shipped, never a citation you have not observed.
