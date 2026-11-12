# Build method

Detail for the numbered method in `SKILL.md`.

## How hard to press

Build it the way a product designer builds a launch page they will be judged on. The gold examples are the bar: if yours is the emptier, flatter or smaller one beside the closest gold, fix that first. Then picture the most exacting designer you know screenshotting the one wrong thing: a dot off its avatar, a unit on its own line, copy touching a card. If you can picture that screenshot, you have found the next fix.

## Why each failure reads wrong

- Too much: the more detail, the more it looks generated.
- Flat: with every object the same weight in the same bordered card, the eye has nowhere to land.

## Plan sizes

An animation plays as a loop, once in view, or on hover. Design at shown size: about 720 × 340 for a hero beside copy, 900 to 1100 wide for a full-width hero, 400 × 300 for a card.

## Working copy

Copy the kit root outside the library, or copy `kit/` into the project's React app. Run `npm install --ignore-scripts` only in that copy, so the library stays free of `node_modules` and lockfiles. `npm run dev` serves the playground on 127.0.0.1. Offline, use dependencies already on disk and report what you could not run.

## Film command

`node scripts/film.mjs "<url>/?capture=<yours>" --select '#example' --gate` at shown width, again with `--width 390`, and with `--states`. `?capture=<yours>` films the folder copied to `examples/<yours>/`.

## Worked failure

A brief asks for a hero showing invoice approval. The first build is a complete window, 480 wide, centered on a tinted plate, with real names in all twelve rows. The gate passes, but beside `static-card` it reads as a screenshot. Largest fault first: remove the plate, run the window off the bottom edge at 720 wide, keep real words on the selected row and its total, and turn the other rows into bars. Then the approval moves the total, because that is the payoff.
