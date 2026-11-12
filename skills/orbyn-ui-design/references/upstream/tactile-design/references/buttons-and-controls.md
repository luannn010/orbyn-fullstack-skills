# Buttons and controls

Values are defaults; the role or reason next to each one is what transfers. `ink-N` is a neutral step, `hue-N` a coloured step. Token names are from [tokens.md](tokens.md).

## 1. Pick the role before the look

| Role | Use it for | Light | Dark |
|---|---|---|---|
| **Primary** | The one action that commits or completes this surface: Create, Save, Continue, Finish, Apply, Copy once a secret is revealed | `--primary-bg` fill (ink-12), `--primary-fg` text (ink-1), `--shadow-primary` (1px ring in the surface colour) | ink-12 (near white) fill, ink-1 text, `--shadow-primary`: a 0.5px outline in its own fill plus the tight black drop |
| **Accent primary** (opt-in) | Only when the brand requires a coloured primary. Same job as the primary. | accent-9 fill, accent-contrast text (at least 4.5:1), accent-10 hover, `--shadow-primary` | same steps, `--shadow-primary` (0.5px outline in its fill + tight black drop) |
| **Secondary** | Every other action of the surface: Cancel, Close, Skip, Docs, View plans, section and header actions | `--raised` (white), `--shadow-button`, no border | ground + 2 steps (ink-3 on the panel, ink-4 on a card or in a modal), `--shadow-button`: a solid 0.5px outline three steps above the fill (ink-6 on the panel, ink-7 on a card or in a modal) + tight black drop |
| **Utility pill** | Light tools attached to content: Copy on a code block, filters, presets, Back in a flow, Show key inside a field, the ⋯ menu | fully round, 28px (36px on a coarse pointer), white, `--shadow-toggle`; 14px icon, body-size label | ground + 2 steps, hover + 3, `--shadow-toggle` (the button's outline and drop) |
| **Icon** | Per-row or in-field tools with a universal glyph: copy, edit, delete | no fill, ink-10 glyph, ink-12 on hover | same |
| **Ghost** | Tertiary actions inside a form: Remove, Clear | no fill, ink-10 text, ink-12 over an ink-2 wash on hover | same |
| **Text link** | Tertiary navigation in a sentence: "No account? Sign up", only the link word underlined | same size as button text | same |
| **Destructive trigger** | Opens a destructive confirm: Delete, Revoke, Remove member | secondary with red-11 text and icon, hover red-3. Or soft: red-3 fill, 0.5px red-6 edge, red-11 text, hover red-4 | same steps |
| **Destructive confirm** | The final yes inside a destructive dialog | solid red-9, red-contrast text (white), no shadow, hover `brightness(.95)` | same fill, a 0.5px red-9 outline + tight black drop, as the dark primary |

**Rules behind the table**

- **A rectangle at control radius belongs to the surface; a round pill belongs to the content.** Page and dialog actions are rectangles. Tools that act on one piece of content are pills.
- **No grey filled buttons in light.** Every button is white or the primary fill. A grey fill reads as disabled.
- **Hue fills at most two buttons:** red-9 on the final destructive confirm, and the primary only if the brand opted into an accent primary. Then that hue leaves status use, and destructive must still look clearly different. Otherwise brand colour lives in tints (badges, charts, identity).
- **The primary needs no drop shadow in light.** The darkest thing on a light page already wins. Its 1px ring in the surface colour makes it read a pixel smaller, which levels it optically with the white buttons, whose ring sits outside. In dark it is the lightest thing, and takes the tight black drop every dark control keeps, under a 0.5px outline in its own fill: `0 0 0 0.5px var(--primary-bg), 0 1px 2px 0 rgb(0 0 0 / .5)`.
- **Destructive is never the primary.** Solid red appears only at the last step, inside the dialog, so a delete never reads as the safe default. The trigger that opens the dialog is softer.
- **Hover works with any colour.** The primary hovers to `--primary-hover`, a 7% mix toward its text colour: it lightens a dark fill and darkens a light one. (`brightness(.95)` barely moves a near-black fill; it is fine on a mid-tone like red-9.)

### Tactility borrows from the parent

A control's fill, edge and drop are never absolute values. Each is taken from the surface it sits on, so the same button, pill, toggle or badge reads equally raised on a panel, a card, a rail, a table row, a sheet or a tinted surface, in light and in dark.

| Part | Light | Dark |
|---|---|---|
| Fill | `--surface-top` (white) | parent + 2 steps for a control (parent + 1 for a card) |
| Edge | a 1px ring, `0 0 0 1px rgb(ink / .08)`: alpha, so it darkens whatever is beneath | one solid 0.5px outline three steps above the fill, the same colour all round: `0 0 0 0.5px var(--ink-7)` over an ink-4 control on a card or overlay, ink-6 over an ink-3 control on the panel |
| Drop | `0 1px 2px 0 rgb(ink / .12)` | `0 1px 2px 0 rgb(0 0 0 / .5)` |
| Badge | its own hue: a 14% ring and a 16% drop | a dark shade of its own colour, `color-mix(in srgb, currentColor 34%, #000)`, plus the black drop |

- **A drop is always darker than its parent, never lighter.** Light drops are drawn in `--shadow-ink`, dark drops in black. A light colour used as a shadow in dark reads as a glow.
- **Dark edges are 0.5px and solid.** No lit top edge (`inset 0 1px 0 rgb(255 255 255 / x)`) and no second line under the edge: on a dark ground the two read as a gradient outline.
- **Dark controls keep their drop.** Buttons, pills, the chosen toggle option and badges all keep the tight black drop under the outline. Without it a grey control reads flat.
- **A white control on a white parent** (a secondary button on a white card, a neutral badge) gets its edge from the ring and the drop, never from a grey fill.
- **Redeclare per surface.** These shadows are variables built from working steps, so they resolve where they are declared. Redeclare them on each surface class, as the step-shift rule in [tokens.md](tokens.md) says, or the edge won't follow the parent.

## 2. How many primaries

- **One per surface.** Exactly one in each modal footer, flow footer and menu (Apply). A page usually has none or one: header and section actions are white, and the primary is kept for the commit.
- **Only when it's the real next step.** An Upgrade button shows only on the plan that can upgrade. Don't render a primary to fill space.
- **Key chips go on the page's primary only.** Not on next/previous, navigation, copy buttons or sign-in.
- **When the user is about to give something up** (downgrade, cancel a plan), the safe choice ("Keep current plan") is the primary and the leaving action is secondary.
- **When the user already chose to destroy** (delete, revoke), the confirm is solid red-9 and names the action: "Yes, delete", "Delete project". Cancel is secondary. The heaviest irreversible deletes can ask the user to press and hold instead of a single click.
- **Disabled until it can work.** Create stays disabled until the required field is filled. Apply stays disabled until something is picked. Assign stays disabled while the current value is still selected.

## 3. Order and placement

| Context | Order | Notes |
|---|---|---|
| Dialog footer | Cancel left, confirm right | `flex justify-between gap-3 p-3` under a 0.5px hairline; buttons hug their labels. After the task is done, Cancel becomes Close. |
| Page or section group | secondary first, primary last at the far right | e.g. View plans, then Upgrade plan |
| Flow footer | Skip, then Continue filling the rest | Continue is `flex-1`; when Skip leaves (scale .95 + fade, 200ms) Continue grows into the space. |
| Phone, page | stacked full width, primary on top | page stacks keep their 12px gap |
| Phone, dialog or flow | stacked, confirm on top, 8px apart | iOS alert order |
| Previous / Next | side by side on a phone too, half and half | |

- Desktop footer buttons never go full width. Phone action stacks always do.
- Don't pre-focus Cancel when a modal opens.
- A section's buttons sit above what the section shows, never under it. See [layout-and-hierarchy.md](layout-and-hierarchy.md).

## 4. Recipes (Tailwind v4)

Recipes use tokens only (see [tokens.md](tokens.md)): sizes, radii, colours, type and shadows from variables, spacing from the 4px scale. A literal px or hex here is a bug. Name every transitioned property, and include `scale`, because Tailwind v4's `scale-*` sets the separate `scale` property.

```html
<!-- Primary -->
<button class="h-[var(--control-h)] px-3.5 rounded-[var(--radius-control)] bg-[var(--primary-bg)] text-[var(--primary-fg)]
  text-sm tracking-[var(--tracking-label)] shadow-[var(--shadow-primary)]
  hover:bg-[var(--primary-hover)] active:scale-[0.97]
  transition-[transform,scale,background-color] duration-[var(--dur-hover)] ease-[var(--ease-out)]
  disabled:opacity-60 disabled:active:scale-100 disabled:hover:bg-[var(--primary-bg)]
  dark:disabled:opacity-100 dark:disabled:bg-ink-4 dark:disabled:text-ink-8 dark:disabled:shadow-none">Create project</button>

<!-- Secondary (dark: ground + 2, hover + 3; ink-3 / ink-4 on the panel, ink-4 / ink-5 on a card or in a modal) -->
<button class="h-[var(--control-h)] px-3.5 rounded-[var(--radius-control)] bg-[var(--raised)] text-ink-12
  text-sm tracking-[var(--tracking-label)] shadow-[var(--shadow-button)]
  hover:bg-[var(--root-ink-2)] active:scale-[0.97]
  transition-[transform,scale,background-color] duration-[var(--dur-hover)] ease-[var(--ease-out)]
  dark:bg-ink-3 dark:hover:bg-ink-4 disabled:opacity-60">Cancel</button>

<!-- Utility pill (icon leads; dark fill as the secondary) -->
<button class="h-[var(--control-h-pill)] pointer-coarse:h-9 rounded-full pl-2.25 pr-2.75 gap-1 inline-flex items-center
  bg-[var(--raised)] text-sm shadow-[var(--shadow-toggle)] active:scale-[0.97]
  dark:bg-ink-3 dark:hover:bg-ink-4 touch-target">Copy</button>

<!-- Row icon button -->
<button aria-label="Delete" class="size-[var(--control-h-icon)] rounded-[var(--radius-control)] text-ink-10
  hover:text-ink-12 hover:bg-ink-4 active:scale-[0.92] disabled:opacity-40 touch-target">...</button>
```

- `--control-h` is 44px on a phone, so these recipes lift without a `max-md:` class.
- **Hover inside overlays** uses `--root-ink-2`, because overlays repaint their own ink-2 as the surface top.
- **Dark colour utilities are fine; dark layout utilities are not.** `dark:bg-*` may change colour or shadow. It may never change padding, height, radius or border width.
- **Dark edges come from the tokens.** `--shadow-primary`, `--shadow-button` and `--shadow-toggle` already carry the solid 0.5px outline and the tight black drop in dark. Never add a `dark:` inset highlight or a second ring.
- **A page-level pill action** (copy the page, share) sits beside the page's other controls, at the pill's size: 28px, a 14px icon, body-size words.
- **Over media:** `bg-black/50 backdrop-blur-md text-white`.
- **Sheet action (phone):** `h-[var(--control-h)] w-full px-3.5 gap-2 text-base bg-[var(--raised)] shadow-[var(--shadow-button)] active:bg-[var(--root-ink-2)]` (16/24 text), icon before the words, ground + 2 in dark (ink-4 on the ink-2 sheet). A real button, not a row of words.

## 5. Sizes

| Height | Token | Used for |
|---|---|---|
| 44 | `--control-h` on a phone | every button, field and toggle track on a phone |
| 36 | `--control-h` | standard desktop button, field, select, menu item, rail row |
| 32 | `--control-h-compact` | compact confirm inside a menu |
| 28 | `--control-h-pill` | pills, toggle options, icon buttons |
| 24 | `--control-h-inline` | inline row or card actions |
| 22 | `--control-h-icon` | row icon buttons |
| 20 | `--badge-h` | badges, the search key pill |
| 18 | `--key-chip` | the key chip on a button |

**Rule:** one control height rules a surface. Input = button = toggle = selector height. Things that sit beside a button (stat chips, selectors) take the button's height.

| Padding | Where |
|---|---|
| 14px a side | centred text buttons: dialog footers, flows, sheets |
| 12px | page-level buttons |
| 10px | header-strip and section actions, 24px inline actions |
| icon side 2px tighter | `pl-2.5 pr-3` with a 6px gap. A glyph with built-in air gets `pl-2` and a 4px gap, so it looks the same. |

| Icon | Size and ink |
|---|---|
| Leading icon in a button | 16px; ink-9 inside white buttons; text 2px closer to it than to the edge |
| Small icon beside text (pills, toggle options) | 14px, 4px before the label, stroke 2.5 on the 24px grid |
| Standalone, row icon | 16–20px, ink-10 to ink-11 |
| Empty-state icon | 18px desktop, 24px phone |
| External-link arrow | only when the link truly leaves the app; 14px, ink-10 |
| Spinner | 14px, the button's own ink, in the icon's 16px slot |

**Icon style:** a 1.5px rendered stroke at 16px (the marks token), round caps and joins, about 1px corner radius. Match the stroke to the UI weight: 1.25px for a light face, 1.75px for a heavy one. A good default is Lucide with `absoluteStrokeWidth` at 1.5. Checkmarks are slightly rounded everywhere. A filled glyph means "ready to run" (a filled play on Start).

- **Small icons get a heavier stroke.** A stroke set on the 24px grid thins as the icon shrinks, so raise it: 2.5 at 14px (about 1.46px rendered), not the default 2 (1.17px), which looks thin beside text. An absolute stroke width does this for you.
- **An icon beside text is centred on the text's line**, not sat on its baseline: `inline-flex items-center` on the pair.
- **The copy glyph is rounder than the set:** both squares take a 3.5 corner radius on the 24px grid (the stock glyph draws 2).

## 6. States

### Hover
- One step above the local ground on fills; ink-11 to ink-12 on text; `--primary-hover` on the primary.
- Selected is two steps above the local ground, so hover never matches it. Hovering a selected item keeps it selected.
- Colour only, 150ms. Nothing moves.
- Each row in a list or menu has its own hover fill, which fades in and out where it is. Never one shared highlight that slides from row to row.
- Only on a fine pointer. On touch the same look shows while pressed (see [mobile.md](mobile.md)).

### Press
Done in CSS so a quick second press retargets instead of restarting. The squeeze gets deeper as the target gets smaller:

| Scale | Target |
|---|---|
| .99 | cards, full-width rows |
| .97 | buttons, pills |
| .94 | 44px round icon buttons |
| .92 | 22px icon buttons |

Disabled controls cancel both: `disabled:active:scale-100`, and the hover returns to the resting fill.

### Focus
Every interactive element needs a visible `:focus-visible` state, drawn with one token: `--focus-ring` (ink-10 by default). It keeps 3:1 or more against white, against the ink-2 and ink-3 tracks and wells, and against the dark surfaces, so it works on every control in both themes. Never hard-code a dark alpha for focus; it vanishes in dark.
- Buttons, pills, toggle options, switches and icon buttons: `outline: 2px solid var(--focus-ring); outline-offset: 2px`.
- Rows and cards reached with Tab: the same outline. Items moved through with arrow keys (menus, choice lists) show the highlight fill instead.
- Fields: deepen their fill one step (the same as focus by pointer). That shift is only about 1.08:1, too faint for keyboard users, so also add `box-shadow: 0 0 0 2px var(--focus-ring)`. Text fields match `:focus-visible` on a click too, so mouse users will see it as well; accept that, or show it only after a keydown.

### Disabled
- `opacity: .6` for buttons, switches and fields; `.4` for icon buttons. Hover and press off. (The black primary also appears at `.5`; pick one per product.)
- In dark, a faded white primary still glows like a live button. Make it solid instead: ink-4 fill, ink-8 text, full opacity, and no outline or drop, so it no longer reads as pressable.
- On a phone, explain why a control is disabled in text under it. Never only in a tooltip.

### Loading (label swap)
- The label swaps in place to a spinner plus a verb in the -ing form: "Saving…", "Creating…", "Deleting…". Always the real "…" character.
- Both labels share one grid cell, so the button keeps the wider of the two until the old one has gone. It never jumps mid-fade.
- Incoming rises from `translateY(6px)` with `blur(2px)` and opacity 0; outgoing leaves to `translateY(-6px)` with `blur(2px)`. 200ms, strong ease-out.
- No animation on mount. Under reduced motion: crossfade only.
- A send button may drop its text and become just the spinner.
- Never show a wrong label while loading. If the current state is unknown, the button reads "Loading…" and is disabled.

### Copy feedback
- The copy icon turns into a tick **on the click itself**, before the clipboard answers. Waiting for the promise makes the button feel slow.
- The tick is drawn at 1.3× so it reads the same size as the icon it replaces.
- Both scale between .5 and 1 with a crossfade, 200ms. Reduced motion: opacity only.
- The tick holds 1000ms on an icon button, 1500ms on a pill.
- No toast and no flash of the field.
- If the clipboard refuses, revert at once: the tick goes back to the copy icon, so the button never claims a copy that didn't happen. A pill with words says "Copy failed" in place of its label for the same hold.

## 7. Fields

**The well:** `h-[var(--control-h)] rounded-[var(--radius-control)] border-0 bg-ink-3 px-3 text-[length:var(--text-field)] leading-[var(--leading-body)] placeholder:text-ink-10 focus:bg-ink-4`.

- No border and no shadow. Focus deepens the fill one step (plus the keyboard cue in §6).
- Read-only keeps its resting fill on focus. Disabled is `opacity: .6`.
- Label: 13/20 ink-12 (or ink-11 in flows), 6–8px above the field. Help text: 12/20 ink-10 under it. "(optional)" in ink-10.
- 20px between fields. Fields in a modal fill its width.
- Textarea: same recipe, `min-h-21` (84px, three lines), `py-2`.
- Placeholders start with a capital letter.
- Field text matches button text size. On any touch screen it is 16px (`--text-field`), as iOS zooms into a field set smaller and stays zoomed: gate it on `(pointer: coarse)`, not only on width, so an iPad's wider layout gets it too.
- On a phone the well is 44pt tall (`--control-h`) with 16/24 text; with a mouse, 36px at the body size. Any icon or key inside it keeps its place: 24px at 36, 32px at 44, the same 6px from the end.
- Lighter variant on a white surface: ink-2 resting, ink-3 on focus.

**A field never looks like a button.** Buttons are raised; fields are sunk. In light a well is one step darker than its surface; in dark, one step lighter.

- A button that opens search wears a field's look: a 0.5px ink-6 border, white (ink-2 in dark), border ink-7 on hover, no shadow.
- Exception: on a phone in light, the search bar is raised (white + `--shadow-button`) like the buttons around it.

**Select trigger:** the dropdown trigger in §8: the white button at control height, with a 16px ink-9 chevron at the right that turns over while open.

### Errors
- **Invalid field:** keep the well and add a 1px red-11 ring as a box-shadow (`0 0 0 1px var(--red-11)`, the same error ring choice tiles and selects use), so nothing moves.
- **Message:** 12/16 red-11 directly under the field, replacing the help text. Link it with `aria-describedby`; give it `role="alert"`. Say what to do: "That name already exists. Pick another name."
- **When:** validate on blur and on submit, never on each keystroke. On submit, focus the first invalid field.
- The primary stays enabled once the required fields are filled; errors show on submit rather than by disabling it.

## 8. Selection controls

### Segmented toggle
- **View switching inside a page (Live / All) uses this toggle.** There are no underline tabs.
- Track: fully round, 4px padding, 4px gap, one step darker than the surface it sits on (one step lighter in dark: a well).
- Options: 28px tall (track 36px), 11px side padding, 13/20. Active text ink-12; inactive ink-11, ink-12 on hover.
- One sliding pill behind the active option, raised like a button and borrowed from the surface: white + `--shadow-toggle` (the button's ring and 1px drop) in light; in dark the control fill (ground + 2, one step above the track) with `--shadow-toggle`: an outline three steps above the pill's fill plus the black drop, `0 0 0 0.5px var(--ink-7), 0 1px 2px 0 rgb(0 0 0 / .5)` on a card.
- The pill moves as a shared-layout spring, `{ bounce: 0.12, duration: 0.4 }`. Its overshoot has to stay inside the track's 4px inset: at `.35` a pill travelling 100px overshoots ~7px and is seen hitting the end of the track. Keep `overflow: hidden` at the track's full radius as a backstop, not as the fix.
- The first placement snaps; only a real toggle animates.
- **Page-level toggle** (a setting for the whole page, such as Light / Dark): the same component, with a 14px icon left of each label (4px gap) and labels at the page's body size and weight. The same spring, so the pill settles without riding into the ends of the track.
- Toggles hug their content. They are the one control that doesn't fill a modal's width.
- On a phone: options 34px, track 42px, 14px text, each option with a 44pt hit area. At the end of a settings row it sits as far from the row's right edge as from its top and bottom (9px in a 60px row); the row's label keeps its 16px. Optionally fill the width with equal options, as iOS does. If the options don't fit, it becomes a dropdown pill that opens a sheet.
- Accessibility: `role="radiogroup"`, one tab stop, arrow keys move between options.
- Use the same toggle component everywhere.

### Choice rows (radio and checkbox lists)
- **The row is the control; the mark is only drawn.**
- Rows: 36px tall (44 on a phone), 8px padding, control radius, 2–4px apart, no box and no lines between them.
- Hover ink-2, selected ink-3. Inside an overlay: hover `--root-ink-2`, selected `--root-ink-3`. In dark: hover ground + 1, selected ground + 2. No white stroke on selection.
- Optional 16px ink-11 icon, 6px before the label. The mark sits at the far right (top right on a selection card).
- Marks: 18px with a 1.5px ink-6 ring. Radio selected: a white well (ink-6 in dark) around an 8px ink-12 dot. Checkbox ticked: `--radius-sm` corners, ink-12 fill, ink-1 check.
- The dot or check enters with `@starting-style` from scale .9 and opacity 0, 150ms.
- Single choice uses circles; multiple choice uses squares.
- "Other" always comes last. Picking it opens a field below it (height 0 to auto plus fade, 200ms) and focuses it.

### Choice tiles
Use tiles when options sit in a grid on a page, rather than a list in a modal.
- 12px padding (44px tall with one line), control radius, the mark at the right.
- A 2-column grid with a 10px gap; one column on a phone.
- Light: resting ink-2 (`--root-ink-2` on a white surface), ink-3 on hover and when selected. Dark: resting ink-3, ink-4 on hover; selected ink-4 plus a 0.5px ink-8 ring. The filled mark is what tells selected from hovered.
- Error: a 1px red-11 ring on the unselected tiles until one is picked.

### Selection card
- At least 124px tall (about 48px taller than its words), 14px padding, title at the top, description at the foot.
- When picked it looks **pressed in, not raised**: ink-3 fill (ink-4 in dark) with the hairline only, no shadow.

### Switch
- **On desktop, a 52×26 track** with a 20px knob 3px in all round: small beside a 36px toggle, as a switch reads as a mark in a settings row rather than a control as big as its neighbours.
- **On a phone, an iPhone's switch** (Apple's HIG): a 51×31 track, the knob still 4px in all round: 23px. 44pt hit area. At a row's end it lines up with the toggle above it, 9px from the right edge.
- **Place the knob with flex, not a pixel offset:** the track is `p-1` with `justify-start` off and `justify-end` on, and the knob moves as a layout animation (`motion.span layout`). It's in place at any size from the first paint (a measured or media-queried offset renders desktop's first and visibly slides on a phone), and Reduce motion makes the move instant.
- The knob is shaded like the toggle's pill: white with `--shadow-toggle` (the button's 1px ring and crisp drop; in dark a solid 0.5px outline and the black drop). It stays white in dark: a grey knob reads as a hole in the track.
- On: green-9. Off: ink-7 in light; in dark a near-black grey between ink-5 and ink-6 (#343434 by default).
- The knob springs across, `{ bounce: 0.2, duration: 0.45 }`, short enough that the overshoot never reaches the track's edge. The track colour changes over 150ms. First render places the knob without animating. Reduced motion: instant, the knob and the track colour both.
- Disabled: `opacity: .6`.
- 44pt hit area via `touch-target`.
- A switch setting in a form is a raised row: white + `--shadow-button`, control radius, 12px padding.

### Filter pills
- Each pill names what is picked ("Status Failed") with a 20px × to clear it (28px on a phone). Label ink-10, value ink-12.
- 28px tall (36px on a phone), white + `--shadow-toggle`; in dark the control fill (ground + 2) with the same token. Open state: ink-2.
- One row next to the toggles, search at the right. The last pill truncates (value max 180px) so search keeps its place. On a phone the row scrolls sideways under 20px edge fades; it never wraps.

### Dropdowns and menus
- **Trigger:** the white secondary button: control height (36px), control radius, `--shadow-button`, `scale(.97)` on press. A 16px ink-9 chevron at the right turns over (`rotate(180deg)`) while the menu is open, in step with the menu.
- **Menu:** `--shadow-menu`, crisp, with no big soft blur: the button's ring and 1px drop plus one short drop. Light `0 0 0 1px rgb(ink / .08), 0 1px 2px 0 rgb(ink / .12), 0 4px 8px -4px rgb(ink / .16)`; dark `0 0 0 0.5px var(--ink-7), 0 1px 2px 0 rgb(0 0 0 / .5), 0 4px 8px -4px rgb(0 0 0 / .5)`. Surface and padding in [surfaces-and-layering.md](surfaces-and-layering.md).
- **Opening:** from the trigger, `scale(.97)` to 1 plus opacity, `transform-origin` at the trigger; 150ms in, 120ms out, `--ease-out`.
- **Fit:** a menu stays inside the container it opens in (a modal, a sheet, a card). Shorten the list until it fits rather than let it cross that edge.

**Items**
- 36px rows (40px in long lists, 48pt in a phone sheet), 2px apart, control radius, 13/20 ink-11.
- Highlight (pointer or arrow keys, one state): local ground + 1 step, ink-12 text. Chosen: local ground + 2 steps, ink-12 text. So in a light menu `--root-ink-2` and `--root-ink-3`; in a dark ink-2 menu, ink-3 and ink-4. Highlight always stays a step below chosen.
- The chosen item gets **no tick**; the grey fill in full ink alone says it.
- A menu with no chosen item may highlight deeper, at ink-4 in light.
- A destructive item is red-11 with a red-a3 hover.
- A multi-select menu ends with a primary Apply (32px; 44px full width on a phone), faint while there's nothing to apply.

## 9. Badges, key chips, status dots

### Badge
- `h-[var(--badge-h)] rounded-full px-2 text-xs leading-[var(--badge-h)] shadow-[var(--shadow-badge)]`; 6px padding on the side where an icon leads, and for very short words. Always fully round.
- Colour (every status and identity badge: Live, Failed, Prod, a plan tier): hue-3 fill, hue-11 text, `--shadow-badge`.
- **A badge borrows its edge from itself.** `--shadow-badge` is drawn from `currentColor` (its hue-11 text), so each hue tints its own edge:
  - Light: the white button's recipe in the badge's own colour, `0 1px 2px 0 color-mix(in srgb, currentColor 16%, transparent), 0 0 0 1px color-mix(in srgb, currentColor 14%, transparent)`. Tight, like the button; not an inset ring plus a soft glow.
  - Dark: a solid outline in a dark shade of its own colour plus the tight black drop, `0 0 0 0.5px color-mix(in srgb, currentColor 34%, #000), 0 1px 2px 0 rgb(0 0 0 / .5)`. Never the hue's light text colour as a blurred shadow: on a dark ground it reads as a glow.
- Neutral (a status with no hue, such as Released or Stopped, or a plain value, like a balance): white on the white card, ink-11 text, `--shadow-button`; the ring and drop give the edge, never a grey fill. In dark: one step above its parent (ink-3 on an ink-2 card) with `--shadow-button`, the control's solid 0.5px outline and black drop.
- Numbers use `tabular-nums`.
- Beside a 20px title the badge goes one size up: 24px tall, 13px text, 10px sides, 8px from the title.
- Phone: 22px tall with 14px text.
- Loading: a 48px pulsing ink-3 pill holds the badge's place.
- The same formula for every badge in every size. No exceptions.

### Key chips
Two chips, one fill: `color-mix(in srgb, currentColor 14%, transparent)` with `--radius-xs` corners (half the control radius). Both are hidden under 768px and on coarse pointers (no keys to press).

| Chip | Where | Size and type |
|---|---|---|
| **Button key chip** | after the label of the page's primary action only | 18px square (`--key-chip`), min width 18px, 4px side padding, 11px mono, `leading-none`, 8px after the label |
| **Search key pill** | inside the search field (⌘K) | 20px tall (`--badge-h`), min width 20px, 6px side padding, 12/16 sans |

### Status dot
- 8px, `currentColor` (the colour of its label). Dots replace ticks and crosses in status text.
- Ongoing states ping (`animate-ping`, opacity .75). No ping under reduced motion.
- Every dot shares one clock phase, so rows mounted at different times beat together.

## 10. Labels

- Sentence case, verb first, short: "Create project", "Invite member", "Copy", "Show key" / "Hide key", "Continue" ("Finish" on the last step), "Skip", "Cancel".
- Confirm buttons name the action: "Yes, delete", not "OK".
- Loading: "Verb-ing…" with the real ellipsis.
- No Title Case, no three dots, no em dashes.

## 11. Keyboard

- Enter submits or continues. Escape closes a modal, menu or panel (in a flow, Escape skips).
- `⌘K` opens search, shown as the search key pill in the search field.
- Arrow keys move inside toggles and menus. One tab stop per toggle group.
