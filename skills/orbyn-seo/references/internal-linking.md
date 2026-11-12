# Internal linking

Links tell search engines which pages a site considers important, and they are how
readers move from an article to a product. Money pages that few pages link to, or
that sit far from the home page, are easy to miss for both.

## Measure

Build the site, then run the graph on the output:

```sh
python3 scripts/link_graph.py --site dist --base-url https://example.com --money /pricing --money /signup
```

It reads the built HTML only and reports pages, inbound links from distinct pages,
orphans, weak pages, broken internal links, click depth from the home page and, for
each money page, its inbound count, depth and top linking pages. Add `--json` for a
machine-readable report. It never fetches the network or writes files.

How it counts: inbound means distinct linking pages; `nofollow` links are checked
for breakage but add no inbound and no path, so a page reached only through them is
an orphan; weak pages exclude orphans; `/about`, `/about/` and `/about.html` are one
page; without `--base-url`, every absolute link counts as external; a malformed href
counts as broken. HTML files that resolve outside `--site` or exceed 20 MB are
skipped and listed. It exits 0 after a successful read and 2 for bad input.

## Fix, in order

1. Broken internal links and orphans.
2. Money pages buried deep (more than about three clicks is a useful warning sign):
   reach them from the home page or the main navigation.
3. Links from the pages that already earn visits to the money pages they relate to.

## Where links go

- Only where the linking page genuinely covers the target's subject; a forced link
  reads as spam to people and search engines alike.
- Early in the body rather than only at the end, since many readers never reach the
  end.
- A few new links per page, and one link per destination per page is enough.

## How anchors read

- The anchor text says what the destination offers, in a few plain words, so a
  reader can predict where it leads; vague text such as "click here" does not.
- Vary the wording across pages rather than repeating one phrase everywhere.
- Internal links stay followable: `nofollow` on your own pages throws away the signal
  you are trying to send.
- Change as little as possible: link words that are already there, or add a sentence
  that helps the reader by itself. Keep the author's paragraph intact.

Hubs and their children link both ways, and breadcrumbs follow the real hierarchy.
Run the graph again after the change and report the before and after numbers.
