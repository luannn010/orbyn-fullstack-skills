# Plugins

All plugins ship in the public `gsap` package (`import { Flip } from "gsap/Flip"`).
No token or private registry is needed; never add an `.npmrc` for one. Register
each plugin once, before use, with `gsap.registerPlugin(...)`. Lazy-load a plugin
used on a single route. Adding any of them is still a dependency decision for the
project, and none belongs in a no-code animation builder (see the licence boundary
in [SKILL.md](../SKILL.md)).

## Flip: animate between layouts

Capture, change the DOM, then play from the old state.

```js
import { Flip } from "gsap/Flip";
gsap.registerPlugin(Flip);

function setView(grid, mode) {
  const state = Flip.getState(".tile");   // 1. First
  grid.dataset.view = mode;               // 2. Last: change class, order or parent
  Flip.from(state, { duration: 0.4, ease: "standard", absolute: true, nested: true }); // 3. Invert + Play
}
```

Give tiles a `data-flip-id` when elements are replaced or re-parented. Use
`absolute: true` when siblings must not reflow mid-flip, `nested: true` for
transformed children, and `onEnter` / `onLeave` to fade added or removed items.
Prefer CSS View Transitions for page-level shared elements when supported.

## SplitText: text in parts

```js
import { SplitText } from "gsap/SplitText";
gsap.registerPlugin(SplitText);

SplitText.create(".headline", {
  type: "lines, words",   // split only what you animate
  mask: "lines",
  autoSplit: true,        // re-split on resize and font load
  onSplit: (self) => gsap.from(self.lines, { yPercent: 100, stagger: 0.08 }),
});
```

Returning the tween from `onSplit` lets it be replaced on re-split. It adds
accessible labelling by default; do not remove it. Split after fonts load or use
`autoSplit`. `revert()` restores the original markup, and a surrounding context
does so on cleanup. Avoid character splits on long paragraphs.

## Draggable and Inertia

```js
import { Draggable } from "gsap/Draggable";
import { InertiaPlugin } from "gsap/InertiaPlugin";
gsap.registerPlugin(Draggable, InertiaPlugin);

Draggable.create(".sheet", { type: "y", bounds: ".viewport", inertia: true, edgeResistance: 0.8,
  onDragEnd() { /* commit on distance or velocity, or snap back */ } });
```

`type` is `"x"`, `"y"`, `"x,y"`, `"rotation"` or `"scroll"`. Provide a keyboard
and non-gesture route to the same action; the gesture is an enhancement. Kill the
instance on teardown (`draggable.kill()`), or create it in a context. Gesture feel
rules (follow the pointer exactly, physics on release) live in
[motion](../../orbyn-ui-design/references/motion.md).

## Observer

`Observer.create({ target, type: "wheel,touch,pointer", onUp, onDown, tolerance })`
normalizes input for swipe or step-through sections without tying to scroll
position.

## ScrollToPlugin

`gsap.to(window, { scrollTo: { y: "#billing", offsetY: 80 }, duration: 0.6 })`
for animated anchor jumps; `"max"` targets the end. Respect reduced motion by
jumping instantly. Pair with `scroll-margin-top` where CSS suffices.

## MotionPath

`gsap.to(".marker", { motionPath: { path: "#route", align: "#route", alignOrigin: [0.5, 0.5], autoRotate: true }, duration: 3 })`
moves an element along an SVG path. Do not combine with the same element's
`x`/`y` tweens.

## SVG plugins

- **DrawSVG:** `drawSVG: "0% 100%"` reveals a stroke; the element needs a visible
  stroke, and it affects strokes only.
- **MorphSVG:** `morphSVG: { shape: "#target", shapeIndex: 2 }`; convert primitives
  with `MorphSVGPlugin.convertToPath()`; adjust `shapeIndex` for twisted morphs.
- **ScrambleText, TextPlugin:** decorative text effects; keep the final text in
  the DOM from the start for assistive tech.

## Easing plugins

`CustomEase.create("name", "0.2,0,0,1")` accepts a cubic-bezier or SVG path; use it
to mirror project tokens. `CustomBounce` and `CustomWiggle` build specific
character; use them sparingly and only when the design asks.

## ScrollSmoother

Needs ScrollTrigger, a wrapper/content structure, and changes native scroll
behavior (anchors, find-in-page, accessibility zoom). Treat as a last resort, with
the project's approval.
