# Deciding a screen, in order

Use when building or restyling a screen, or reviewing one that feels busy, flat or
hard to act on. Work top to bottom: each step constrains the next, and most weak UI
starts at step 4. The project's own design system supplies the values; this file
supplies the order and the defaults to fall back on.

1. **Hierarchy: what must the person do next?** Decide the one next step here. That
   is the single primary action, or there is none. Rank the rest below
   it: secondary, utility (a pill or icon), tertiary (text). Destructive is never
   the primary; in a "give something up" dialog the safe option is the primary.
2. **Amount of data: the least that answers the question.** Prefer one clear figure
   to a row of small ones. On a summary or overview page, a list shows about 5-6
   rows, then a pager or "View all". Leave out sections with nothing to show, nothing
   left to do or nothing relevant yet, and do not repeat what a heading already says.
3. **Placement.** Pick the column by page type: the project's widths, else about
   800 px to read, 1,200 px for data and 440 px for a form or flow. A section's actions sit right of
   its title, above the data they act on; paging sits below the data, outside its
   card. A control sits next to what it sets.
4. **Component.** Lists and navigation as plain rows, one group of related data as a
   card, many records as a table. Inline first; a modal only for a focused task or a
   confirm (a sheet on a phone); a toast only for a result the person cannot
   otherwise see.
5. **Surface and layer.** Decide what each thing sits on, then use the project's
   elevation tokens (the [house style](house-style/README.md) for a new app). For a
   tactile look, see [tactile treatment](tactile-theme.md#surfaces-take-their-look-from-their-parent).
6. **Type and spacing.** Rank with size, contrast and placement before weight, and
   never with colour alone. Keep one spacing grid.
7. **Colour roles.** Neutrals carry structure. Hue carries meaning: a status or an
   identity, apart from the project's accent primary and a destructive confirm.
   Status wins a clash.
8. **Motion gate.** Should it move at all? The more often it is seen, the less it
   moves. Then follow [motion](motion.md).
9. **Phone and review.** Targets and contrast per the
   [WCAG checklist](design-rules.md#wcag-22-checklist), input text per
   [mobile web](mobile-web.md), then the review below.

## Working posture

- **Smallest change that fixes it,** in the system's units (2 px, one contrast step,
  5% of opacity or scale). Do not bundle changes nobody asked for.
- **Reuse before inventing.** Find the existing recipe and match it exactly; a stock
  library primitive that lacks it is legacy, not precedent.
- **Remove before adding.** Borders, containers, separators, icons, labels over
  labels; decoration (gradients, glows, patterns) nearly always comes back out.
- **Match the neighbour.** Siblings share height, padding, radius, text size and
  contrast; treat a mismatch as a defect.
- **A rule is global.** When a pattern changes, change every instance in the same
  change.
- **Show only what this state needs.** New and returning people may see different
  pages. Never show fake data to real users, or a wrong label while loading.

## Review at zoom

Before calling it done, check at 4-8× zoom in every supported theme, with worst-case
data and every state (empty, loading, error, long, short). Look for 1 px seams,
double borders, an inner radius that is not the outer minus the border, wrapped or
cropped labels, layout that jumps when data arrives, and siblings that do not match.

Report in plain bullets: what changed, where, and anything that conflicts with an
earlier rule.

## Worked example

A usage page: what has the account used, and is anything about to run out?

1. No primary most of the time; "Upgrade plan" becomes the one primary only near a
   limit. Export and the date range are secondary.
2. One figure with its meter, one period of bars, the top 5 items with "View all".
3. A data-width column; range and Export right of the section title.
4. A card for figure and chart, a table for items, a segmented control for the range.
5. Before: six stat tiles and two primaries. After: one figure, one primary shown
   only when it applies, and the pager moved below the table's card.
