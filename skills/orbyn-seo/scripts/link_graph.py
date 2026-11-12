#!/usr/bin/env python3
"""Internal link graph of a built static site: orphans, weak pages, broken links and click depth.

Read-only and offline: it parses the `.html` files under `--site` and never fetches the network or writes a file.
A page's URL is its path in the output folder: `dir/index.html` is `/dir/`, `about.html` is `/about`; `/about/` and
`/about.html` count as aliases of that page. Relative links resolve against the page, query and fragment are dropped,
and `mailto:`, `tel:`, `javascript:` and links to other origins are skipped. Absolute links count as internal only
when they point at `--base-url`. Links marked `rel=nofollow` are still checked for breakage but pass no inbound
count and open no path for the depth search. Inbound counts distinct linking pages, never the page itself.
A page is weak when it has at least one inbound link but fewer than `--min-inbound`; orphans are listed apart.
Standard library only.

A page file is skipped, with its reason listed in the report, when it resolves outside `--site` (a symlink out) or is
larger than 20 MB. A malformed href such as `http://[x` is counted as a broken link.

Exit codes: 0 for a successful read, 2 for bad input (missing folder, no pages, unknown home).
"""
import argparse
from collections import deque
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import posixpath
import sys
from urllib.parse import unquote, urljoin, urlsplit

SKIP_SCHEMES = ('mailto:', 'tel:', 'javascript:', 'sms:', 'data:', 'ftp:')
TOP_LINKING = 5
MAX_BYTES = 20 * 1024 * 1024


class Unusable(Exception):
    pass


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        attrs = dict(attrs)
        href = attrs.get('href')
        if href is None or not href.strip():
            return
        rel = (attrs.get('rel') or '').lower().split()
        self.links.append((href.strip(), 'nofollow' in rel))


def key_of(path):
    """Alias-free key of a URL path: no `index.html`, no `.html`, no trailing slash (root stays `/`)."""
    path = posixpath.normpath(path) if path else '/'
    if not path.startswith('/'):
        path = '/' + path
    if path.endswith('/index.html'):
        path = path[:-len('index.html')]
    elif path == '/index.html':
        path = '/'
    elif path.endswith('.html'):
        path = path[:-len('.html')]
    return path.rstrip('/') or '/'


def scan_site(site):
    """Return (pages {key: {'path', 'base', 'file'}}, files {posix path}, skipped [{file, reason}])."""
    pages, files, skipped = {}, set(), []
    for root, _dirs, names in os.walk(site):
        for name in names:
            full = Path(root) / name
            rel = '/' + full.relative_to(site).as_posix()
            if not name.endswith('.html'):
                files.add(rel)
                continue
            try:
                inside = full.resolve().is_relative_to(Path(site).resolve())
                size = full.stat().st_size
            except OSError as error:
                skipped.append({'file': rel, 'reason': f'unreadable: {error.strerror or error}'})
                continue
            if not inside:
                skipped.append({'file': rel, 'reason': 'resolves outside --site (symlink)'})
                continue
            if size > MAX_BYTES:
                skipped.append({'file': rel, 'reason': 'larger than 20 MB'})
                continue
            files.add(rel)
            if name == 'index.html':
                base = rel[:-len('index.html')]
                path = base
            else:
                base = rel
                path = rel[:-len('.html')]
            key = key_of(path)
            if key in pages and pages[key]['file'] < rel:
                continue
            pages[key] = {'path': path, 'base': base, 'file': rel, 'disk': full}
    return pages, files, sorted(skipped, key=lambda item: item['file'])


def resolve(href, page, origin):
    """The target URL path of an internal `href`, or None for a link that is skipped."""
    lowered = href.lower()
    if lowered.startswith(SKIP_SCHEMES):
        return None
    joined = urljoin('http://site.invalid' + page['base'], href)
    parts = urlsplit(joined)
    if parts.netloc.lower() != 'site.invalid':
        if parts.scheme not in ('http', 'https') or not origin or parts.netloc.lower() != origin:
            return None
    if urlsplit(href).path == '' and not urlsplit(href).netloc:
        return None  # a query-only or fragment-only link points back at the same page
    return unquote(parts.path) or '/'


def build(site, base_url, home):
    pages, files, skipped = scan_site(site)
    if not pages:
        raise Unusable(f'no .html pages under {site}')
    origin = urlsplit(base_url).netloc.lower() if base_url else ''
    home_key = key_of(unquote(urlsplit(home).path) or '/')
    if home_key not in pages:
        raise Unusable(f'home page {home} is not a page of the site')
    edges = []  # (source key, target key, nofollow)
    broken = set()
    link_count = 0
    for key, page in pages.items():
        parser = AnchorParser()
        parser.feed(page['disk'].read_text(encoding='utf-8', errors='replace'))
        for href, nofollow in parser.links:
            try:
                target = resolve(href, page, origin)
            except ValueError:
                link_count += 1
                broken.add((page['path'], href))
                continue
            if target is None:
                continue
            link_count += 1
            target_key = key_of(target)
            if target_key in pages:
                if target_key != key:
                    edges.append((key, target_key, nofollow))
            elif target in files and not target.endswith('/'):
                continue  # an asset or other file that exists
            else:
                broken.add((page['path'], href))
    return pages, edges, sorted(broken), link_count, home_key, skipped


def analyse(site, base_url, home, money, min_inbound):
    pages, edges, broken, link_count, home_key, skipped = build(site, base_url, home)
    followed = {}
    nofollow_in = {key: 0 for key in pages}
    for source, target, nofollow in edges:
        if nofollow:
            nofollow_in[target] += 1
        else:
            followed.setdefault(target, set()).add(source)
    inbound = {key: len(followed.get(key, ())) for key in pages}
    out = {}
    for source, target, nofollow in edges:
        if not nofollow:
            out.setdefault(source, set()).add(target)
    depth = {home_key: 0}
    queue = deque([home_key])
    while queue:
        current = queue.popleft()
        for target in sorted(out.get(current, ())):
            if target not in depth:
                depth[target] = depth[current] + 1
                queue.append(target)
    show = lambda key: pages[key]['path']
    order = sorted(pages, key=show)
    result = {
        'pages': len(pages),
        'links': link_count,
        'home': show(home_key),
        'min_inbound': min_inbound,
        'inbound': {show(k): inbound[k] for k in order},
        'nofollow_inbound': {show(k): nofollow_in[k] for k in order if nofollow_in[k]},
        'orphans': [show(k) for k in order if inbound[k] == 0 and k != home_key],
        'weak': [show(k) for k in order if 0 < inbound[k] < min_inbound and k != home_key],
        'broken': [{'source': source, 'href': href} for source, href in broken],
        'depth': {show(k): depth[k] for k in order if k in depth},
        'unreachable': [show(k) for k in order if k not in depth],
        'skipped': skipped,
        'money': [],
    }
    for path in money:
        key = key_of(unquote(urlsplit(path).path) or '/')
        if key not in pages:
            result['money'].append({'path': path, 'found': False})
            continue
        sources = sorted(followed.get(key, ()), key=lambda s: (-inbound[s], show(s)))
        result['money'].append({
            'path': show(key), 'found': True, 'inbound': inbound[key], 'depth': depth.get(key),
            'top_linking': [show(s) for s in sources[:TOP_LINKING]],
        })
    return result


def render(report):
    lines = [f"pages: {report['pages']}", f"internal links: {report['links']}", f"home: {report['home']}", '']
    lines.append('inbound (distinct linking pages)')
    for path, count in report['inbound'].items():
        extra = f" (+{report['nofollow_inbound'][path]} nofollow)" if path in report['nofollow_inbound'] else ''
        lines.append(f'  {count:>4}  {path}{extra}')
    for title, items in (('orphans (no inbound)', report['orphans']),
                         (f"weak (inbound below {report['min_inbound']})", report['weak'])):
        lines += ['', f'{title}: {len(items)}'] + [f'  {item}' for item in items]
    lines += ['', f"broken internal links: {len(report['broken'])}"]
    lines += [f"  {item['source']} -> {item['href']}" for item in report['broken']]
    lines += ['', 'click depth from home']
    levels = {}
    for path, level in report['depth'].items():
        levels.setdefault(level, []).append(path)
    for level in sorted(levels):
        lines.append(f'  {level}: ' + ', '.join(levels[level]))
    lines += ['', f"unreachable from home: {len(report['unreachable'])}"] + [f'  {p}' for p in report['unreachable']]
    if report['skipped']:
        lines += ['', f"skipped files: {len(report['skipped'])}"]
        lines += [f"  {item['file']}: {item['reason']}" for item in report['skipped']]
    if report['money']:
        lines += ['', 'money pages']
        for item in report['money']:
            if not item['found']:
                lines.append(f"  {item['path']}: not a page of the site")
                continue
            depth = 'unreachable' if item['depth'] is None else item['depth']
            top = ', '.join(item['top_linking']) or 'none'
            lines.append(f"  {item['path']}: inbound {item['inbound']}, depth {depth}, top linking: {top}")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Internal link graph of a built static site (read-only, offline).')
    parser.add_argument('--site', required=True, help='built HTML output folder, such as dist/, out/ or public/')
    parser.add_argument('--base-url', help='site origin, so absolute links to it count as internal')
    parser.add_argument('--home', default='/', help='home page path (default /)')
    parser.add_argument('--money', action='append', default=[], metavar='PATH', help='money page path; repeatable')
    parser.add_argument('--min-inbound', type=int, default=2, help='weak page threshold (default 2)')
    parser.add_argument('--json', action='store_true', help='print JSON instead of text')
    args = parser.parse_args(argv)
    try:
        site = Path(args.site)
        if not site.is_dir():
            raise Unusable(f'--site {args.site} is not a directory')
        if args.base_url and urlsplit(args.base_url).scheme not in ('http', 'https'):
            raise Unusable('--base-url must start with http:// or https://')
        report = analyse(site.resolve(), args.base_url, args.home, args.money, args.min_inbound)
    except Unusable as error:
        print(f'link_graph: {error}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
