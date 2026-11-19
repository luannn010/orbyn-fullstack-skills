# Framework lifecycle and cleanup

The same three rules in every framework: create after the DOM exists, scope
selectors to the component root, revert everything on teardown. A
`gsap.context()` collects each tween, timeline and ScrollTrigger made inside it,
so one `revert()` kills them and restores inline styles.

## React and Next.js

```tsx
import { useRef } from "react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
gsap.registerPlugin(useGSAP);

export function Onboarding({ step }: { step: number }) {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    (_ctx, contextSafe) => {
      gsap.from(".card", { y: 12, autoAlpha: 0, stagger: 0.06 });

      const onPress = contextSafe!(() => gsap.to(".cta", { scale: 0.97, yoyo: true, repeat: 1 }));
      const cta = root.current!.querySelector(".cta")!;
      cta.addEventListener("pointerdown", onPress);
      return () => cta.removeEventListener("pointerdown", onPress);
    },
    { scope: root, dependencies: [step], revertOnUpdate: true },
  );

  return <div ref={root}>{/* .card, .cta */}</div>;
}
```

- `scope` limits selector strings to the component. Pass refs for single targets.
- The hook's dependency array defaults to empty; add `dependencies` and
  `revertOnUpdate: true` when the animation must rebuild with state.
- Anything created later (event handlers, async callbacks) goes through
  `contextSafe`, or it is not reverted. Remove listeners in the returned cleanup.
- Without `@gsap/react`: `useEffect(() => { const ctx = gsap.context(fn, root); return () => ctx.revert(); }, [])`.
- Server rendering: gsap code runs only in effects, never during render. In
  Strict Mode effects run twice; cleanup must fully undo setup.
- Register plugins once at module or app level, not inside a rendering component.

## Vue 3 and Nuxt

```ts
const root = ref<HTMLElement | null>(null);
let ctx: gsap.Context | undefined;

onMounted(() => {
  ctx = gsap.context(() => {
    gsap.from(".row", { autoAlpha: 0, y: 8, stagger: 0.05 });
  }, root.value!);
});
onUnmounted(() => ctx?.revert());
```

In Nuxt, wrap setup in a client-only hook or `<ClientOnly>`; lazy-load rarely used
plugins with a dynamic `import("gsap/SplitText")` and register after it resolves.

## Svelte

```svelte
<script>
  import { onMount } from "svelte";
  import { gsap } from "gsap";
  let root;
  onMount(() => {
    const ctx = gsap.context(() => gsap.from(".item", { autoAlpha: 0, stagger: 0.05 }), root);
    return () => ctx.revert();
  });
</script>
<div bind:this={root}>...</div>
```

Svelte transitions and `animate:` directives cover simple enter/exit and list
reorders; reach for the engine when they do not.

## Vanilla and routers

Build inside one `gsap.context()` per page or widget and keep the handle. On route
change, call `revert()`. `ctx.add(fn)` runs `fn` at once; for a handler that fires later, register it as a
named method (`ctx.add("open", () => ...)`, then call `ctx.open()` from the listener)
so the tweens it creates still belong to the context, and remove the listener on
revert.

## Responsive and reduced motion

`gsap.matchMedia()` makes its own context and reverts when a query stops matching:

```js
const mm = gsap.matchMedia();
mm.add(
  { motion: "(prefers-reduced-motion: no-preference)", wide: "(min-width: 900px)" },
  ({ conditions }) => {
    if (!conditions.motion) return; // final state, no animation
    gsap.from(".hero__item", { y: conditions.wide ? 24 : 12, autoAlpha: 0, stagger: 0.08 });
  },
  rootEl, // optional scope
);
// teardown
mm.revert();
```

A `matchMedia` created inside `useGSAP` or a `context()` is reverted with it; do not create a `context()` inside a `matchMedia` handler, since the handler is already one. Use `gsap.matchMediaRefresh()`
to re-run handlers after an in-app reduced-motion toggle.

## Do not

- Create animations before the root element exists.
- Use unscoped selectors that can reach another instance of the component.
- Skip `revert()`; leaked ScrollTriggers keep measuring detached nodes.
