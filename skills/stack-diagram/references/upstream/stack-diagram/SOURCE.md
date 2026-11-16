# stack-diagram source record

This is an inactive provenance record, not an agent entrypoint. The skill derives from
stack-diagram by caru-ini (MIT). The pin, `75dbd3e3c6fe28844322e6064d3a947b870a6c61`, is the
revision the original hashes in `source-manifest.json` were taken from:
<https://github.com/caru-ini/stack-diagram/tree/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram>.
Later upstream changes were adapted selectively, without moving the pin; see "Later incorporation".
`LICENSE` is the upstream root notice, unchanged. It is used in place of the skill-level
copy, which differs only by a note about the font files left out here. `LICENSE-Orbyn.txt`
covers Orbyn adaptations and additions. Use the maintained `stack-diagram` skill.

`source-manifest.json` lists every shipped file by its path under the skill root, with its
upstream path and its original and maintained hashes. `snapshot.json` pins this folder.
Editing a listed file means refreshing both records.

## Selected

`assets/template.html`, `assets/generic/` (five pictograms, unchanged), `references/geometry.md`,
`references/tsx.md`, `scripts/build.py`, `scripts/render_png.py`, `scripts/fetch_icons.py` and
the `SKILL.md` workflow. Icon and AWS guidance moved from `SKILL.md` to `references/icons.md`
and `references/aws.md`.

## Excluded, never copied

- `assets/fonts/`: Geist and JetBrains Mono woff2 files, their OFL texts and README.
- `docs/*.png`, `README.md`, `.github/workflows/release.yml`, `.gitignore`.
- The template's "made with" link and the instruction to keep it.
- Install commands, host-specific claims and the publishing delivery option.

## Changed

- Fonts: system stacks only. `%%FONT_*%%`, `@font-face` and `--fonts` are gone.
- Logos: nothing branded ships. `fetch_icons.py` is offline unless given `--allow-network`,
  refuses a folder Git would commit, and falls back to `assets/generic` and records it.
- Fetching: https only, no URL credentials, https-only redirects, size limits, socket and
  total timeouts, type taken from bytes, slug validation. Upstream deletion of `<name>.*`
  now spares non-icon files.
- SVG: new `scripts/sanitise_svg.py`, an element allowlist applied at fetch and again at build.
- `build.py`: `%%CREDITS%%` from the manifest, `%%TITLE%%`, `%%KICKER%%`, `%%LEDE%%` and
  `%%FOOT%%` placeholders, a view-time load check, atomic writes.
- `render_png.py`: stdlib DevTools pipe to an existing Chrome, sandbox on, no install path, a
  network request fails the render, default capture `.page` so the legend and credit stay in
  the PNG.
- `template.html`: higher muted and accent contrast in the light theme, keyboard focus on the
  scroller, reduced motion.
- Eight original pictograms in `assets/generic`: box, branch, check, database, document, folder,
  link, terminal.

## Later incorporation

The pin above did not move. Two later upstream changes were adapted selectively:

- `1ed53e3e9525364ae5d82e0430f2bb3f7ef4c838` (MIT, caru-ini): Google Cloud and Azure icon
  support. The `gcp/` and `azure/` spec forms and name tables in `scripts/fetch_icons.py`,
  the `group gcp` and `group azure` styles in `assets/template.html`, and the vendor rules
  in `references/gcp-azure.md`.
- `9175bde8449cc8f5390d6eb72ecc2e1f5bfe21f3` (MIT, caru-ini, "k8s icon support"): Kubernetes
  icon support. The `k8s/` spec form, the icon table and aliases in `scripts/fetch_icons.py`,
  and the pinned kubernetes/community commit `307ae50e8e4246de172f195c73e3f026b4f0c7ff` that
  upstream uses. The icons (Apache-2.0 or CC-BY-4.0) are read at run time from `raw.githubusercontent.com`
  and are never copied here. Guidance is in `references/kubernetes.md` and `references/icons.md`.
  The `k8s-*` and `kubernetes-*` slug forms are not adopted, so a product such as
  `kubernetes-dashboard` stays on the usual chain.

The fetch code follows this skill's package class, limits and fallback rules, not upstream's
structure. Not adopted from either: gallery sharing (`share.py` and the publish step), which
posts to a third-party site, and the tile radius change of `f333b4716…` (`--radius-tile`
8px to 12px with redrawn examples), because this template keeps its own 8px styling.

Source identity is not runtime proof.
