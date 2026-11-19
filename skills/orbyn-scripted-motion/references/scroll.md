# Scroll-linked scenes

Try native `animation-timeline: scroll()` / `view()` first (see
[animation performance](../../orbyn-ui-design/references/animation-performance.md)).
Use ScrollTrigger when you need pinning, snapping to labels, scrub smoothing,
horizontal scenes driven by vertical scroll, or support beyond native timelines.

```js
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger); // once, at app level
```

## Two modes, never both

- **Triggered:** `toggleActions: "play none none reverse"` plays on a threshold.
- **Scrubbed:** `scrub: true` locks progress to scroll; `scrub: 0.6` lets the
  playhead trail by that many seconds. When both are set, scrub wins; pick one.

`start` and `end` read `"<trigger position> <viewport position>"`, such as
`"top 80%"` or `"center center"`. `end: "+=600"` is pixels past the start,
`"+=100%"` a viewport height. Functions are allowed; add `invalidateOnRefresh: true`
when values depend on measured size. `markers: true` only while developing.

## Pinned, scrubbed scene

```js
const scene = gsap.timeline({
  defaults: { ease: "none" },
  scrollTrigger: {
    trigger: ".tour",
    start: "top top",
    end: "+=1800",
    pin: true,
    scrub: 0.6,
    anticipatePin: 1,
  },
});

scene
  .from(".tour__shot--1", { autoAlpha: 0, y: 24 })
  .to(".tour__shot--1", { autoAlpha: 0 }, "+=0.5")
  .from(".tour__shot--2", { autoAlpha: 0, y: 24 }, "<")
  .from(".tour__caption", { autoAlpha: 0 }, ">-0.2");
```

- Pin the section and animate its children; do not animate the pinned element.
- Scrubbed motion uses `ease: "none"` unless a step needs shape; scroll supplies
  the easing.
- `pinSpacing` defaults on (a spacer keeps layout); turn off only when layout is
  handled elsewhere.
- `snap: "labels"` or a progress step lets a scene settle on its beats.
- ScrollTrigger goes on the timeline or a top-level tween, never on a child, and
  scenes are never nested inside another timeline.

## Horizontal gallery by vertical scroll

```js
const track = document.querySelector(".gallery__track");
const distance = () => track.scrollWidth - window.innerWidth;

const slide = gsap.to(track, {
  x: () => -distance(),
  ease: "none", // required, or scroll and position drift apart
  scrollTrigger: {
    trigger: ".gallery",
    pin: true,
    scrub: true,
    end: () => "+=" + distance(),
    invalidateOnRefresh: true,
  },
});

gsap.from(".gallery__item--3 img", {
  scale: 1.1,
  scrollTrigger: { trigger: ".gallery__item--3", containerAnimation: slide, start: "left 70%" },
});
```

A ScrollTrigger that uses `containerAnimation` cannot pin or snap.

## Batches and standalone triggers

`ScrollTrigger.batch(".card", { onEnter: (els) => gsap.to(els, { autoAlpha: 1, y: 0, stagger: 0.08 }), start: "top 85%" })`
groups elements entering together; `onEnter`, `onLeave`, `onEnterBack` and
`onLeaveBack` each receive arrays. Do not pass
`trigger`, `scrub`, `snap` or `toggleActions` to a batch. For a progress readout
or a UI toggle use `ScrollTrigger.create({ trigger, start, end, onUpdate })` and
read `self.progress`.

## Order, refresh and cleanup

- Create triggers top to bottom in page order, or set `refreshPriority` so they
  refresh in that order; pin spacing depends on it.
- `ScrollTrigger.refresh()` after layout shifts that resize still-pending content
  (fonts, images, data). Window resize refreshes by itself, debounced.
- Kill by owner, not globally: create inside a context and `revert()`, or give
  triggers an `id` and call `ScrollTrigger.getById(id)?.kill()`.
- Custom smooth-scroll libraries need `ScrollTrigger.scrollerProxy()` and an
  update listener; prefer native scroll when the design allows.
- On touch devices a pinned scene fights browser chrome and address-bar resize;
  test on a real phone, and consider an unpinned version behind `matchMedia`.
