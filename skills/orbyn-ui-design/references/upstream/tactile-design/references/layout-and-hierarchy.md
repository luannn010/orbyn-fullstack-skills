# Layout and hierarchy

Where things go, how big they are relative to each other, how much to show, and how the eye is led. `ink-N` is a neutral step; values are defaults.

## 1. How hierarchy works

**Hierarchy comes from contrast steps, not from weight, big size jumps or colour.**

The ladder of emphasis, strongest first:

1. **Primary fill** (ink-12): the one primary action.
2. **White with a shadow**: secondary actions, cards, the chosen option.
3. **Fill only** (ink-2 to ink-4): selected rows, wells, quiet chips.
4. **Text only**: links, ghost actions, labels.

For type, one weight everywhere. Rank text with **a size step plus an ink step**:

| Ink | Role |
|---|---|
| ink-12 | titles, values, labels, the variable part of a line |
| ink-11 | descriptions, body, row icons, a fixed prefix, meter labels |
| ink-10 | labels under figures, "/ total" suffixes, placeholders, chevrons, "(optional)", footnotes, pager counts |
| ink-9 | group titles, empty-state text, taglines, leading icons |
| ink-6 | 0.5px hairlines |

Text a user must read to act passes 4.5:1. Where your ink-9 or ink-10 doesn't (default sand doesn't), tune it or use ink-11 for that text. See [tokens.md](tokens.md) §1.

| Size | Use |
|---|---|
| 32/40, −0.02em | display title, one hero stat |
| 24/32 | display figures |
| 20/28 | section titles and in-column page titles |
| 16/24 | card, step, dialog and alert titles ("a step up" from body) |
| 13/20 | body, descriptions, controls, the top-strip page title |
| 12/16–20 | badges, footnotes, meta |
| 11 | counts, the button key chip; rare |

**Mixed-ink lines** lead the eye to what changes:
- A set filter: label ink-10, value ink-12 ("Status **Failed**").
- A hint: "Filter by" ink-11, the key and value ink-12.
- A two-tone display title: lead words ink-11, the key noun ink-12 ("Create your first **project**"). Taglines: body ink-9, one key word ink-12.

**Colour carries meaning, never rank.** Success green only when something is live and the count is above 0. Danger red for errors. Info blue, warning yellow. Identity hues for a category or tier only. Keep highlights inside text monochrome (ink-12), not hued. Roles and the collision rule are in [tokens.md](tokens.md) §4.

**Don't repeat what's already said.**
- A card under a heading doesn't repeat the heading's name.
- View switches say "Live" and "All", not "Live projects" and "All projects", when the page title already says it. They use the segmented toggle; there are no underline tabs.
- A table's Actions header appears only once a row exists.

**No eyebrows.** No small label above a title, no "Step 1 of 4" above a progress bar (the bar's own accessible label says it), no warning icon before an alert title, no subtitle on a step that has nothing to add.

## 2. Columns

| Page type | Column | Why |
|---|---|---|
| Read top to bottom (home, overview, guides) | 800px, centred | a comfortable line for 13px text and a single scan path |
| Data (tables, charts, usage, plans) | 1200px | tables and charts need width |
| Form, flow, sign-in | 440px (a sign-in card: 464px with 32px padding) | one field per line, eyes don't travel |
| Rail | 292px | widest nav label + 16px icon + 6px gap + row and rail padding, rounded up to 4px |

- **The widths follow the type.** If "Typeface fit" in [tokens.md](tokens.md) scales the type sizes by a factor f, scale these column widths by f too. Cap prose at 70ch whatever the column.
- A wrapped card column adds its own inner padding to the width (800 + 2 × 12 = 824) so its content lines up with an 800px column elsewhere.
- **Markers hang outside the column.** When there's room (container at least 800 + 2 × 48px), step markers sit in the margin so every line of text starts on the page's left edge and the column stays centred on the text. Narrower, the markers move inside.
- **Room at the ends:** 48px above the first title, 64px at the foot of the page, 16px around the main area on desktop.

## 3. Rhythm

The default section, summarised: **20px titles over 13px lines, 24px apart, in 32px of room.**

| Gap | Value |
|---|---|
| Section title to its description | 6px |
| Heading block to content | 24px |
| Section padding | 32px above and below (64px from one section's content to the next title) |
| Display title extra room below | +32px compared with a section title |
| Inside a step: title block to content | 16px |
| Step to step | 32px |
| Between fields or form blocks | 20px |
| Card padding | 24px (20px on a phone) |
| Figure to its chart | 16px |
| Divider between groups | full-width 0.5px hairline, 32px clear on each side |

**Title-to-description gap ladder:** 2px under a 16px card title, 4px under a 20px page title in app chrome, 6px under a section title, 8px under a display title. The gap between a title and a following notice equals its title-to-description gap. Tune these in 2px steps.

**Spacing ladder:** 2, 4, 6, 8, 12, 16, 20, 24, 32, 48, 64. Nudges are 1, 2 or 4px; blocks move in 8, 16 or 32px.

**Bar and row heights** are line height + 2 × padding: 36 = 20 + 2 × 8, 38 = 20 + 2 × 9, 46 = 20 + 2 × 13, and a 52px strip is a 36px control + 2 × 8px inset. Recompute them this way if the line height changes.

## 4. Proportion rules

- **Equal padding.** Top and bottom padding match the sides on strips, bars, cards and selectors. An icon button in a bar is as wide as the bar is tall.
- **Match the neighbour.** Input = button = toggle = selector height. Dropdown rows = button height. A selected row inside a menu is as wide as the search field above it. Cards in a row share one height.
- **Space above equals space below** for anything placed between two things.
- **One left edge.** All text in a column starts on the same line. When centring, centre the text, not the markers beside it. Table cells align left.
- **Icons** align to the first line of text, or centre on the title-plus-description block as a whole.
- **Numbers in a table align left** with every other cell, in tabular figures. **Elsewhere a value set against its label aligns right** (a stat row, a meter's amount). A badge may run slightly past the padding to keep that line. In a row of pills, align the text inside them, not the pills.
- **Fixed ratios.** Action cells are 1:1. Media and players are 16:9. Thumbnails share their card's ratio. Logos in a set get equal visual weight (nudge each 2–10%).
- **Hug or fill.** Table columns, toggles and action cells hug their content, up to the caps in §7, so text doesn't wrap. Inputs and dropdowns in a modal fill the width. Desktop dialog buttons hug; phone action stacks fill.
- **Nested radius = outer minus border.** No double borders.

## 5. Placement

| Element | Goes |
|---|---|
| Page title | 13/20 ink-12, centred in the top strip, absolutely positioned so it doesn't move with the switcher. A 20/28 title is only for an in-column page or section heading. |
| Breadcrumbs | top strip, left. They replace back buttons. Parent crumbs ink-10, small ink-8 chevrons. |
| Page-level actions | top strip, right |
| Section actions | right of the section title, vertically centred on title + description together (`flex items-center justify-between gap-4`) |
| On a phone | under the title, full width, 16px under the description, 24px before the content |
| **Actions vs data** | **always above the data they act on, never under it** |
| Paging | below the data, outside its card: count left, Previous / Next right |
| "View all" | after the section's content |
| Filters | one row beside the toggles, search at the right; scrolls sideways on a phone, never wraps |
| A control that sets something | right next to (or right above) the thing it sets |
| Rail | switcher and search pinned top; notices and account pinned at the foot |
| Order of a pair, desktop | secondary first, primary at the far right |
| Order of a pair, phone | primary on top for pages; confirm on top for dialogs and flows |

## 6. How much data to show

**The least that answers the question the page exists for.**

| Where | Rule | Default (source example) |
|---|---|---|
| A summary list | 5–6 rows, then a pager under the card or "View all" | |
| A full list page | about the rows that fit one viewport at the row height, rounded to 10, 20, 25 or 50 | 20 at 38px rows |
| A period breakdown | one natural period of the data's unit: 24 hours, 7 days, 30 days, 12 months | 30 days |
| A card grid | a whole multiple of the column count, 2–3 rows | 6 updates (2 × 3) |
| Skeleton rows | the page size, at most 10 | |
| Stats on a phone | rows (label left, value right, hairlines between), so six stay a glance | |

- **Prefer one strong metric.** A big number with a small label under it beats a grid of small numbers.
- **Remove duplicate widgets.** Fold secondary numbers into the card they belong to.
- **Gate by state.** New and returning users can see different pages. Until the user has done the first key thing, the steps to do it can be the whole page. Afterwards the remaining steps shrink to one section at the top, above the usual content, and leave once done.
- **Progressive disclosure.** Show the next steps only after a choice is made; the next marker waits at 50% opacity. "Other" opens an inline field.
- **Hide rather than delete.** Sections and invitations show only if they exist; completed steps are hidden; optional work stays out of the critical path.
- **Never show fake data to users.** Mock data belongs in previews only.

**Number and date formatting**
- Format with the user's locale through the Intl APIs. The examples show the pattern, not a fixed format.
- Money: `Intl.NumberFormat(locale, { style: "currency", currency, minimumFractionDigits: whole ? 0 : 2 })`, so whole amounts drop ".00". At most 3 decimals elsewhere.
- Dates: `Intl.DateTimeFormat(locale, { weekday: "short", day: "numeric", month: "short" })` ("Fri, 24 Oct" in en-GB). Drop the time zone on a phone.
- Long IDs: truncated to about 8 characters, with the full value in a tooltip and a copy action.
- "0:00" for durations that haven't started; `tabular-nums` wherever numbers line up.

## 7. Worst-case data

Design for the shortest and longest real values, not the sample.

| Case | Rule |
|---|---|
| Free text in cells (names, emails, URLs) | one line; hug up to 32ch (about 240px at 13px), then end-truncate with "…"; full value in a tooltip and still selectable |
| Names in the rail, breadcrumbs, modal titles | the same rule at the container's width |
| Descriptions in cards | clamp to 2 lines |
| Badges | at most 24ch |
| Figures over 6 digits | `Intl.NumberFormat(locale, { notation: "compact" })` (1.2M), full value in a tooltip |
| Missing or null value | an ink-9 en dash |
| Counts | plural forms via `Intl.PluralRules` |
| Flex children that hold text | `min-width: 0`, so truncation can happen |

Preview each component with the shortest and longest real values before shipping.

## 8. Figures and meters

- **Figure:** 24/32 ink-12 number, with a 13/20 ink-10 label directly under it (no gap). The range goes in brackets after the label: "Runs (24h)". Two figures side by side sit 32px apart.
- While loading, the number shows a pulsing ink-10 dash; the label stays put.
- **Meter:** label (ink-11) and amount (ink-12 with an ink-10 "/ total") on one line, then a 10px bar 12px under it. Every bar is 10px. An amount of 0 shows no fill; anything above 0 shows at least a 2% sliver. A bar takes its identity hue. It turns red at 10% remaining or below (or the product's own threshold), and only for quantities that run down, never for progress.
- **Chart type:** bars for counts per period and for status or health; a line for continuous measures where the trend is the question (latency, a balance over time).
- **Axis labels:** short weekday names from `Intl.DateTimeFormat(locale, { weekday: "short" })`, shown in capitals with `text-transform: uppercase` and +0.02em tracking (MON TUE). Skip the capitals for scripts without case.
- Hovering between ticks shows that exact time and dims the nearest ticks. No clipping or overflow.

## 9. Steps and markers

- **Marker:** a 32px disc, number 16/24 ink-11, white + `--shadow-button` (in dark ink-3 with the same token: its solid 0.5px outline and black drop), nudged to centre on the 24px title line.
- **Connector:** 0.5px ink-6 line, 8px under the marker, 12px above the next.
- Marker to text: 16px (12px on a phone). All steps the same height.
- **States:** done = green-9 disc with a tick in green-contrast; waiting = a slowly turning dashed ring with a shimmer on the title; counting = a segmented ring (accent-9 done, accent-6 to go).
- **Progress bar:** 6px segments, 6px apart, ink-4 track, ink-12 fill.
- A step that can't run yet shakes where it stands and says why.
- Celebrate the moment of finishing (a short beat, then the card fades out), not the state. Never replay it on reload.

## 10. Badges beside titles

8px from the title. A 20px pill normally; beside a 20px title it goes one size up (24px, 13px text). A badge used as a heading uses 14px. Full spec in [buttons-and-controls.md](buttons-and-controls.md).

## 11. Empty, loading and error states

**Empty:** a bare centred panel, no table chrome. Ink-2 fill, 44px padding, an 18px icon (24px on a phone, not in a box), two lines in ink-9 (ink-11 where ink-9 misses 4.5:1): what's missing, then what to do. "No projects yet." / "Create a project and it will appear here." Keep each line to one line.

**Failed load:** the empty-state layout with two lines ("Couldn't load runs." / what to try) and one secondary "Try again" button. Field errors are in [buttons-and-controls.md](buttons-and-controls.md).

**Loading:**
- Use the empty-state layout with a spinner in place of the icon and no description, or skeletons that keep labels and column widths in place and replace only the values.
- Hold steps and panels at a minimum height so buttons stay put.
- Cycling text shares one grid cell sized to its longest option.
- Never show a wrong label while loading ("Loading…", disabled, until the real state is known). Say what's happening honestly: "Adding funds to your balance…" until it has actually landed.

## 12. Copy

- **Sentence case, short, plain.** Descriptions are usually one sentence with a full stop, and they must help: explain the mechanism, not restate the title. "Each key is pinned to one project."
- **Buttons are a verb plus an object:** "Create project", "View all projects", "Edit limits", "Copy command". "Done", not "Completed".
- **Loading labels** end in a real ellipsis: "Opening…".
- **Small additions:** "(optional)" in ink-10; a range in brackets after a label.
- **Capitalisation:** capitals for product names and acronyms ("API"); lowercase common nouns inside phrases ("Create a key"); a capital first letter in placeholders.
- **Value the user holds:** use the product's own word for its unit of value, phrased from the holder's side ("your balance"). Never frame value they hold as "free".
- **No em dashes** in UI copy; use a plain dash or a full stop. No three dots. Footnotes break after each full stop.
- **Shorter on a phone:** drop qualifiers the section title already supplies ("Included" for "Included in your plan"), and use short forms ("org" for "organization"). Whole amounts drop ".00".
- **Confirmations state the consequence:** "This will remove access for 3 members."
