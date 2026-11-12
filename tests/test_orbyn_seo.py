"""orbyn-seo helpers: link graph report values, redirect map checks offline and against a local server."""
import importlib.util
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import unittest.mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/orbyn-seo/scripts'
LINK_GRAPH = SCRIPTS / 'link_graph.py'
REDIRECTS = SCRIPTS / 'verify_redirects.py'


def load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script, *args):
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=60)
    return result.returncode, result.stdout, result.stderr


def page(*links):
    return '<html><body>' + ''.join(links) + '</body></html>'


def a(href, extra=''):
    return f'<a href="{href}" {extra}>x</a>'


class LinkGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        files = {
            'index.html': page(a('/about'), a('/blog/'), a('https://example.com/pricing.html'),
                               a('https://other.test/x'), a('mailto:a@b.test'), a('tel:+1'), a('javascript:void(0)'),
                               a('/missing')),
            'about.html': page(a('/'), a('/blog/post-1/?ref=nav#top'), a('/pricing', 'rel="nofollow noopener"')),
            'pricing.html': page(a('/')),
            'blog/index.html': page(a('post-1/'), a('../about#team'), a('/blog/post-1.html')),
            'blog/post-1/index.html': page(a('../'), a('deep/'), a('/img/logo.png'), a('#top'), a('./nowhere')),
            'blog/post-1/deep/index.html': page(a('/'), a('/pricing')),
            'blog/post-1/deep/money/index.html': page(a('/')),
            'orphan.html': page(a('/')),
            'img/logo.png': 'png',
        }
        for name, body in files.items():
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        self.report = self.graph('--base-url', 'https://example.com', '--money', '/blog/post-1/deep/',
                                 '--money', '/pricing', '--money', '/nope')

    def graph(self, *extra):
        code, out, err = run(LINK_GRAPH, '--site', str(self.site), '--json', *extra)
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_counts_and_inbound(self):
        report = self.report
        self.assertEqual(report['pages'], 8)
        self.assertEqual(report['links'], 19)
        self.assertEqual(report['inbound'], {
            '/': 5, '/about': 2, '/blog/': 2, '/blog/post-1/': 2, '/blog/post-1/deep/': 1,
            '/blog/post-1/deep/money/': 0, '/orphan': 0, '/pricing': 2})

    def test_orphans_weak_and_broken(self):
        report = self.report
        self.assertEqual(report['orphans'], ['/blog/post-1/deep/money/', '/orphan'])
        self.assertEqual(report['weak'], ['/blog/post-1/deep/'])
        self.assertEqual(report['broken'], [
            {'source': '/', 'href': '/missing'}, {'source': '/blog/post-1/', 'href': './nowhere'}])

    def test_depth_and_unreachable(self):
        report = self.report
        self.assertEqual(report['depth'], {'/': 0, '/about': 1, '/blog/': 1, '/blog/post-1/': 2,
                                           '/blog/post-1/deep/': 3, '/pricing': 1})
        self.assertEqual(report['unreachable'], ['/blog/post-1/deep/money/', '/orphan'])

    def test_nofollow_passes_no_inbound_and_money_pages(self):
        report = self.report
        self.assertEqual(report['nofollow_inbound'], {'/pricing': 1})
        deep, pricing, nope = report['money']
        self.assertEqual(deep, {'path': '/blog/post-1/deep/', 'found': True, 'inbound': 1, 'depth': 3,
                                'top_linking': ['/blog/post-1/']})
        self.assertEqual(pricing['top_linking'], ['/', '/blog/post-1/deep/'])
        self.assertEqual((pricing['inbound'], pricing['depth']), (2, 1))
        self.assertEqual(nope, {'path': '/nope', 'found': False})

    def test_without_base_url_absolute_links_are_external(self):
        report = self.graph()
        self.assertEqual(report['inbound']['/pricing'], 1)  # only /blog/post-1/deep/ now; the absolute link is skipped

    def test_min_inbound_changes_weak_list(self):
        report = self.graph('--base-url', 'https://example.com', '--min-inbound', '3')
        self.assertEqual(report['weak'], ['/about', '/blog/', '/blog/post-1/', '/blog/post-1/deep/', '/pricing'])

    def test_text_output(self):
        code, out, _ = run(LINK_GRAPH, '--site', str(self.site), '--base-url', 'https://example.com', '--money', '/pricing')
        self.assertEqual(code, 0)
        self.assertIn('pages: 8', out)
        self.assertIn('/ -> /missing', out)
        self.assertIn('/pricing: inbound 2, depth 1, top linking: /, /blog/post-1/deep/', out)

    def test_bad_input_exits_two(self):
        self.assertEqual(run(LINK_GRAPH, '--site', str(self.site / 'nope'))[0], 2)
        self.assertEqual(run(LINK_GRAPH, '--site', str(self.site), '--home', '/unknown')[0], 2)
        empty = self.site / 'empty'
        empty.mkdir()
        self.assertEqual(run(LINK_GRAPH, '--site', str(empty))[0], 2)

    def test_malformed_href_is_broken_and_run_continues(self):
        (self.site / 'bad.html').write_text(page(a('http://[x'), a('/about')))
        report = self.graph('--base-url', 'https://example.com')
        self.assertIn({'source': '/bad', 'href': 'http://[x'}, report['broken'])
        self.assertEqual(report['inbound']['/about'], 3)

    @unittest.skipUnless(hasattr(os, 'symlink'), 'needs symlinks')
    def test_symlinked_page_outside_site_is_skipped(self):
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / 'secret.html'
            secret.write_text(page(a('/pricing')))
            try:
                os.symlink(secret, self.site / 'leak.html')
            except OSError:
                self.skipTest('symlinks not permitted')
            report = self.graph('--base-url', 'https://example.com')
            self.assertEqual(report['skipped'], [{'file': '/leak.html', 'reason': 'resolves outside --site (symlink)'}])
            self.assertNotIn('/leak', report['inbound'])
            self.assertEqual(report['inbound']['/pricing'], 2)
            code, out, _ = run(LINK_GRAPH, '--site', str(self.site))
            self.assertIn('skipped files: 1', out)
            self.assertIn('/leak.html: resolves outside --site (symlink)', out)

    def test_oversized_file_is_skipped(self):
        module = load(LINK_GRAPH)
        module.MAX_BYTES = 1000
        (self.site / 'huge.html').write_text(page(a('/about')) + '<!--' + 'x' * 3000 + '-->')
        report = module.analyse(self.site.resolve(), None, '/', [], 2)
        self.assertEqual(report['skipped'], [{'file': '/huge.html', 'reason': 'larger than 20 MB'}])
        self.assertNotIn('/huge', report['inbound'])
        self.assertEqual(report['inbound']['/about'], 2)
        (self.site / 'links-big.html').write_text(page(a('/huge.html'), a('/huge')))
        report = module.analyse(self.site.resolve(), None, '/', [], 2)
        broken = {(b['source'], b['href']) for b in report['broken']} if report['broken'] and isinstance(report['broken'][0], dict) else set(map(tuple, report['broken']))
        self.assertTrue({('/links-big', '/huge.html'), ('/links-big', '/huge')} <= broken, report['broken'])

    def test_read_only(self):
        before = sorted(p.relative_to(self.site).as_posix() for p in self.site.rglob('*'))
        run(LINK_GRAPH, '--site', str(self.site))
        self.assertEqual(before, sorted(p.relative_to(self.site).as_posix() for p in self.site.rglob('*')))


class OfflineRedirectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def write(self, name, text):
        path = self.dir / name
        path.write_text(text)
        return str(path)

    def check(self, map_path, *extra):
        code, out, err = run(REDIRECTS, '--map', map_path, '--json', *extra)
        return code, json.loads(out) if out.strip() else None, err

    def issues(self, report, check):
        return [i for i in report['offline'] if i['check'] == check]

    def test_clean_map_passes(self):
        code, report, _ = self.check(self.write('m.csv', 'from,to\n/a,/b\n/c,/d\n'))
        self.assertEqual(code, 0)
        self.assertEqual((report['ok'], report['rules'], report['offline'], report['live']), (True, 2, [], None))

    def test_duplicates_self_and_chain(self):
        csv_text = 'from,to\n/a,/b\n/a,/z\n/b,/c\n/s,/s/\n/x,/y\n/x,/y\n'
        code, report, _ = self.check(self.write('m.csv', csv_text))
        self.assertEqual(code, 1)
        dupes = self.issues(report, 'duplicate')
        self.assertEqual([d['from'] for d in dupes], ['/a', '/x'])
        self.assertIn('conflicting targets', dupes[0]['detail'])
        self.assertIn('same target repeated', dupes[1]['detail'])
        self.assertEqual([i['from'] for i in self.issues(report, 'self')], ['/s'])
        chain = self.issues(report, 'chain')
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0]['from'], '/a')
        self.assertIn('/a -> /b -> /c', chain[0]['detail'])
        self.assertIn('redirect /a straight to /c', chain[0]['detail'])

    def test_strict_slash_distinguishes_self(self):
        _, report, _ = self.check(self.write('m.csv', 'from,to\n/s,/s/\n'), '--slash', 'strict')
        self.assertEqual(self.issues(report, 'self'), [])

    def test_loop_reported_once(self):
        code, report, _ = self.check(self.write('m.json', json.dumps({'/a': '/b', '/b': '/c', '/c': '/a'})))
        self.assertEqual(code, 1)
        loops = self.issues(report, 'loop')
        self.assertEqual(len(loops), 1)
        self.assertIn('/a -> /b -> /c -> /a', loops[0]['detail'])
        self.assertEqual(self.issues(report, 'chain'), [])

    def test_missing_old_pages_and_comments(self):
        old = self.write('old.txt', '# old urls\n/a\n\n/gone\n/b/\n')
        _, report, _ = self.check(self.write('m.csv', 'from,to\n/a,/n\n/b,/m\n'), '--old-pages', old)
        self.assertEqual([i['from'] for i in self.issues(report, 'missing')], ['/gone'])

    def test_json_list_and_malformed(self):
        data = [{'from': '/a', 'to': '/b'}, {'from': 'a', 'to': '/b'}, {'from': '/c'}, 'junk']
        code, report, _ = self.check(self.write('m.json', json.dumps(data)))
        self.assertEqual(code, 1)
        self.assertEqual(report['rules'], 4)
        self.assertEqual(len(self.issues(report, 'malformed')), 3)

    def test_absolute_urls_and_header_case(self):
        text = 'From,To\nhttps://old.test/a,https://new.test/a\n'
        code, report, _ = self.check(self.write('m.csv', text))
        self.assertEqual((code, report['offline']), (0, []))

    def test_malformed_url_entries_are_flagged_not_crashes(self):
        code, report, err = self.check(self.write('m.csv', 'from,to\n/a,http://[x\nhttp://[y/z,/b\n/ok,/fine\n'),
                                       '--old-pages', self.write('old.txt', 'http://[q\n/ok\n'))
        self.assertEqual(code, 1, err)
        self.assertEqual(len(self.issues(report, 'malformed')), 3)
        self.assertEqual(self.issues(report, 'missing'), [])

    def test_host_flag_treats_origin_urls_as_paths(self):
        text = 'from,to\nhttps://Example.com:443/a,https://example.com/b\n/b,/c\nhttps://example.com/s,/s\n'
        _, plain, _ = self.check(self.write('m.csv', text))
        self.assertEqual(plain['offline'], [])  # origin URLs and paths are different forms without --host
        code, report, _ = self.check(self.write('m.csv', text), '--host', 'https://example.com')
        self.assertEqual(code, 1)
        chain = self.issues(report, 'chain')
        self.assertEqual([c['from'] for c in chain], ['https://Example.com:443/a'])
        self.assertIn('straight to /c', chain[0]['detail'])
        self.assertEqual([i['to'] for i in self.issues(report, 'self')], ['/s'])
        self.assertEqual(self.check(self.write('m.csv', text), '--host', 'example.com')[0], 2)

    def test_bad_input_exits_two(self):
        self.assertEqual(self.check(str(self.dir / 'absent.csv'))[0], 2)
        self.assertEqual(self.check(self.write('bad.json', '{oops'))[0], 2)
        self.assertEqual(self.check(self.write('scalar.json', '3'))[0], 2)
        self.assertEqual(self.check(self.write('nohead.csv', 'a,b\n/x,/y\n'))[0], 2)
        good = self.write('m.csv', 'from,to\n/a,/b\n')
        self.assertEqual(self.check(good, '--base', 'ftp://x')[0], 2)
        self.assertEqual(self.check(good, '--base', 'http://user:pw@old.test')[0], 2)
        self.assertEqual(self.check(good, '--base', 'http://[bad')[0], 2)
        self.assertEqual(self.check(good, '--base', 'http://old.test', '--allow-host', 'u:p@new.test')[0], 2)
        self.assertEqual(self.check(good, '--allow-host', 'x.test')[0], 2)
        self.assertEqual(self.check(good, '--old-pages', str(self.dir / 'nope.txt'))[0], 2)
        self.assertEqual(run(REDIRECTS)[0], 2)


class Handler(BaseHTTPRequestHandler):
    release = None

    def log_message(self, *args):
        pass

    def reply(self, status, location=None):
        self.send_response(status)
        if location:
            self.send_header('Location', location)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def handle_any(self):
        path = self.path.split('?')[0]
        port = self.server.server_address[1]
        redirects = {
            '/p301': (301, '/new'), '/p308': (308, '/new'), '/t302': (302, '/new'), '/t307': (307, '/new'),
            '/chain': (301, '/hop'), '/hop': (301, '/new'), '/loopa': (301, '/loopb'), '/loopb': (301, '/loopa'),
            '/gone': (301, '/missing'), '/boom': (301, '/err'), '/wrong': (301, '/other'),
            '/headless': (301, '/nohead'), '/slashy': (301, '/new/'), '/offsite': (301, 'http://example.invalid/x'),
            '/xhost': (301, f'http://localhost:{port}/new'), '/slow': (301, '/slowtarget'),
            '/upper': (301, f'http://LOCALHOST:{port}/new'), '/userinfo': (301, f'http://u:pw@localhost:{port}/new'),
            '/file': (301, 'file:///etc/hosts'), '/proto': (301, '//evil.invalid/x'),
            '/nonascii': (301, '/caf\u00e9'), '/nolocation': (302, None), '/p3xx': (301, '/nolocation'),
            '/badloc': (301, 'http://[bad/x'), '/v6': (301, 'http://[::1]:1/new'),
        }
        if path in redirects:
            return self.reply(*redirects[path])
        if path in ('/new', '/new/', '/other'):
            return self.reply(200)
        if path == '/caf%C3%A9':
            return self.reply(200)
        if path == '/nohead':
            return self.reply(405) if self.command == 'HEAD' else self.reply(200)
        if path == '/slowtarget':
            self.release.wait(5)
            return
        if path == '/err':
            return self.reply(500)
        if path == '/plain':
            return self.reply(200)
        return self.reply(404)

    do_HEAD = do_GET = handle_any


class LiveRedirectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Handler.release = threading.Event()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_address[1]}'

    @classmethod
    def tearDownClass(cls):
        Handler.release.set()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(5)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def live(self, rules, *extra):
        path = Path(self.temp.name) / 'map.json'
        path.write_text(json.dumps([{'from': src, 'to': dst} for src, dst in rules]))
        code, out, err = run(REDIRECTS, '--map', str(path), '--base', self.base, '--json', *extra)
        self.assertIn(code, (0, 1), err)
        report = json.loads(out)
        return code, {item['from']: item for item in report['live']}

    def test_passing_rules_exit_zero(self):
        code, results = self.live([('/p301', '/new'), ('/p308', '/new'), ('/headless', '/nohead'), ('/slashy', '/new')])
        self.assertEqual(code, 0, results)
        self.assertEqual(results['/p301']['first_status'], 301)
        self.assertEqual(results['/p308']['first_status'], 308)
        self.assertEqual([h['status'] for h in results['/headless']['hops']], [301, 200])

    def test_failures_exit_one(self):
        rules = [('/t302', '/new'), ('/t307', '/new'), ('/chain', '/new'), ('/loopa', '/loopb'), ('/gone', '/missing'),
                 ('/boom', '/err'), ('/wrong', '/new'), ('/plain', '/new'), ('/nothere', '/new')]
        code, results = self.live(rules)
        self.assertEqual(code, 1)
        problems = {src: ' | '.join(item['problems']) for src, item in results.items()}
        self.assertFalse(any(item['ok'] for item in results.values()))
        self.assertIn('302 used for a permanent move', problems['/t302'])
        self.assertIn('307 used for a permanent move', problems['/t307'])
        self.assertIn('wrong target', problems['/chain'])
        self.assertIn('chain of 2 hops', problems['/chain'])
        self.assertIn('loop', problems['/loopa'])
        self.assertIn('returned 404', problems['/gone'])
        self.assertIn('returned 500', problems['/boom'])
        self.assertIn('wrong target', problems['/wrong'])
        self.assertIn('no redirect: first response 200', problems['/plain'])
        self.assertIn('no redirect: first response 404', problems['/nothere'])

    def test_chain_with_matching_first_target_is_flagged(self):
        code, results = self.live([('/chain', '/hop')])
        self.assertEqual(code, 1)
        self.assertEqual(results['/chain']['problems'], ['chain of 2 hops; redirect straight to the final target'])

    def test_strict_slash(self):
        self.assertEqual(self.live([('/slashy', '/new')], '--slash', 'strict')[0], 1)
        self.assertEqual(self.live([('/slashy', '/new/')], '--slash', 'strict')[0], 0)

    def test_disallowed_host_is_reported_not_fetched(self):
        code, results = self.live([('/offsite', 'http://example.invalid/x')])
        self.assertEqual(code, 1)
        item = results['/offsite']
        self.assertEqual([h['status'] for h in item['hops']], [301])
        self.assertTrue(any('not requested' in p and 'example.invalid' in p for p in item['problems']), item)

    def test_allowed_host_is_followed(self):
        target = f'http://localhost:{self.server.server_address[1]}/new'
        self.assertEqual(self.live([('/xhost', target)])[0], 1)
        self.assertEqual(self.live([('/xhost', target)], '--allow-host', 'localhost')[0], 1)  # bare host: port 80 only
        code, results = self.live([('/xhost', target)], '--allow-host', f'localhost:{self.server.server_address[1]}')
        self.assertEqual(code, 0, results)

    def test_uppercase_host_matches(self):
        port = self.server.server_address[1]
        code, results = self.live([('/upper', f'http://localhost:{port}/new')], '--allow-host', f'localhost:{port}')
        self.assertEqual(code, 0, results)

    def refused(self, route, target):
        code, results = self.live([(route, target)], '--allow-host', 'localhost', '--allow-host', 'example.invalid')
        self.assertEqual(code, 1)
        problems = results[route]['problems']
        self.assertTrue(any('not requested' in p for p in problems), problems)
        self.assertEqual(len(results[route]['hops']), 1)

    def test_userinfo_location_is_never_requested(self):
        port = self.server.server_address[1]
        self.refused('/userinfo', f'http://localhost:{port}/new')

    def test_file_and_protocol_relative_locations_are_not_requested(self):
        self.refused('/file', '/new')
        self.refused('/proto', 'http://evil.invalid/x')

    def test_non_ascii_location_is_encoded(self):
        code, results = self.live([('/nonascii', '/caf\u00e9')])
        self.assertEqual(code, 0, results)
        self.assertEqual(results['/nonascii']['hops'][-1]['status'], 200)

    def test_malformed_location_is_a_problem(self):
        code, results = self.live([('/badloc', '/new')])
        self.assertEqual(code, 1)
        self.assertTrue(any('malformed Location' in p for p in results['/badloc']['problems']), results)

    def test_final_3xx_without_location_fails(self):
        code, results = self.live([('/p3xx', '/nolocation')])
        self.assertEqual(code, 1)
        self.assertTrue(any('with no Location' in p for p in results['/p3xx']['problems']), results)

    def test_allowed_rules_for_ports_ipv6_and_userinfo(self):
        checker = load(REDIRECTS).Checker('http://old.test', ['new.test', 'https://secure.test', 'other.test:8080',
                                                                  '[::1]:9'], 'loose', 1, 0)
        for url in ('http://old.test/x', 'http://OLD.test:80/x', 'https://old.test/x', 'http://new.test:80/x',
                    'https://NEW.test:443/x', 'https://secure.test/x', 'http://other.test:8080/x', 'http://[::1]:9/x'):
            self.assertTrue(checker.allowed(url), url)
        for url in ('http://old.test:8080/x', 'http://new.test:8080/x', 'http://other.test/x', 'http://secure.test/x',
                    'http://[::1]/x', 'http://[::2]:9/x', 'http://u:p@old.test/x', 'http://u@new.test/x',
                    'file:///etc/hosts', 'http://[bad/x', 'http:///x'):
            self.assertFalse(checker.allowed(url), url)

    def test_ipv6_without_port_connects_to_the_default_port(self):
        module = load(REDIRECTS)
        seen = []

        class Stop(Exception):
            pass

        class Fake:
            def __init__(self, host, port=None, timeout=None):
                seen.append((host, port))
                raise Stop

        checker = module.Checker('http://[::1]', [], 'loose', 1, 0)
        with unittest.mock.patch.object(module.http.client, 'HTTPConnection', Fake):
            with self.assertRaises(Stop):
                checker.fetch('http://[::1]/x')
        self.assertEqual(seen, [('::1', 80)])

    def test_norm_drops_default_ports_and_case(self):
        norm = load(REDIRECTS).norm
        self.assertEqual(norm('HTTP://Example.COM:80/a/', 'loose'), norm('https://example.com:443/a', 'loose'))
        self.assertNotEqual(norm('http://example.com:8080/a', 'loose'), norm('http://example.com/a', 'loose'))
        self.assertEqual(norm('http://[::1]:80/a', 'strict')[0], '[::1]')

    def test_timeout_is_flagged(self):
        code, results = self.live([('/slow', '/slowtarget')], '--timeout', '0.3')
        self.assertEqual(code, 1)
        self.assertTrue(any('timeout' in p for p in results['/slow']['problems']), results)

    def test_text_output(self):
        path = Path(self.temp.name) / 'map.csv'
        path.write_text('from,to\n/p301,/new\n/t302,/new\n')
        code, out, _ = run(REDIRECTS, '--map', str(path), '--base', self.base)
        self.assertEqual(code, 1)
        self.assertIn('PASS /p301 -> /new', out)
        self.assertIn('FAIL /t302 -> /new', out)
        self.assertIn('result: fail', out)


if __name__ == '__main__':
    unittest.main()
