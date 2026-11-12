# Surfaces and layering

How things sit on top of each other, and how that reads in light and in dark. Shadow and colour tokens are defined in [tokens.md](tokens.md).

## Tactility borrows from its parent

A tactile thing has three parts: a fill, an edge and a drop. None of them is a fixed value. Each is taken from the surface the thing sits on, its parent, so the same control reads equally tactile on a panel, a card, a rail, a table row, a sheet or a tinted surface, in both themes.

| Part | Light | Dark | Rule |
|---|---|---|---|
| Fill | `--surface-top` | parent + 2 steps (controls), parent + 1 step (cards) | The step-shift rule: the same contrast against every ground. |
| Edge | a 1px `rgb(ink / .08)` ring over whatever is beneath (`.07` on cards and modals) | one solid 0.5px outline, lighter than the fill, the same colour all round: three steps above the fill on controls and toggles (ink-6 over ink-3 on the panel, ink-7 over ink-4 on a card, table or overlay), ink-7 on menus and modals, ink-6 on cards | Light adapts through alpha. Dark adapts per surface: each surface class redeclares the outline step, so it moves with the fill. |
| Drop | `rgb(ink / a)` | `rgb(0 0 0 / a)` | Always darker than the parent, never lighter. A lighter drop reads as a glow. |

- **The primary's ring is its parent's colour.** In light, `--shadow-primary` is a 1px ring in the local surface colour, so the fill reads a pixel smaller and never halos on an ink-2 rail. In dark, its 0.5px outline is its own fill colour, over the black drop.
- **A badge borrows from itself.** Its edge is a darker shade of its own colour, so each hue tints its own edge. Light: the button's ring and drop drawn in `currentColor` (14% ring, 16% drop). Dark: a `color-mix(in srgb, currentColor 34%, #000)` outline and the black drop. A hue's light text colour is never a blurred shadow in dark.
- **White on white takes its edge from the ring and drop, never from a fill change.** A secondary button or a neutral badge on a white card stays white.
- **The tactile tokens are built from working steps.** A variable resolves where it is declared, so `--line`, `--shadow-primary`, `--shadow-button` and the other tactile shadows are redeclared on every surface class, or the edge stops following its parent. Implementation in [tokens.md](tokens.md) §3.

| Example | Light | Dark |
|---|---|---|
| Secondary button on a card | white on the white card; the ring and drop draw the edge | ink-4 on the ink-2 card, 0.5px ink-7 outline, black drop |
| Control on the rail | white on the ink-2 rail with the same 8% ring, which reads on ink-2 without retuning; the primary's ring turns ink-2 | two steps above the rail, an outline three steps above its fill, the black drop |
| Button in a table row | white on the white row, ring and drop | ink-4 on the ink-2 row, 0.5px ink-7 outline, black drop; two steps more on hover |
| Neutral badge on a white card | white, `--shadow-button` | one step above the card (ink-3 on ink-2), `--shadow-button` (solid outline, black drop) |
| Tinted badge | hue-3 fill, hue-11 text, `--shadow-badge` (ring and drop tinted from its own text) | hue-3 fill, hue-11 text, `--shadow-badge` (a darker shade of its own colour, black drop) |

## 1. The layer stack (bottom to top)

| Layer | Light | Dark | Notes |
|---|---|---|---|
| **Ground** (window, rail) | ink-2 | a stop below ink-1 (#080807) | The rail sits straight on the ground. No border; the panel's edge divides them. |
| **Panel** (page body) | `--surface-top`, `--shadow-panel` | ink-1, `--shadow-panel` (darker) | Floats 8px off the window's top, right and bottom; flush against the rail; radius 8. Pages scroll inside it. |
| **Raised** (cards, buttons, chosen toggle option) | `--surface-top`; `--shadow-button` on controls, `--shadow-card` on cards | parent + 1 step (cards) or + 2 steps (controls); one solid 0.5px outline (ink-6 on cards; on controls three steps above the fill, ink-7 on a card) and a tight black drop | A card is the button's ring and 1px drop plus one short drop. |
| **Well** (fields, toggle tracks) | one step darker than its surface | one step lighter | Sinks instead of rising. |
| **Table** | white rows, 0.5px ink-6 frame and dividers, `--shadow-table` | ink-2 rows, 0.5px ink-5 frame and dividers, `--shadow-table` | No stripes on a short table. The frame stands in for the button's ring; the drop sits under it. |
| **Overlay** (menu, popover, modal, side panel, search) | `--surface-top`, shadow by level; the shadow's ring is the edge, no border | ink-2, a solid 0.5px ink-7 outline and black drops by level | Each level is the button's ring and 1px drop plus one short drop, never a big soft blur. |
| **Toast** | tinted pill | tinted pill | Above everything. |

## 2. Elevation is expressed differently per theme

**Light:** the ground is ink-2 and anything raised is the white surface top with a 1px ring and a tight drop. Lift = white + shadow.

**The ladder** ([tokens.md](tokens.md) §6): every level is the button's ring and 1px drop, plus at most one short, tight drop. No big soft blurs anywhere.

| Level | Light |
|---|---|
| Control (`--shadow-button`) | `0 1px 2px 0 rgb(ink / .12), 0 0 0 1px rgb(ink / .08)` |
| Table (`--shadow-table`) | `0 1px 2px 0 rgb(ink / .12)`, under its 0.5px frame |
| Card (`--shadow-card`) | `0 0 0 1px rgb(ink / .07), 0 1px 2px 0 rgb(ink / .12), 0 3px 4px -2px rgb(ink / .08)` |
| Menu, dropdown (`--shadow-menu`) | `0 0 0 1px rgb(ink / .08), 0 1px 2px 0 rgb(ink / .12), 0 4px 8px -4px rgb(ink / .16)` |
| Modal (`--shadow-modal`) | `0 0 0 1px rgb(ink / .07), 0 1px 2px 0 rgb(ink / .14), 0 6px 8px -4px rgb(ink / .14)` |

**Dark:** a shadow alone doesn't read on a dark ground. A raised thing is told by being **lighter** and by **one solid 0.5px outline**, the same colour all round, with a tight black drop under it.

| Thing | Fill | Edge and drop |
|---|---|---|
| Card | parent + 1 (ink-2 on the panel) | `0 0 0 0.5px ink-6, 0 1px 2px 0 rgb(0 0 0 / .5), 0 3px 4px -2px rgb(0 0 0 / .4)` |
| Control (button, pill), chosen toggle option | parent + 2, hover one more | `0 0 0 0.5px ink-7, 0 1px 2px 0 rgb(0 0 0 / .5)` on a card, table or overlay (ink-4 fill); ink-6 on the panel (ink-3 fill) |
| Primary | ink-12 | `0 0 0 0.5px var(--primary-bg), 0 1px 2px 0 rgb(0 0 0 / .5)` |
| Badge | hue-3 | `0 0 0 0.5px color-mix(in srgb, currentColor 34%, #000), 0 1px 2px 0 rgb(0 0 0 / .5)` |
| Table | ink-2 rows | 0.5px ink-5 frame, `0 1px 2px 0 rgb(0 0 0 / .5)` |
| Menu, dropdown | ink-2 | `0 0 0 0.5px ink-7, 0 1px 2px 0 rgb(0 0 0 / .5), 0 4px 8px -4px rgb(0 0 0 / .5)` |

- In table rows, buttons are two steps above the row and two more on hover (ink-4 on the ink-2 rows), with the control's outline and drop.
- **No lit top edge** (`inset 0 1px 0 rgb(255 255 255 / a)`) and no second line under the outline. On a dark ground the two read as a gradient.
- **Drops are always black**, darker than the parent. A hue's light text colour used as a blurred shadow reads as a glow.
- Controls, badges, toggles, tables and cards keep their tight drops in dark. The panel over the near-black ground and floating overlays keep theirs too.

**Sizes never fork.**

- Every ring is a `box-shadow` (0.5px or 1px spread), so it never changes layout. The light 1px ring and the dark 0.5px outline leave the box the same size.
- Where light hides a border that dark shows, the border exists in both: `border border-transparent` in light, coloured in dark. The box is the same size.
- Put theme differences in tokens, not in scattered `dark:` utilities. A dark change may only alter colour or shadow values.

## 3. Hairlines and borders

- **One weight: 0.5px in ink-6** (ink-5 in dark). Images, screenshots and recordings get a 0.5px ink-6 frame.
- **Every edge in dark is 0.5px**, components included: control, toggle and card outlines, the primary's outline and badge outlines. The 1px ring inside a light shadow is the only 1px line, and it becomes a 0.5px solid outline in dark.
- **The dark line rule only reaches what it targets.** If it is written as a selector list of hairline utilities (0.5px borders, 0.5px-tall or -wide rules, named ring shadows), a line drawn any other way, such as an inset box-shadow, keeps ink-6 in dark. Give it its own dark remap.
- **Bar edges are drawn over the bar.** On a top strip, top bar or bottom bar, draw the foot or top rule as an absolutely positioned 0.5px element over the edge, not as a border. Content then centres on the full bar height (52px, 56px).
- **No double borders.** A nested element with its own border inside a bordered parent, a doubled bottom line, a header band rounder than its dialog, a border inside a shadow's ring: all bugs. When a header strip meets a body, the strip's radius belongs to the parent (outer radius minus the border).
- **Remove lines before adding them.** No lines between choice rows, no borders on empty states, no box around a group that space already groups.
- **Separators in menus and drawers run edge to edge.** The space above and below a separator equals the side padding.
- **A sticky header's bottom line appears only once content scrolls under it.** At the top it's invisible.
- **A fade beats a hard cut.** Where content scrolls, a mask fade in the background colour says "more" better than a scrollbar: 36px on a rail, 20px on a sideways row, 24px under a sticky top. Animate the fade length (registered `@property`, 200ms) so it eases in as you leave an edge.
- **Overscroll:** `overscroll-behavior: none` everywhere. No rubber banding, no scroll handed to the page behind.

## 4. Shell

### Desktop
- **Rail:** 292px wide, on the ground. The width is the widest nav label at body size + 16px icon + 6px gap + row padding + rail padding, rounded up to 4px; 292 is that sum for the default labels in Inter. Pinned top (account or workspace switcher, search), scrolling middle with 36px fades, pinned foot (one notice, then the user row, 18px apart and 18px from the bottom). No rules between parts; space separates them.
- **Rail rows:** 36px, control radius, 16px icon, 6px gap, 13/20 ink-10 text (ink-11 if your ink-10 misses 4.5:1 on the rail; see [tokens.md](tokens.md) §1). Hover: ground + 1 with ink-12 text, fading in and out on that row (150ms); no shared highlight slides between rows. Current page: ink-3 fill (ink-2 in dark) with no edge and no shadow. Hover stays a step below the current fill so they never match. Rows 1px apart.
- **Group titles:** 13/20 ink-9, set off by 16px of space above, not a rule. Groups are always open, with no chevrons.
- **Top strip of the panel:** 52px tall (a 36px control + 2 × 8px inset), 36px controls 8px in from every edge, a hairline at its foot. The page title is 13/20 ink-12, centred and absolutely positioned so it doesn't move with the switcher. Breadcrumbs at the left (they replace back buttons); page-level actions at the right. The top bar is part of the panel, not a separate layer.
- **Collapse in three beats:** contents fade out together (80ms), the width changes (220ms), contents fade back in. Contents are pinned at full width inside the frame, so nothing reflows or slides while it moves.

### Phone
See [mobile.md](mobile.md): the panel goes edge to edge, the rail becomes a top bar with a menu.

## 5. Cards

**When to use a card**

| Content | Container |
|---|---|
| Navigation, link lists, choice lists | plain rows: no box, fill on hover only |
| One unit of related data (a figure with its chart, a balance, a plan) | a card |
| A step that is itself an action | a clickable card |
| Many records with the same fields | a table |
| Grouped settings or choices on a phone | one raised card of rows |

**Data card:** white + `--shadow-card` (in dark: ink-2, its 0.5px ink-6 outline and black drop), radius 8, 24px padding, 16–24px gaps. Charts and settings sit on it. Optional header strip: 46px (20px line + 2 × 13px), 10px left / 8px right padding, a 13/20 title, a 0.5px rule under it and its action at the right.

**Clickable card:** white + `--shadow-card`, radius 8, 12–16px padding. Hover ink-2 (ink-3 in dark). Press `scale(.99)`. Cards in a row are the same height.

**Selection card:** pressed in when picked (ink-3 fill, hairline only). See [buttons-and-controls.md](buttons-and-controls.md).

**Notice:** radius 12, 0.5px border, white, `--shadow-table`, padding 24 × 16, a 16/24 title over a 13/20 line, the action at the right (under it, full width, on a phone). A tinted notice: hue-3 fill, hue-6 edge, hue-11 text. No warning icon before the title.

**Rail notice:** one at a time, by priority (blocking problems before warnings before announcements). Control radius, raised, a 38px header strip (20px line + 2 × 9px), full-width 36px buttons stacked (primary on top). It can fold to its title plus a progress ring. Dismissed through ⋯ or ×, except a blocking state, which can't be dismissed. It finishes by fading out whole.

**Section headings sit outside cards.** The heading names the card, so the card doesn't repeat it.

## 6. Tables

| Part | Default |
|---|---|
| Frame | 0.5px `--line` border (ink-6; ink-5 in dark), radius 8, `--shadow-table` under it in both themes: `0 1px 2px 0 rgb(ink / .12)` in light, `0 1px 2px 0 rgb(0 0 0 / .5)` in dark |
| Fill | one fill for the header and every row: white (`--surface-top`) in light, ink-2 in dark. No zebra stripes; only a long table may stripe (white / ink-2 in light, ink-2 / ink-3 in dark). |
| Lines | 0.5px `--line` rules between rows; columns split by 0.5px left dividers. The last row draws no rule, so the frame is the only bottom line. |
| Header | 13/20 ink-12, a 0.5px ink-6 rule under it |
| Rows | 38px desktop (20px line + 2 × 9px), 44pt phone; 13/20 text; 12–16px cell padding (16px on the main record tables, 12px on denser ones), matched within a table. The frame hugs the last row, with no empty space under it. |
| Ink | the header and the first, identifying column in ink-12; every other body cell ink-10 (ink-11 if your ink-10 misses 4.5:1 on the row; see [tokens.md](tokens.md) §1), so the header and each row's name lead |
| Type | one typeface in every cell, with figures in `tabular-nums`; no mono column |
| Status | a dot in its hue with its label, not a badge. See "Status dot" in [buttons-and-controls.md](buttons-and-controls.md). |
| Hover, selected | local ground + 1 and + 2, declared after the row fill so they always win |
| Alignment | every cell left-aligned, numbers included; first and last cells line up with the card's padding |
| Columns | hug their content so nothing wraps. Free text (names, emails, URLs) caps at 32ch (about 240px at 13px), then truncates on one line with "…" and a tooltip. See "Worst-case data" in [layout-and-hierarchy.md](layout-and-hierarchy.md). |
| Actions column | last; hugs its contents with 12–16px either side, matching the table's cell padding; a 1:1 ⋯ menu or a 22px icon / "View" pill; only valid actions (a deleted item can't be viewed) |
| Header for actions | appears only once a row exists |
| Expired or inactive row | the whole row at 50% opacity, never one cell |
| Row highlight | a new or merged row fades ink-a4 to transparent over 700ms |

**Pager outside, below.** 12px under the card: the count on the left ("Showing 1–10 of 48", ink-10), white Previous / Next on the right. Only when there's a page to move to. Lists on summary pages stop at 5–6 rows.

**Empty state:** hide the header and the pager. A bare centred panel: ink-2 fill, 44px padding, radius 8 (0.5px ring in dark), an 18px icon (24px on a phone, not in a box), two 13/20 lines in ink-9 (ink-11 where ink-9 misses 4.5:1): what's missing, then what to do. With filters on: "Try removing a filter, or clear them all."

**Failed load:** the empty-state layout with two lines ("Couldn't load runs." / what to try) and one secondary "Try again" button.

**Loading:** keep the frame and column widths; 12px pulsing ink-4 bars with control radius in place of text. Skeleton rows: the page size, capped at 10.

**Table inside a card:** runs edge to edge along the card's foot under its own hairline (negative margins equal to the card padding). First and last cells are inset by the card's padding.

## 7. Modals (desktop)

**Choose a modal** for a focused task (a form, a purchase, revealing a secret) or a confirm. An action opens its dialog over the current page; it doesn't navigate away.

**A small confirm shown in place** on the page, with no backdrop, is a card with `--shadow-button` (ring and 1px drop), not `--shadow-modal`.

| Width | Use |
|---|---|
| 620px | default: forms, purchases, key reveal |
| 460px | confirm, downgrade |
| 440px | compact info or steps popup |

Always `max-width: 100%` with a 16px backdrop gutter; `max-height: calc(100dvh - 32px)`.

**Card:** ink-2 (white in light), radius 8, `--shadow-modal`, z 100. The shadow's ring is the edge (a 0.5px ink-7 outline in dark); no border.

**Three parts, split by full-width 0.5px hairlines:**

1. **Header band:** padding 20 / 20 / 16 (sides, top, bottom). Title 16/24 ink-12. Description 13/20 ink-11, 4px under. Light: white like the body. Dark: a lifted ink-3 band over the ink-2 body. Takes the card's top corners: the outer radius minus the border, so the full 8px when the edge is the shadow's ring.
2. **Body:** 16px padding (24px for roomy forms), 16–24px gaps, inputs fill the width. The only part that scrolls.
3. **Footer:** 12px padding, Cancel left, confirm right, 12px gap, buttons hug their labels.

**Confirm variant (two parts):** the band holds the message; then the actions row. No body.
- State the consequence plainly: "This will delete the key from 3 projects." The title asks the question.
- Destructive: title in red-11, confirm solid red-9.

**No × on footer-driven modals.** Cancel, Escape and a backdrop click close them. Only footer-less info popups keep a 22px × at 20px from the top right, ink-10, hovering to an ink-3 fill.

**Backdrop:** black 30% in light, 90% in dark, 2px blur. Modals always dim. A side panel dims only when it's fullscreen. These are the house Modal's values; a library Dialog that drifts (80% dark, no blur, a 300ms sheet) should be brought in line.

**Behaviour**
- `role="dialog"` with `aria-labelledby` on the title.
- On open, focus the first field (not Cancel), or the confirm button in a two-part confirm.
- Trap Tab inside the modal; return focus to the trigger on close.
- Lock page scroll while it's open.
- Once the form has changed, a backdrop click does nothing (only Cancel or Escape close it), or it asks before discarding.
- Never stack two modals; replace the content in place.

**Multi-step in place.** Form, then spinner, then result happen inside the same card, with no close and reopen. The card eases between measured heights over 300ms with the strong ease-out while contents crossfade. Better still: hold the final size from the start so only the content fades. Give a spinner step a fixed height. Move focus into each new step.

**Anything opened from a modal** (select, menu) sits above it (z 110).

**Errors** from a modal on a list page become a toast after it closes, not an inline block on the page.

## 8. Side panel (desktop)

(Not in the source; defaults for the designer to confirm.)

- **Use it** to inspect or edit one record while the list stays visible. A focused task or a confirm is still a modal; a whole new context is a page.
- 400–480px wide, full height inside the 8px panel float, radius 8 on the inner edge.
- Same header band, body and footer as a modal.
- Overlay surface and `--shadow-modal`, z 100. No dim unless it's fullscreen.
- Enters `translateX(100%)` to 0 in 240ms on `--ease-out`; exits in 200ms. Escape closes it.
- On a phone it becomes a bottom sheet.

## 9. Bottom sheets (phone)

Every dialog becomes a bottom sheet under 768px. Full anatomy and drag physics in [mobile.md](mobile.md). The surface rules:

- Full width, 14px top corners, hairline on the top edge only. The sheet is `--surface-top` (white) in light, ink-2 in dark.
- No header band and no ×. The title becomes a 20/28 section title on the sheet; a white, tactile grab handle above the sheet replaces the ×.
- Rises in 320ms (the house Modal's value; bring a library Dialog's 300ms in line).
- **Related information joins into one raised card**, like a table: white + `--shadow-button` on the white sheet in light; in dark, ink-3 on the ink-2 sheet with the control's 0.5px outline and black drop; control radius; 0.5px rules between rows; rows at least 48pt.
- **Buttons never sit inside that card.** They go below it, 12px under, 8px apart, as full-width 44pt secondary buttons. They must look like real buttons.

## 10. Menus, popovers, tooltips

**Menu**
- Trigger: a secondary button with a chevron that turns over while the menu is open.
- Portalled to the body; positioned from the trigger, 6px below it (or centred on it). Min width 160px (320px for a workspace switcher).
- White in light, ink-2 in dark; radius 8; `--shadow-menu`, whose ring is the edge, so no border; 4–6px padding.
- Items per [buttons-and-controls.md](buttons-and-controls.md): 36px, 2px apart. The picked row is local ground + 2 with ink-12 text and no tick (`--root-ink-3` in light); the row under the pointer is ground + 1 (`--root-ink-2` in light). Each item's fill fades in and out where it is (150ms); no shared highlight slides between items.
- Opens from the trigger: `scale(.97)` to 1 with a fade, 150ms in and 120ms out, origin at the trigger.
- Closes on outside press, Escape, resize, or page scroll (scrolling its own list doesn't count).
- Don't move an open menu while items shift; reposition on the next open.
- On a phone it stays 20px from the screen edges, or becomes a sheet.
- Use one dropdown component everywhere.

**Info popover:** 12px × 10px padding, 12/16 ink-11, `--shadow-popover`. On a phone it opens on tap.

**Action tooltip:** names an icon-only action. Ink-3 fill with a 0.5px ink-6 border (or ink-12 inverted), 12/16 text, **zero delay**: it names the action the moment it's hovered. Never the only place information lives.

## 11. Toasts

- **One at a time.** Bottom centre, 24px from the bottom, z 120. On a phone: 12px above the bottom bar or home indicator, 20px from the sides.
- **Pill:** 48px tall, fully round. The tone's -3 fill, a hairline ring in its -6, title in -11 (-9 in dark), an optional 22px solid -9 action button with -contrast text. The whole pill is the tap target.
- Width: at least 400px with an action; otherwise it hugs the title plus 32px.
- Auto-dismiss after 6s.
- **Use a toast** for a result the user can't otherwise see: a background job finished, an action from a closed modal failed, a reward landed. Toasts may carry one action ("View project").
- **Don't toast** a copy (the icon turns into a tick) or anything already visible on screen.
- **Decorative shapes only for celebrations.** Routine saves get none; errors never do.
- Motion in [motion.md](motion.md).
