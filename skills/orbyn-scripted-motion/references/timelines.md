# Timelines, tweens and tokens

## Tween basics

`gsap.to()` animates to values, `from()` from them to the current state,
`fromTo()` states both ends, `set()` applies at once. Property names are camelCase
(`backgroundColor`). Prefer the transform aliases (`x`, `y`, `xPercent`, `scale`,
`rotation`) over a raw `transform` string; they compose in a fixed order and
survive repeated tweens. Relative values: `y: "+=16"`. Function values run once per
target: `x: (i) => i * 24`.

`from()` and `fromTo()` render their start state immediately. When two of them hit
the same property of one element, set `immediateRender: false` on the later one or
its start state overwrites the first tween's end.

## Tokens once, not per tween

Read the project's motion tokens and register them a single time:

```js
import { gsap } from "gsap";
import { CustomEase } from "gsap/CustomEase";
gsap.registerPlugin(CustomEase);

const css = getComputedStyle(document.documentElement);
// Tokens may be "200ms", "0.2s" or a bare number of ms; return seconds.
const ms = (name) => {
  const raw = css.getPropertyValue(name).trim();
  const n = parseFloat(raw);
  return raw.endsWith("ms") || !raw.endsWith("s") ? n / 1000 : n;
};
// CustomEase takes bare control points; strip a cubic-bezier() wrapper.
const bezier = (name) => css.getPropertyValue(name).trim().replace(/^cubic-bezier\((.*)\)$/, "$1");

CustomEase.create("standard", bezier("--ease-standard")); // "0.2, 0, 0, 1"
gsap.defaults({ duration: ms("--motion-base"), ease: "standard" });
```

Then tweens say `gsap.to(row, { y: 0 })` and inherit. Built-in names such as
`power2.out` are fine only when the project has no tokens or its tokens name them.

## Timeline structure

```js
const tl = gsap.timeline({ defaults: { duration: 0.3 }, paused: true });

tl.addLabel("panel")
  .from(".sheet", { yPercent: 8, autoAlpha: 0 }, "panel")
  .from(".sheet__row", { y: 8, autoAlpha: 0, stagger: 0.04 }, "panel+=0.1")
  .from(".sheet__cta", { scale: 0.96, autoAlpha: 0 }, ">-0.1");
```

Position parameter (third argument): a number is absolute; `"+=0.2"` / `"-=0.2"`
are relative to the timeline's end; `"label"` and `"label+=0.3"` anchor to a
label; `"<"` starts with the previous step and `">"` after it (`"<0.2"` offsets
from its start). Defaults on the constructor apply to every child. A timeline's
duration comes from its children, not from a `duration` option.

Nest a timeline with `master.add(child, "label")` to keep each scene separable and
testable. Compose with functions that return a timeline, so a parent decides when
and where it plays.

## Control

Keep the returned instance when you need control: `play()`, `pause()`,
`reverse()`, `restart()`, `seek("label")`, `progress(0.5)`, `timeScale(2)`,
`kill()`. A reversible open/close is one paused timeline played forward and
reversed, which retargets from the live position by construction. `tweenFromTo()`
plays a span between two labels.

## Choreography

Cast and relate the motions first, as in the
[choreography rules](../../orbyn-ui-design/references/motion.md). The stagger and
position values come from that cast, not from a fixed rhythm. Keep staggers off
frequent or keyboard-opened surfaces. `stagger` accepts `{ each, from, amount }`.
Use `overwrite: "auto"` so a second trigger replaces only the overlapping
properties of an active tween.

## Do not

- Chain steps with `delay` when a timeline can place them.
- Leave `repeat: -1` loops running off-screen or after unmount.
- Use `clearProps` casually: clearing any transform property clears the whole
  transform. Use it to hand control back to a stylesheet when a tween ends.
