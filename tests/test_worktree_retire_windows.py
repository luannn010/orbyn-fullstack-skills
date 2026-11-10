"""Native retirement contracts on disposable Windows paths; no real workspace cleanup."""
import importlib.util
import os
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1]/'skills/orbyn-worktree/scripts/worktree_retire.py'
spec = importlib.util.spec_from_file_location('windows_retirement_contract', SCRIPT)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class IntegrationContracts(unittest.TestCase):
    def test_recycle_callbacks_veto_permanent_delete_and_missing_destination(self):
        progress = tool.native._DeleteProgress()
        self.assertLess(progress.pre_delete(0), 0)
        self.assertTrue(progress.proof(0, False)['reason'])
        progress = tool.native._DeleteProgress()
        self.assertEqual(progress.pre_delete(0x80), 0)
        self.assertLess(progress.post_delete(0, False), 0)
        self.assertTrue(progress.proof(0, False)['reason'])

    def test_host_management_uses_components_and_windows_separators(self):
        for path in (r'D:\library\.claude\worktrees\slice',
                     'D:/library/.CODEX/WORKTREES/slice', '/library/.claude/worktrees/slice'):
            with self.subTest(path=path):
                ctx = object.__new__(tool.Context)
                ctx.memo = {'judged': {}}
                with mock.patch.object(tool.os.path, 'isdir', return_value=False):
                    result = ctx.judge('repo', {'worktree': path}, False)
                self.assertIn("host-managed; use the host's own cleanup", result['why'])

    def test_windows_usage_distinguishes_busy_unknown_and_idle(self):
        with mock.patch.object(tool.native, 'is_windows', return_value=True):
            for answer, expected in ((None, 'cannot check open files'),
                                     ({'busy.txt'}, 'a process has files open here'), (set(), None)):
                with self.subTest(answer=answer), mock.patch.object(tool.native, 'usage', return_value=answer):
                    self.assertEqual(tool.usage_reason(Path('candidate'), set()), expected)

    def test_windows_recycle_failure_is_a_helper_refusal(self):
        with mock.patch.object(tool.native, 'is_windows', return_value=True), mock.patch.object(
                tool.native, 'recycle', side_effect=tool.native.PlatformRefused('recycling unavailable')):
            with self.assertRaisesRegex(tool.Refused, 'recycling unavailable'):
                tool.trash([Path('candidate')])

    def test_windows_lock_failure_is_a_helper_refusal(self):
        with mock.patch.object(tool.native, 'is_windows', return_value=True), mock.patch.object(
                tool.native, 'cleanup_lock', side_effect=tool.native.PlatformRefused('busy lock')):
            with self.assertRaisesRegex(tool.Refused, 'busy lock'):
                with tool.locked(Path('candidate')):
                    self.fail('entered a refused lock')


@unittest.skipUnless(os.name == 'nt', 'native Windows contracts')
class NativeWindowsContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='orbyn-retire-contract-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def child(self, code, *args, cwd=None):
        process = subprocess.Popen([sys.executable, '-u', '-c', code, *map(str, args)], cwd=cwd,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        self.addCleanup(self.stop, process)
        self.assertEqual(process.stdout.readline().strip(), 'ready')
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.communicate('\n', timeout=15)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream and not stream.closed:
                stream.close()

    def test_idle_unicode_directory_and_file_are_usable(self):
        path = self.root/'design café'
        path.mkdir()
        file = path/'sơ đồ.txt'
        file.write_text('synthetic', encoding='utf-8')
        self.assertEqual(tool.native.usage(path), set())
        self.assertEqual(tool.native.usage(file), set())

    def test_file_open_in_another_process_is_busy_then_released(self):
        path = self.root/'sample.txt'
        path.write_text('synthetic', encoding='utf-8')
        process = self.child('import sys; f=open(sys.argv[1]); print("ready",flush=True); sys.stdin.readline()', path)
        self.assertTrue(tool.native.usage(self.root))
        self.stop(process)
        self.assertEqual(tool.native.usage(self.root), set())

    def test_other_process_working_directory_is_busy(self):
        process = self.child('import sys; print("ready",flush=True); sys.stdin.readline()', cwd=self.root)
        self.assertTrue(tool.native.usage(self.root))
        self.stop(process)
        self.assertEqual(tool.native.usage(self.root), set())

    def test_cleanup_lock_contends_across_processes_and_releases(self):
        code = ('import importlib.util,sys; '
                's=importlib.util.spec_from_file_location("native",sys.argv[1]); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                'ctx=m.cleanup_lock(sys.argv[2]); ctx.__enter__(); '
                'print("ready",flush=True); sys.stdin.readline(); ctx.__exit__(None,None,None)')
        process = self.child(code, SCRIPT.with_name('retirement_platform.py'), self.root)
        with self.assertRaises(tool.native.PlatformRefused):
            with tool.native.cleanup_lock(self.root):
                self.fail('two processes acquired the cleanup lock')
        self.stop(process)
        with tool.native.cleanup_lock(self.root):
            pass

    def test_exception_releases_cleanup_lock(self):
        with self.assertRaisesRegex(RuntimeError, 'synthetic'):
            with tool.native.cleanup_lock(self.root):
                raise RuntimeError('synthetic')
        with tool.native.cleanup_lock(self.root):
            pass

    def test_hardlinked_lock_is_refused(self):
        outside = self.root/'preserve.txt'
        outside.write_text('synthetic', encoding='utf-8')
        os.link(outside, self.root/'.cleanup.lock')
        with self.assertRaises(tool.native.PlatformRefused):
            with tool.native.cleanup_lock(self.root):
                self.fail('hardlinked lock accepted')
        self.assertEqual(outside.read_text(encoding='utf-8'), 'synthetic')

    def test_junction_candidate_is_unknown_and_cannot_be_confined(self):
        source, junction = self.root/'original', self.root/'junction'
        source.mkdir()
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(junction), str(source)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(junction.rmdir)
        self.assertTrue(tool.native.is_reparse(junction))
        self.assertIsNone(tool.native.usage(junction))
        self.assertFalse(tool.confined(junction, self.root))
        with self.assertRaises(tool.native.PlatformRefused):
            with tool.native.cleanup_lock(junction):
                self.fail('junction lock accepted')

    def test_missing_candidate_is_unknown(self):
        self.assertIsNone(tool.native.usage(self.root/'missing'))

    def test_access_failure_is_unknown_not_idle(self):
        path = self.root/'sample.txt'
        path.write_text('synthetic', encoding='utf-8')
        with mock.patch.object(tool.native, '_open', side_effect=PermissionError('synthetic denial')):
            self.assertIsNone(tool.native.usage(path))

    def test_incomplete_recycle_proof_keeps_source_and_does_not_claim_success(self):
        target = self.root/'candidate'
        target.mkdir()
        valid = {'result': 0, 'aborted': False, 'reason': None, 'pre_count': 1, 'post_count': 1}
        for override in ({'aborted': True}, {'result': -1}, {'reason': 'permanent delete vetoed'},
                         {'post_count': 0}, {'post_count': 2}, {}):
            proof = {**valid, **override}
            with self.subTest(override=override), mock.patch.object(tool.native, '_shell_recycle', return_value=proof):
                with self.assertRaises(tool.native.PlatformRefused):
                    tool.native.recycle([target])
                self.assertTrue(target.is_dir())

    def test_unusable_bin_refuses_before_anything_moves(self):
        target = self.root/'candidate'
        target.mkdir()
        with mock.patch.object(tool.native, 'usage', return_value=set()), mock.patch.object(
                tool.native, '_bin_state', side_effect=tool.native.PlatformRefused('no usable bin')), mock.patch.object(
                tool.native, '_shell_recycle') as shell:
            with self.assertRaises(tool.native.PlatformRefused):
                tool.native.recycle([target])
            shell.assert_not_called()
        self.assertTrue(target.is_dir())

    def test_bin_that_does_not_record_the_item_is_not_reported_as_recycled(self):
        target = self.root/'candidate'
        target.mkdir()
        proof = {'result': 0, 'aborted': False, 'reason': None, 'pre_count': 1, 'post_count': 1}
        with mock.patch.object(tool.native, 'usage', return_value=set()), mock.patch.object(
                tool.native, '_bin_state', side_effect=[4, 4]), mock.patch.object(
                tool.native, '_shell_recycle', return_value=proof):
            with self.assertRaises(tool.native.PlatformRefused):
                tool.native.recycle([target])
        self.assertTrue(target.is_dir())

    def test_bin_growth_with_an_absent_source_reports_success(self):
        target = self.root/'candidate'
        target.mkdir()
        (target/'fixture.txt').write_text('synthetic', encoding='utf-8')
        proof = {'result': 0, 'aborted': False, 'reason': None, 'pre_count': 1, 'post_count': 1}
        def moved(path, guard=None):
            if guard:
                guard(path)
            shutil.rmtree(target)
            return proof
        with mock.patch.object(tool.native, 'usage', return_value=set()), mock.patch.object(
                tool.native, '_bin_state', side_effect=[4, 5]), mock.patch.object(
                tool.native, '_shell_recycle', side_effect=moved):
            tool.native.recycle([target])
        self.assertFalse(target.exists())

    def test_candidate_becoming_busy_stops_before_shell(self):
        target = self.root/'candidate'
        target.mkdir()
        with mock.patch.object(tool.native, 'usage', side_effect=[set(), {'newly-open.txt'}]), mock.patch.object(
                tool.native, '_shell_recycle') as shell:
            with self.assertRaises(tool.native.PlatformRefused):
                tool.native.recycle([target])
            shell.assert_not_called()

    def test_unc_path_is_refused_before_shell(self):
        with mock.patch.object(tool.native, '_shell_recycle') as shell:
            with self.assertRaises(tool.native.PlatformRefused):
                tool.native.recycle([r'\\server\share\candidate'])
            shell.assert_not_called()

    def disposable_worktree(self):
        repo, tree = self.root/'repo', self.root/'worktree'
        repo.mkdir()
        def git(*args):
            return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True)
        git('init', '-q', '-b', 'main')
        (repo/'fixture.txt').write_text('synthetic', encoding='utf-8')
        git('add', 'fixture.txt')
        git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.test', 'commit', '-qm', 'fixture')
        git('worktree', 'add', '-qb', 'fixture', str(tree))
        return repo, tree

    def test_partial_shell_result_never_clears_registration(self):
        repo, tree = self.disposable_worktree()
        archive, retained = self.root/'archive', self.root/'retained'
        def incomplete(_path, guard=None):
            if guard:
                guard(_path)
            # Simulate a moved folder with an inconclusive result; retain all data.
            shutil.move(str(tree), str(retained))
            return {'result': 0, 'aborted': True, 'reason': None, 'pre_count': 1, 'post_count': 1}
        with mock.patch.object(tool.native, '_shell_recycle', side_effect=incomplete):
            with self.assertRaises(tool.Refused):
                tool.discard(repo, tree, archive, 'synthetic')
        registered = subprocess.run(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'],
                                    check=True, capture_output=True, text=True).stdout.replace('\\', '/')
        self.assertIn(tree.as_posix(), registered)
        record = json.loads((archive/'worktree/RETIRED.json').read_text(encoding='utf-8'))
        self.assertEqual(record['registration'], 'pending')
        self.assertTrue(record['trashed'].startswith('failed:'))
        self.assertTrue((retained/'fixture.txt').is_file())

    @unittest.skipUnless(os.environ.get('ORBYN_TEST_RECYCLE') == '1', 'opt-in disposable Recycle Bin trial')
    def test_verified_recycle_clears_only_disposable_worktree_registration(self):
        repo, tree = self.disposable_worktree()
        record = tool.discard(repo, tree, self.root/'archive', 'synthetic completed work')
        self.assertEqual(record['registration'], 'cleared')
        self.assertFalse(tree.exists())
        registered = subprocess.run(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'],
                                    check=True, capture_output=True, text=True).stdout.replace('\\', '/')
        self.assertNotIn(tree.as_posix(), registered)
        self.assertIn(repo.as_posix(), registered)
        receipt = json.loads((Path(record['archive'])/'RETIRED.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['registration'], 'cleared')

    @unittest.skipUnless(os.environ.get('ORBYN_TEST_RECYCLE') == '1', 'opt-in disposable Recycle Bin trial')
    def test_html_recycling_preserves_unrequested_connected_assets(self):
        page, assets = self.root/'sample.html', self.root/'sample_files'
        page.write_text('<p>synthetic</p>', encoding='utf-8')
        assets.mkdir()
        (assets/'keep.txt').write_text('must remain', encoding='utf-8')
        tool.native.recycle([page])
        self.assertFalse(page.exists())
        self.assertTrue((assets/'keep.txt').is_file())

    @unittest.skipUnless(os.environ.get('ORBYN_TEST_RECYCLE') == '1', 'opt-in disposable Recycle Bin trial')
    def test_connected_assets_recycling_preserves_unrequested_html(self):
        page, assets = self.root/'sample.html', self.root/'sample_files'
        page.write_text('<p>must remain</p>', encoding='utf-8')
        assets.mkdir()
        (assets/'fixture.txt').write_text('synthetic', encoding='utf-8')
        tool.native.recycle([assets])
        self.assertTrue(page.is_file())
        self.assertFalse(assets.exists())

    @unittest.skipUnless(os.environ.get('ORBYN_TEST_RECYCLE') == '1', 'opt-in disposable Recycle Bin trial')
    def test_replacement_after_usage_is_not_recycled(self):
        target, checked = self.root/'candidate', self.root/'checked-original'
        target.mkdir()
        (target/'original.txt').write_text('synthetic', encoding='utf-8')
        real_usage, calls = tool.native.usage, []
        def replace_after_final_usage(path):
            result = real_usage(path)
            calls.append(path)
            if len(calls) == 2 and result == set():
                target.rename(checked)
                target.mkdir()
                (target/'replacement.txt').write_text('not reviewed', encoding='utf-8')
            return result
        with mock.patch.object(tool.native, 'usage', side_effect=replace_after_final_usage):
            with self.assertRaises(tool.native.PlatformRefused):
                tool.native.recycle([target])
        self.assertTrue((target/'replacement.txt').is_file())
        self.assertTrue((checked/'original.txt').is_file())

    @unittest.skipUnless(os.environ.get('ORBYN_TEST_RECYCLE') == '1', 'opt-in disposable Recycle Bin trial')
    def test_recycles_only_a_disposable_unicode_folder(self):
        target = self.root/'recycle café'
        target.mkdir()
        (target/'fixture.txt').write_text('disposable fixture', encoding='utf-8')
        tool.native.recycle([target])
        self.assertFalse(target.exists())
        self.assertTrue(self.root.is_dir())


if __name__ == '__main__':
    unittest.main()
