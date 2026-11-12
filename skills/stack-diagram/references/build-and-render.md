# Build and render

Detail for steps 4 and 5 of `SKILL.md`.

## Build the HTML

Copy `assets/template.html` into the job folder. Replace the sample groups, edges and nodes, and fill `%%TITLE%%`, `%%KICKER%%`, `%%LEDE%%` and `%%FOOT%%`. Leave `%%CREDITS%%` for the build. Set `lang` on `<html>` to the label language. Keep colours and fonts behind the CSS tokens.

```bash
python3 scripts/build.py <job>/draft.html <job>/icons <job>/diagram.html
```

The build embeds icons as data URIs, sanitises every SVG again and writes the footer credit. It fails on an unresolved token or anything that would load at view time. For a dark default, set `data-theme="dark"` on `<html>`. To show a deploy to a platform that is a group, point the arrow at the most representative node inside it and label the edge.

## Render and look

```bash
python3 scripts/render_png.py <job>/diagram.html <job>/diagram.png --scale 2
```

This writes light and dark PNGs using an existing Chrome, with the title, legend and credit included. Pass `--selector .canvas` for the bare drawing. Set `CHROME_PATH` if discovery fails; the script installs nothing. Open both images and read them.

## Worked failure

An API node has its tile top at 120 and a database below it at 350. The first draft draws `M487 180 V344`, from the tile bottom. The render shows the line running through the name and role. Change the start to the box bottom, 120+100+6: `M487 226 V344`. Then list every vertical segment and ask which node boxes it passes between its two ends. The answer must be none.
