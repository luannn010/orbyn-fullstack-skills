# Motion

The motion principles here follow **Emil Kowalski's** teaching (his course is at [animations.dev](https://animations.dev)). They are paraphrased and applied to this system. The values come from a production dashboard. Where his principle and the product agree, the value is the product's.

**In one line:** decide whether to animate before deciding how; when it moves, it's short, strong ease-out, transform and opacity, exits faster than entrances, and it has a reduced-motion version.

## 1. Decision order

Work through these in order for every motion. Stop as soon as the answer is "don't animate".

1. **Who caused it, and has the user seen it yet?**
   - Settled on load or by the system: snap into place. No animation on first paint (`initial={false}`, a pre-placed knob, a pill that only animates after a real toggle).
   - Caused by the user: strong ease-out, starting at once.
   - The system speaking ("live", "listening", "now"): a slow loop, linear or a breathing ease-in-out.
2. **How often is it seen?** (frequency gate)

   | Tier | Examples | Treatment |
   |---|---|---|
   | Constant | hover, typing, chart hover, scrolling | colour or opacity only, 150ms or less, no movement |
   | Frequent | press, toggle, tab, copy, menu | 150–200ms, or a spring that retargets |
   | Occasional | modal, sheet, step change, alert | 200–320ms, with a small blur as the bridge |
   | Rare, first time | onboarding, reward, first success | the delight budget: bounce up to .45, decorative shapes, choreography |

   Keyboard-triggered and high-frequency actions don't animate. Drag and resize are instant; nothing animates while the user is dragging.
3. **Name one purpose.** Feedback (press, tick, shake), state (label swap, shimmer, pulse), spatial (sheet from the foot, menu from its trigger, sliding pill), bridge (blur-fade, height following content), or delight (rare tier only). Data and the words being read never move for style.
4. **Cheapest tool that works.**
   - CSS transition for state changes (it retargets).
   - CSS keyframes only for mount entrances that must stay smooth while the page loads (a modal). A menu is a transition, since it reopens.
   - Registered `@property` for animating mask lengths.
   - Web Animations API for a one-off measured height.
   - A motion library for springs, shared layout, exits and choreography.
   - Raw pointer events for drags.
5. **Properties.** `transform` and `opacity`; `filter: blur()` as a bridge; `clip-path` for reveals and rounded clipping. Width or height only when measured. Name every property; never `transition: all`.
6. **Curve, duration or spring.** Tables below. Exits are quicker than entrances.
7. **Interruption.** Anything that can be re-triggered uses a transition or a spring, never keyframes. Springs keep velocity through an interruption.
8. **Layout stability.** Nothing around it moves. Both states share a grid cell; heights are reserved; measurements happen before paint.
9. **Reduced motion ships with it.** Fewer and gentler, not zero.
10. **Touch.** Hover only under a fine pointer; sheets drag only on phones.
11. **Check it.** Slow it down, look again the next day, check both themes and a phone.

## 2. Curves

| Token | Value | Use |
|---|---|---|
| `--ease-out` | `cubic-bezier(.23, 1, .32, 1)` | The default. Anything the user caused: press, swap, menu, modal, sheet open, enter, exit. Hover and colour changes use it too. |
| `--ease-move` | `cubic-bezier(.22, 1, .36, 1)` | Long moves of large objects: a panel resizing, a card flipping (400–450ms). |
| `--ease-drawer` | `cubic-bezier(.32, .72, 0, 1)` | A sheet after the finger lets go: spring back 400ms, slide out 300ms. |
| `--ease-in-out` | `cubic-bezier(.77, 0, .175, 1)` | One-off: a card folding to its header (250ms), where both ends stay on screen. Don't reach for it elsewhere. |
| Material standard | `cubic-bezier(.4, 0, .2, 1)` | Optional for measured width and height changes: rail width (220ms), row height (140ms), a disclosure (320ms), a list re-laying out (280ms). `--ease-out` is the default; pick one per product. |
| linear | | Constant loops only: shimmer, a ring turning, decorative rotation. |
| ease-in-out | | Breathing and pulses only: skeletons, a live ring. |

**Never ease-in on UI.** Built-in `ease-out` curves are too weak for movement; use the strong one. A colour-only fade with no movement (a row highlight) may use the CSS `ease-out` keyword.

**Tailwind gotcha:** in v4 the bare `ease-out` class is `cubic-bezier(0, 0, .2, 1)` unless you redefine `--ease-out` in `@theme`. Write `ease-[var(--ease-out)]` or `[transition-timing-function:var(--ease-out)]` and it can't bite. See [tokens.md](tokens.md).

## 3. Durations

| Duration | Use |
|---|---|
| 80ms | a fade that carries no news: chart bars on a new range, rail contents before the rail moves |
| 100–120ms | small exits: axis labels hiding, a menu or popover closing, a phone menu closing |
| **150ms** | the workhorse: press, hover colour, toggle colour, every swap's exit, a menu or popover opening, a phone menu opening |
| **200ms** | content swaps, overlay fade, modal exit, sheet exit, copy tick, the reduced-motion fallback |
| 220ms | rail width |
| **240ms** | modal card entrance |
| 250ms | step blocks entering, a card fold |
| 300ms | page sections entering, a modal following its content's height, accordion chevron |
| 320ms | a sheet rising |
| 400–500ms | springs and long geometry only, never a plain fade |

**Exits are faster than entrances:**

| Element | In | Out |
|---|---|---|
| Text or panel swap | 250ms | 150ms |
| Desktop modal | 240ms | 200ms |
| Desktop side panel | 240ms | 200ms |
| Menu, dropdown, popover | 150ms | 120ms |
| Phone sheet | 320ms | 200ms |
| Phone menu | 150ms | 120ms |

**Holds:** toast 6000ms; copied tick 1000ms (1500ms on a pill); a rotating hint 2600ms (time to read the longest); a finishing beat 260ms before a 420ms fade.

## 4. Springs

Always written as `{ type: "spring", bounce, duration }`, never as stiffness and damping. Bounce rises with rarity; a small part that stays inside its control (a toggle's pill, a switch knob) may bounce on every use.

| Bounce / duration | Use |
|---|---|
| 0 / 0.5s | camera pans. No bounce on a camera. |
| 0.12 / 0.4s | every segmented toggle's pill: a control's (Live / All, 7 / 30 days) and a page-level one (theme Light / Dark) |
| 0.2 / 0.35–0.5s | height reveals, a page-entrance rise, progress fills |
| 0.28 / 0.4s | a celebratory modal (rare) |
| 0.2 / 0.45s | a switch knob |
| 0.32–0.45 / 0.5–0.7s | a reward toast and its shapes (rare tier only) |

**Springs stay inside their containers.** A clipped overshoot still shows: the pill flattens against the end of its track. So the bounce is set by the room it has. The overshoot grows with how far the part travels, roughly travel × e^(−π·(1−bounce)/√(1−(1−bounce)²)): at `.35` a pill crossing 100px overshoots ~7px, past a toggle's 4px inset; at `.12`, under a pixel. Keep `overflow: hidden` as a backstop only.

## 5. Travel, blur and scale

**Travel grows with the size of what moves:**

| Element | Travel |
|---|---|
| phone menu | 4px |
| text and label swaps | 6px |
| step blocks, form views, a small celebratory modal | 8px |
| page sections, modal card | 16px |
| toast exit | 24px |
| sheet | 100% of its own height plus 48px (the grab handle over its top edge) |

**Blur is the bridge.** It hides the seam where one thing becomes another. It follows the size of what swaps, not the distance:

| Blur | Use |
|---|---|
| 2px | small text: button labels, rotating hint words |
| 4px | panels, icons, chevrons, the modal card |
| 6px | headline-size text, a whole step |
| 8px | a large panel entering |

Flat, minimal surfaces (a plain sign-in page) can skip blur entirely and only fade and rise.

**Scale:**
- Press `.97` (see the ladder in [buttons-and-controls.md](buttons-and-controls.md)).
- Enter from `.95–.97` (a menu from `.97`), never from 0.
- Icon swaps `.5 ↔ 1` with a crossfade.
- Decorative shapes may start at `.2–.6`. UI never does.

**Stagger:** 40–80ms between children. Page sections 60ms; blocks inside a step 40ms; decorative shapes 50–80ms.

## 6. Patterns

### Press
`active:scale-[0.97]`, `transition-[transform,scale,<colour property>]`, 150ms, strong ease-out. In CSS, so a fast second press retargets instead of restarting. Disabled: `active:scale-100`.

### Hover
Colour or background only, 150ms on `--ease-out`. Nothing moves. Fine pointer only; touch gets the same look on `:active`.

In a list or a menu every row has its own hover fill, which fades in and out where it is. Never one shared highlight that slides from row to row: it makes the list look as if it is shuffling.

### Menu and popover
Opens from its trigger: `scale(.97)` plus opacity to 1 in 150ms; closes in 120ms with the same values in reverse; `transform-origin` at the trigger edge. Both are transitions, so a quick reopen retargets; the menu stays mounted and takes `visibility: hidden` once the exit ends. The trigger's chevron turns over while it is open (see Chevrons). Library popovers: fade + zoom from .95 + a 2px slide from the trigger side. Icon tooltips: zero delay.

### Desktop modal
- Overlay fades in 200ms.
- Card in: 240ms from opacity 0, `translateY(16px)`, `blur(4px)`.
- Card out: 200ms, the same values in reverse; keep it mounted until the exit finishes.
- The card stays centred; modals don't scale from their trigger.
- Steps inside: content keyed and faded in over 200ms; height follows the measured content over 300ms.

### Desktop side panel
Slides in from `translateX(100%)` to 0 in 240ms on `--ease-out`; out in 200ms. No fade or blur on the panel. Reduced motion: a 200ms crossfade.

### Phone sheet
- Rises from `translateY(calc(100% + 48px))` to 0 in 320ms; sinks back there in 200ms. The extra 48px takes the grab handle, which rides over the top edge, off screen too. **No fade and no blur**: the sheet stays solid the whole way.
- Drag moves the sheet with the CSS `translate` property, which stacks on top of the enter/exit `transform` so neither interrupts the other.
- After a release it springs back in 400ms or slides out in 300ms, both on `--ease-drawer`.
- The grab handle scales to `.94` when pressed, 150ms.
- The rest of the physics (slop, close thresholds, cancels) in [mobile.md](mobile.md).

### Phone menu panel
150ms in, 120ms out, opacity plus a 4px drop, strong ease-out. No transform once open (so nothing inside is pinned to a transformed parent). `inert` while closed. The hamburger's two 1.5px lines slide to the middle and turn 45° into an × in 160ms, transform only; at rest each line sits on a whole pixel.

### Collapsing a rail or panel
Contents fade out together (80ms), then the width animates (220ms, `--ease-out` or Material standard), then contents fade back in together. Flip the state while nothing is visible. Contents are pinned at full width, so they never slide or reflow. Never fade icons in before their text.

### Sliding selection pill
One shared-layout element. In every segmented toggle, a control's or a page-level one, it springs with `{ bounce: 0.12, duration: 0.4 }`, so it settles short of the track's ends (`overflow: hidden` stays as a backstop). The first placement snaps. The pill marks the choice only; hover never moves it. Optional stretch while travelling, capped at 3px (`scaleX(1 + min(0.1, 3 / width))`) on a nested element so it composes with the layout transform. Text colour changes over 150ms. Each toggle gets its own layout id.

### Switch knob
From the track's start to its end (flex; the move is a layout animation), 3px in either way in a 52×26 track (4px in a phone's 51×31), spring `{ bounce: 0.2, duration: 0.45 }`. Track colour 150ms. First render doesn't animate. Reduced motion: instant, the knob and the track colour both.

### Label swap (loading, done)
Both states in one grid cell. New state rises from +6px, old leaves to −6px, both with `blur(2px)`, 200ms, strong ease-out. No animation on mount. See [buttons-and-controls.md](buttons-and-controls.md).

### Content arriving after a choice
Opacity plus `blur(4px)` to 0, 200ms, no travel. Swapping an empty state for inputs: the empty state fades out while the inputs fade in, in place. No scale, no rise.

### Step change in a flow
The old step leaves as one block in 150ms (−8px, 6px blur). The new step un-blurs over 250ms while its blocks rise 8px, 40ms apart. Nothing waits: the fields take input at once.

### Chevrons
A menu trigger's chevron turns over while its menu is open: `rotate: 180deg`, 150ms on `--ease-out`, and back as it closes. Reduced motion: it flips at once. A disclosure's chevron, which also changes ink, doesn't turn: stack two (down in ink-10, up in ink-12) and crossfade with a 4px blur, 200–300ms.

### Copy
The tick shows on the click itself, before the clipboard answers. Icon to tick: crossfade plus scale .5 ↔ 1, 200ms. Tick drawn at 1.3×, held 1000ms (1500ms on a pill). If the clipboard refuses, or there is none, the icon comes straight back: never a tick for a copy that didn't happen. The failure message is in [buttons-and-controls.md](buttons-and-controls.md). No toast for a copy that worked.

### Rows appearing and leaving
Three beats, the same both ways: content fades out (100ms), height changes (140ms, `--ease-out` or Material standard), new content fades in (120ms). When adding, the table lines are revealed by the height change before the text fades in, as if they were already there. Under reduced motion every duration is 0.

### New row highlight
Background ink-a4 to transparent over 700ms, the CSS `ease-out` keyword (colour only, nothing moves).

### Page entrance
Sections fade up 16px over 300ms, 60ms apart. Only on route mount. The same entrance on every page.

### Data
Chart bars fade in (80ms) on a new range. They never sweep left to right and never grow for style. Hover dims the other bars to .35 over 150ms. The latest bar may pulse to mean "now". Figures never move.

### Disclosure
`height: 0` to `auto` plus opacity, spring `{ bounce: 0.2, duration: 0.35 }` or a 300–320ms tween (`--ease-out` or Material standard). Add a few px of padding with a matching negative margin so child shadows aren't clipped.

### Shake (blocked)
The element shakes where it stands, `x: [0, -6, 6, -4, 4, 0]` over 420ms, and the UI says why (a short neutral toast or a line of text).

### Live and waiting states
- Shimmer on a title while waiting: a gradient ink-12 / ink-9 / ink-12 at 200% size, 2.2s linear, infinite.
- A ring that breathes in sync (opacity .25 to 1, peaking at 75% as the shimmer crosses the words) and turns once every two breaths.
- Skeletons pulse between ink-a3 and ink-a4 (1–1.4s, alternate). No gradient sweep.
- Status dots for ongoing states ping, all on one shared clock.

### Toast (rare tier)
A 48px circle rises 140px (spring .32 / 0.5s); at 520ms it springs open to its measured width (spring .35 / 0.7s), clipped with `clip-path: inset(0 round 9999px)`. The title follows 140ms later. Leaving: decorations go first, then the pill drops 24px and fades over 200ms. **A toast wider than 600px skips all this and fades in place** (a wide expansion reads as a stretch). Reduced motion takes the same fade.

## 7. Interruption and staging

- Nothing re-triggerable uses keyframes.
- Drag uses `translate`, separate from the enter/exit `transform`.
- Hold the measured height mid-ease; never jump to `auto`.
- Stage exits so content leaves before its frame. Choreograph in steps, never all at once, but keep the whole sequence quick.
- Unmount only after the exit has finished; timers match the durations.
- Don't animate on drag or resize. A resize handle appears after the panel has settled.
- Reuse an existing animation exactly before writing a new one. The same transition everywhere for the same job.

## 8. Layout stability

- Swapping states share one grid cell, sized to the larger.
- Reserve height for rotating text (the longest option).
- Measure in a layout effect, before paint.
- Rest positions land on whole pixels so lines stay crisp.
- Render nothing until a layout decision is known, so nothing moves when it is.

## 9. Reduced motion

Respect `prefers-reduced-motion` by softening, not deleting.

| Normal | Reduced |
|---|---|
| travel, blur, scale, spin | a 150–200ms opacity crossfade |
| a loop that carries state (live, waiting) | keeps only its opacity pulse |
| height changes | instant |
| a toggle's sliding pill | a 150ms tween |
| a switch knob | instant, the knob and its track colour both |
| video autoplay | holds the first frame |
| press scale | may stay (it's feedback, not travel) |

Add `motion-reduce:transition-none` (or the library equivalent) to every custom transition.

## 10. Don't

- Animate keyboard actions, typing, drag, resize or figures.
- Use `transition: all`, ease-in, or scale from 0.
- Use overshoot except on a small part held by its control (a toggle's pill in its clipping track, a switch knob), tiny confirmations and the rare tier.
- Slide one shared hover highlight from row to row.
- Run two unrelated motions at once in the same place.
- Shimmer, tilt or glow cards for decoration.
- Leave a transition without a reduced-motion path.

## Credit

Principles adapted from Emil Kowalski: decide whether before how, frequency sets the budget, every motion has a purpose, strong custom ease-out by default and never ease-in, short durations with faster exits, transform and opacity, never from scale 0, origin at the trigger (modals exempt), transitions or springs for anything interruptible, momentum-based sheet dismissal, small staggers, and softening rather than removing motion for reduced-motion users. See [animations.dev](https://animations.dev).
