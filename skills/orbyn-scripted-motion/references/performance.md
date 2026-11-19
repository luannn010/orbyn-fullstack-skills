# Utilities and performance

## gsap.utils

Pure helpers; no registration. Most take the value last or return a function when
the value is omitted.

| Helper | Use |
| --- | --- |
| `clamp(min, max, v)` | keep a drag or pointer value in range |
| `mapRange(inMin, inMax, outMin, outMax, v)` | pointer x to rotation, progress to opacity |
| `normalize(min, max, v)` | value to 0..1 |
| `interpolate(a, b, t)` | numbers, colors, objects |
| `snap(step or array, v)` | grid and step values |
| `wrap(min, max, v)` / `wrapYoyo` | carousels, cyclic indexes |
| `random(min, max, snap?)` | one value, or `random(a, b, true)` for a reusable function |
| `distribute({ base, amount, from, ease })` | function value for `stagger` or per-target spread |
| `pipe(f, g)` | compose transforms |
| `toArray(sel, scope)` | selector or NodeList to a real array, scoped |
| `selector(root)` | a scoped selector function for a component |

```js
const toTilt = gsap.utils.mapRange(0, window.innerWidth, -6, 6);
const setTilt = gsap.quickTo(".card", "rotationY", { duration: 0.4 });
window.addEventListener("pointermove", (e) => setTilt(toTilt(e.clientX)));
```

## Hot-path updates

- `gsap.quickTo(target, "x", { duration })` reuses one tween for values that update
  every frame (cursor followers, sliders). `gsap.quickSetter` writes without easing.
- For work tied to every frame use `gsap.ticker.add(fn)`; remove it on teardown.
- Do not create a new tween per mouse event.

## Keep it on the compositor

- Animate `x`, `y`, `scale`, `rotation`, `opacity`; avoid layout and paint
  properties. See [animation performance](../../orbyn-ui-design/references/animation-performance.md).
- `will-change: transform` only on elements that are about to animate, removed
  afterwards; never blanket `force3D` or `will-change` on lists.
- Batch DOM reads before writes; do not read layout (`getBoundingClientRect`,
  `offsetHeight`) between tweens created in a loop.

## Many elements

- Use one `stagger` instead of many tweens with manual delays.
- Animate only what is visible; virtualize long lists and skip off-screen items.
- Reuse timelines; do not build one per frame.
- Pause or kill loops when the tab or section is hidden.

## ScrollTrigger cost

- Pin only what must stay fixed; fewer pins, fewer refreshes.
- Refresh on real layout changes, not on every event.
- Prefer `scrub` with a small lag (about 0.5 to 1) and verify on a low-end phone.

## Measure

Check the claim, not the theory: record a performance trace on the slowest target
device, watch for long frames, layout and paint on the animated nodes, and compare
with the reduced-motion path. Report what was measured.
