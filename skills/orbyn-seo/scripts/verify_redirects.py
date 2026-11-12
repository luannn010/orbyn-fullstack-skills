#!/usr/bin/env python3
"""Check a redirect map offline and, with `--base`, against the live old site.

Offline checks always run: malformed entries, duplicate sources, self-redirects, chains inside the map (A to B and
B to C: it suggests A to C), loops, and with `--old-pages` the old paths that have no rule. Live mode requests
base + each source without following redirects, then follows the answer by hand for up to 5 hops and records every
status and Location. It only ever sends a request to the `--base` host or an `--allow-host`; a hop to any other host is
reported and not requested. A rule passes when the first response is 301 or 308, points straight at the expected
target (exact match after dropping the scheme, lowercasing the host and, in `--slash loose`, the trailing slash) and
the target finally returns 200. A final 3xx without Location or any non-200 final answer fails. Requests connect to
the parsed hostname and port; URLs with a username or password are never requested, and a bare `--allow-host host`
allows only the scheme's default port (`host:port` allows that port, the `--base` origin its own port). HEAD is used, with GET as the fallback on 405 or 501. Standard library only.

Exit codes: 0 everything passes, 1 any offline issue or live rule fails, 2 bad input.
"""
import argparse
import csv
import http.client
import json
from pathlib import Path
import sys
import time
from urllib.parse import quote, urljoin, urlsplit

MAX_HOPS = 5
USER_AGENT = 'orbyn-seo-redirect-check'
PERMANENT = (301, 308)
TEMPORARY = (302, 307)
DEFAULT_PORTS = {'http': 80, 'https': 443}
PATH_SAFE = "/%:@!$&'()*+,;=-._~"
QUERY_SAFE = PATH_SAFE + '?'


class Unusable(Exception):
    pass


def hostport(parts):
    """`host` or `host:port` of a split URL, lowercase, brackets on IPv6, the scheme's default port dropped."""
    host = parts.hostname or ''
    if ':' in host:
        host = f'[{host}]'
    port = parts.port
    if port and port != DEFAULT_PORTS.get(parts.scheme):
        host = f'{host}:{port}'
    return host


def norm(value, slash, hosts=()):
    """(host, path, query) of a path or URL; scheme and fragment dropped, host lowercased, default port dropped.

    A host listed in `hosts` (an origin such as the old site) is treated as a plain path. Raises ValueError on a
    malformed URL."""
    parts = urlsplit(value)
    host = hostport(parts)
    if host in hosts:
        host = ''
    path = parts.path or '/'
    if slash == 'loose':
        path = path.rstrip('/') or '/'
    return host, path, parts.query


def valid_ref(value):
    if not isinstance(value, str) or not value.strip():
        return False
    value = value.strip()
    try:
        parts = urlsplit(value)
        parts.port
    except ValueError:
        return False
    if parts.scheme in ('http', 'https'):
        return bool(parts.netloc)
    return value.startswith('/') and not value.startswith('//')


def load_map(path):
    """Raw entries as (from, to) pairs of whatever the file held."""
    try:
        text = Path(path).read_text(encoding='utf-8-sig')
    except (OSError, UnicodeDecodeError) as error:
        raise Unusable(f'cannot read --map {path}: {error}')
    if Path(path).suffix.lower() == '.json':
        try:
            data = json.loads(text)
        except ValueError as error:
            raise Unusable(f'--map {path} is not valid JSON: {error}')
        if isinstance(data, dict):
            return list(data.items())
        if isinstance(data, list):
            return [(item.get('from'), item.get('to')) if isinstance(item, dict) else (None, None) for item in data]
        raise Unusable('--map JSON must be a list of {from,to} objects or an object of from: to')
    reader = csv.DictReader(text.splitlines())
    fields = {(name or '').strip().lower(): name for name in reader.fieldnames or []}
    if 'from' not in fields or 'to' not in fields:
        raise Unusable('--map CSV needs a header row with from and to columns')
    return [(row.get(fields['from']), row.get(fields['to'])) for row in reader]


def offline_checks(entries, slash, hosts, old_pages):
    issues = []
    rules = []  # (from, to) valid, in file order
    for index, (src, dst) in enumerate(entries, 1):
        if valid_ref(src) and valid_ref(dst):
            rules.append((src.strip(), dst.strip()))
        else:
            issues.append({'check': 'malformed', 'from': src, 'to': dst, 'detail':
                           f'entry {index}: from and to must each be a path starting with / or an http(s) URL'})
    key = lambda value: norm(value, slash, hosts)
    first, seen = {}, {}
    for src, dst in rules:
        seen.setdefault(key(src), []).append((src, dst))
    unique = []
    for entries_for_key in seen.values():
        src, dst = entries_for_key[0]
        unique.append((src, dst))
        if len(entries_for_key) > 1:
            targets = {key(d) for _s, d in entries_for_key}
            kind = 'conflicting targets' if len(targets) > 1 else 'same target repeated'
            issues.append({'check': 'duplicate', 'from': src, 'to': dst,
                           'detail': f'{len(entries_for_key)} rules for one source ({kind}): ' +
                                     ', '.join(d for _s, d in entries_for_key)})
        first[key(src)] = dst
    for src, dst in unique:
        if key(src) == key(dst):
            issues.append({'check': 'self', 'from': src, 'to': dst, 'detail': 'redirects to itself'})
    reported_loops = set()
    for src, dst in unique:
        if key(src) == key(dst):
            continue
        path, current = [key(src)], key(dst)
        while current in first and current not in path:
            path.append(current)
            current = key(first[current])
        if current in first and current in path:
            cycle = path[path.index(current):]
            rotation = min(range(len(cycle)), key=lambda i: cycle[i])
            canonical = tuple(cycle[rotation:] + cycle[:rotation])
            if canonical not in reported_loops and len(cycle) > 1:
                reported_loops.add(canonical)
                names = [p[1] for p in canonical]
                issues.append({'check': 'loop', 'from': src, 'to': dst,
                               'detail': 'loop: ' + ' -> '.join(names + [names[0]])})
        elif len(path) > 1:
            final = first[path[-1]]
            issues.append({'check': 'chain', 'from': src, 'to': dst, 'detail':
                           f'chain of {len(path)} hops: ' + ' -> '.join([p[1] for p in path] + [current[1]]) +
                           f'; redirect {src} straight to {final}'})
    if old_pages is not None:
        for page in old_pages:
            try:
                known = key(page) in first
            except ValueError:
                issues.append({'check': 'malformed', 'from': page, 'to': None,
                               'detail': 'old page is not a valid path or URL'})
                continue
            if not known:
                issues.append({'check': 'missing', 'from': page, 'to': None, 'detail': 'old page has no redirect rule'})
    return issues, unique


def load_old_pages(path):
    try:
        lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise Unusable(f'cannot read --old-pages {path}: {error}')
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]


def parse_origin(entry):
    """(scheme or None, hostname, port or None) of an `--allow-host` or `--base` value."""
    text = entry.strip()
    try:
        parts = urlsplit(text if '://' in text else '//' + text)
        host, port = parts.hostname, parts.port
    except ValueError:
        raise Unusable(f'not a valid host: {entry}')
    if (not host or parts.username is not None or parts.password is not None or parts.path not in ('', '/')
            or parts.query or parts.scheme not in ('', 'http', 'https')):
        raise Unusable(f'not a valid host (no username, password or path allowed): {entry}')
    return parts.scheme or None, host, port


class Checker:
    def __init__(self, base, allow, slash, timeout, delay):
        self.base = base.rstrip('/')
        self.slash = slash
        self.timeout = timeout
        self.delay = delay
        _scheme, host, port = parse_origin(base)
        self.hosts = {hostport(urlsplit(self.base))}
        self.entries = [(None, host, port)] + [parse_origin(entry) for entry in allow]
        self.requests = 0

    def allowed(self, url):
        try:
            parts = urlsplit(url)
            host, port = parts.hostname, parts.port
        except ValueError:
            return False
        if parts.scheme not in DEFAULT_PORTS or not host or parts.username is not None or parts.password is not None:
            return False
        default = DEFAULT_PORTS[parts.scheme]
        for scheme, name, allowed_port in self.entries:
            if name == host and scheme in (None, parts.scheme) and (port or default) == (allowed_port or default):
                return True
        return False

    def fetch(self, url):
        """One request without following: (status, location). HEAD, then GET on 405 or 501."""
        parts = urlsplit(url)
        cls = http.client.HTTPSConnection if parts.scheme == 'https' else http.client.HTTPConnection
        target = quote(parts.path or '/', safe=PATH_SAFE) + (f'?{quote(parts.query, safe=QUERY_SAFE)}' if parts.query else '')
        for method in ('HEAD', 'GET'):
            if self.requests and self.delay:
                time.sleep(self.delay)
            self.requests += 1
            conn = cls(parts.hostname, parts.port or DEFAULT_PORTS[parts.scheme], timeout=self.timeout)
            try:
                conn.request(method, target, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
                response = conn.getresponse()
                status, location = response.status, response.getheader('Location')
            finally:
                conn.close()
            if method == 'HEAD' and status in (405, 501):
                continue
            return status, location
        return status, location

    def expected_url(self, dst):
        return dst if urlsplit(dst).scheme else self.base + dst

    def same(self, left, right):
        return norm(left, self.slash) == norm(right, self.slash)

    def check(self, src, dst):
        start = src if urlsplit(src).scheme else self.base + src
        result = {'from': src, 'to': dst, 'ok': False, 'first_status': None, 'hops': [], 'problems': []}
        problems = result['problems']
        if not self.allowed(start):
            problems.append(f'source host not allowed, not requested: {start}')
            return result
        expected = self.expected_url(dst)
        current, visited = start, {norm(start, 'strict')}
        redirects = 0
        refused = False
        while True:
            try:
                status, location = self.fetch(current)
            except (TimeoutError, OSError, http.client.HTTPException, ValueError) as error:
                timed_out = isinstance(error, TimeoutError) or 'timed out' in str(error)
                problems.append(f'timeout requesting {current}' if timed_out else f'request failed for {current}: {error}')
                return result
            result['hops'].append({'url': current, 'status': status, 'location': location})
            if len(result['hops']) == 1:
                result['first_status'] = status
            if not (300 <= status < 400 and location):
                break
            redirects += 1
            try:
                nxt = urljoin(current, location)
                key = norm(nxt, 'strict')
                matches = self.same(nxt, expected)
            except ValueError:
                problems.append(f'malformed Location, not requested: {location!r}')
                return result
            if redirects == 1:
                if status in TEMPORARY:
                    problems.append(f'{status} used for a permanent move; use 301 or 308')
                elif status not in PERMANENT:
                    problems.append(f'unexpected redirect status {status}')
                if not matches:
                    problems.append(f'wrong target: points at {nxt}, expected {expected}')
            if key in visited:
                problems.append(f'loop: {nxt} was already requested')
                return result
            visited.add(key)
            if redirects > MAX_HOPS:
                problems.append(f'more than {MAX_HOPS} hops; stopped at {nxt}')
                return result
            if not self.allowed(nxt):
                problems.append(f'hop to host not allowed, not requested: {nxt} (add --allow-host to verify it)')
                refused = True
                break
            current = nxt
        if redirects == 0:
            problems.append(f'no redirect: first response {result["first_status"]}')
        else:
            if redirects > 1:
                problems.append(f'chain of {redirects} hops; redirect straight to the final target')
            final = result['hops'][-1]
            if not refused and final['status'] != 200:
                if 300 <= final['status'] < 400:
                    problems.append(f'target {final["url"]} returned {final["status"]} with no Location')
                else:
                    problems.append(f'target {final["url"]} returned {final["status"]}')
        result['ok'] = not problems
        return result


def render(report):
    lines = []
    offline = report['offline']
    lines.append(f"rules: {report['rules']}; offline issues: {len(offline)}")
    for issue in offline:
        lines.append(f"  [{issue['check']}] {issue['from']}" + (f" -> {issue['to']}" if issue['to'] else '') +
                     f": {issue['detail']}")
    if report['live'] is not None:
        passed = sum(1 for item in report['live'] if item['ok'])
        lines += ['', f"live: {passed}/{len(report['live'])} pass"]
        for item in report['live']:
            lines.append(f"  {'PASS' if item['ok'] else 'FAIL'} {item['from']} -> {item['to']}")
            for hop in item['hops']:
                lines.append(f"      {hop['status']} {hop['url']}" + (f" -> {hop['location']}" if hop['location'] else ''))
            for problem in item['problems']:
                lines.append(f'      problem: {problem}')
    lines.append('')
    lines.append('result: ' + ('pass' if report['ok'] else 'fail'))
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Check a redirect map offline and optionally against the live old site.')
    parser.add_argument('--map', required=True, help='redirect map: CSV (from,to with a header) or JSON')
    parser.add_argument('--old-pages', help='file with one old path per line; lists those without a rule')
    parser.add_argument('--base', help='live mode: old site origin, such as https://old.example.com')
    parser.add_argument('--allow-host', action='append', default=[], metavar='HOST',
                        help='extra host that live mode may request (the new site); repeatable')
    parser.add_argument('--host', help='offline: origin whose absolute URLs count as plain paths, such as https://example.com')
    parser.add_argument('--slash', choices=('strict', 'loose'), default='loose',
                        help='trailing slash in target comparison (default loose)')
    parser.add_argument('--timeout', type=float, default=10.0, help='seconds per request (default 10)')
    parser.add_argument('--delay', type=float, default=0.0, help='seconds between requests (default 0)')
    parser.add_argument('--json', action='store_true', help='print JSON instead of text')
    args = parser.parse_args(argv)
    try:
        for flag, value in (('--base', args.base), ('--host', args.host)):
            if value:
                parse_origin(value)
                if not value.lower().startswith(('http://', 'https://')):
                    raise Unusable(f'{flag} must start with http:// or https://')
        if args.allow_host and not args.base:
            raise Unusable('--allow-host needs --base')
        if args.timeout <= 0 or args.delay < 0:
            raise Unusable('--timeout must be positive and --delay not negative')
        entries = load_map(args.map)
        old_pages = load_old_pages(args.old_pages) if args.old_pages else None
        hosts = {hostport(urlsplit(value.rstrip('/'))) for value in (args.base, args.host) if value}
        offline, unique = offline_checks(entries, args.slash, hosts, old_pages)
        live = None
        if args.base:
            checker = Checker(args.base, args.allow_host, args.slash, args.timeout, args.delay)
            live = [checker.check(src, dst) for src, dst in unique]
    except Unusable as error:
        print(f'verify_redirects: {error}', file=sys.stderr)
        return 2
    ok = not offline and all(item['ok'] for item in live or [])
    report = {'ok': ok, 'rules': len(entries), 'offline': offline, 'live': live}
    print(json.dumps(report, indent=2) if args.json else render(report))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
