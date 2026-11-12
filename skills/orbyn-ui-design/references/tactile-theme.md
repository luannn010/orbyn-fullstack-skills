# Tactile theme

An optional visual direction: interfaces that feel physical but quiet. A soft ground,
raised surfaces with a fine ring and a crisp drop, one strong action, controls that
squeeze when pressed. Use it only when the person asks for this look or a product
adopts it. A project's own design system, and the [house style](house-style/README.md)
for a new app, keep their values. The full source, with every value and a token
template, is pinned at [upstream tactile-design](upstream/tactile-design/SOURCE.md).

Values below assume a 12-step neutral scale (`ink-1` lightest to `ink-12` strongest)
and Inter at one weight. Remap them to the project's palette and type; keep the roles.

## Surfaces take their look from their parent

A control's fill, edge and drop come from the surface it sits on, so it reads equally
pressable on a panel, card, table row or sheet. Redeclare the tokens on each surface
class; set once on the root, they will not follow the parent.

| Part | Light | Dark |
| --- | --- | --- |
| Fill | the top surface (white) | parent + 2 steps for controls, + 1 for cards |
| Edge | 1 px ring of `ink / .08` | one solid 0.5 px outline, three steps above a control's fill (ink-6 on cards), same colour all round |
| Drop | `0 1px 2px 0 rgb(ink / .12)` | `0 1px 2px 0 rgb(0 0 0 / .5)`, always darker than the parent |

- Shadows are crisp: the ring and 1 px drop plus at most one short drop (card
  `0 3px 4px -2px`, menu `0 4px 8px -4px`, modal `0 6px 8px -4px`). No big soft blur.
- Dark mode is designed, not inverted: never a lit top edge, an outline that changes
  colour, an edge over 0.5 px, or a shadow lighter than its parent (a glow).
- Dark changes colour and shadow only; sizes, padding and radius never fork by theme.
- Fields are wells: a sunk fill, no border; focus deepens the fill and adds the ring on keyboard focus.
- Structural lines are 0.5 px. White on white gets its edge from the ring, not a fill.

## Controls

- One primary per surface, filled with the strongest neutral. No grey buttons in
  light: every button is white or the primary. Cancel is white everywhere.
- Destructive trigger: white with red text. Solid red only on the final confirm,
  which names the action ("Yes, delete").
- One control height (36 px desktop, 44 pt on touch), 6 px control radius matched to
  the icon set, fully round pills and badges.
- Press: `scale(.97)` over 150 ms; smaller targets squeeze more, cards less.
- One focus token drawn 2 px on every control, at least 3:1 on every surface.
- Disabled: .6 for buttons and fields, .4 for icon buttons.
- Loading swaps the label in place ("Saving…"); nothing moves.
- Copy: the icon turns to a tick on click, reverts or says "Copy failed" on refusal;
  no toast. A chosen menu item shows a stronger fill, not a tick.

## Motion values

- One curve for anything the person caused: `cubic-bezier(.23, 1, .32, 1)`.
- Hover is colour only, 150 ms, fine pointer only; each row fades its own fill.
- Menu in 150 ms from `scale(.97)` with a fade, out 120 ms; modal in 240 ms, out
  200 ms; sheet up 320 ms, down 200 ms. Never enter from scale 0.
- Springs keep their overshoot inside the container: a sliding toggle pill at about
  bounce .12 over 0.4 s; check the overshoot distance against the track's inset.
- No animation on keyboard actions, drag, resize or data figures.

## Phone

- 20 px gutters, full-width stacked actions, the confirm on top in a dialog.
- Dialogs become bottom sheets with a grab handle instead of ×. A sheet drags from
  anywhere once a press moves 4 px, closes past min(64 px, 15% of its height) or on a
  fast flick, else springs back.

## Never ship

Beyond the rules above and the [screen decisions](screen-decisions.md):

- An eyebrow label over a title, or "Step 1 of 4" over a progress bar.
- A toast for a successful copy, or a copy tick that waits for the clipboard.
- One hover highlight that slides between rows.
