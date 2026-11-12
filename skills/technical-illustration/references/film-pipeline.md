# Film pipeline

Detail for MP4 delivery, step 6 of `SKILL.md`.

1. Use the original [motion-film exporter](../../orbyn-ui-design/examples/spatial-review/motion-films.md). Author a validated scene/beat specification and run the existing-tool pipeline; inspect actual probe/decode/playback receipts and unsupported parity cells.
2. Run `python3 scripts/check-code-only.py <source>` before rendering.
3. Run `python3 scripts/flash-check.py film.mp4` on the finished file; exit 1 means more than three flashes in a second, so fix the source and render again.
4. When the film carries words or a logo, also run `scripts/legibility-check.py` on a plate.
5. For audio-reactive frames, onsets and supplied lyrics, start with `python3 scripts/audio-bake.py` as [music timing](music-timing.md) shows.
