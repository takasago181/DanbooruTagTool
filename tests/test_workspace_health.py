"""Disposable Git fixtures; no access to real worktrees/UserData."""
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / 'scripts/maintenance/workspace_health.py'
spec = importlib.util.spec_from_file_location('workspace_health', TOOL)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class WorkspaceHealthTests(unittest.TestCase):
    def test_census_separates_git_state_and_protected_ignored_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-C', tmp, *args], stderr=subprocess.STDOUT)
            git('init', '-b', 'main')
            git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
            git('config', 'core.autocrlf', 'false')
            (root / '.gitignore').write_text('UserData/\n', encoding='utf-8')
            (root / 'first.cs').write_text('one\n', encoding='utf-8')
            (root / 'second.cs').write_text('two\n', encoding='utf-8')
            git('add', '.'); git('commit', '-m', 'fixture'); git('update-ref', 'refs/remotes/origin/main', 'HEAD')
            (root / 'first.cs').write_text('changed\n', encoding='utf-8'); git('add', 'first.cs')
            (root / 'second.cs').write_text('unfinished\n', encoding='utf-8')
            (root / 'untracked.md').write_text('keep\n', encoding='utf-8')
            (root / 'UserData').mkdir(); protected = root / 'UserData/user.db'; protected.write_bytes(b'keep-protected')
            row = health.census(tmp, ignored=True)['worktrees'][0]
            self.assertEqual(['first.cs'], row['staged']); self.assertEqual(['second.cs'], row['unstaged'])
            self.assertEqual(['untracked.md'], row['untracked']); self.assertEqual(1, row['ignored_count'])
            self.assertFalse(row['clean']); self.assertFalse(row['retirement_candidate'])
            self.assertEqual(b'keep-protected', protected.read_bytes())

    def test_classification_does_not_treat_research_or_userdata_as_disposable(self):
        self.assertTrue(health.classify('.issue180_test_tmp/build_wave.py').startswith('B'))
        self.assertTrue(health.classify('UserData/user.db').startswith('G'))
        self.assertTrue(health.classify('src/project/bin/app.dll').startswith('C'))

    @unittest.skipUnless(__import__('os').name == 'nt', 'Windows lifecycle contract')
    def test_start_applies_lf_before_checkout_from_legacy_autocrlf_owner(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp); repo = base / 'repo'; repo.mkdir(); remote = base / 'origin.git'
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.STDOUT)
            git('init', '-b', 'main'); git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
            git('config', 'core.autocrlf', 'false'); (repo / 'source.txt').write_bytes(b'first\nsecond\n')
            git('add', '.'); git('commit', '-m', 'fixture'); subprocess.check_output(['git', 'init', '--bare', str(remote)], stderr=subprocess.STDOUT)
            git('remote', 'add', 'origin', str(remote)); git('push', '-u', 'origin', 'main'); git('config', 'extensions.worktreeConfig', 'true'); git('config', '--worktree', 'core.autocrlf', 'true')
            task_root = base / 'tasks'; task_root.mkdir()
            (repo / '.git/workspace-layout.json').write_text(json.dumps({'main_entry':str(repo),'task_root':str(task_root)}),encoding='utf-8')
            script = TOOL.with_name('workspace_task.ps1')
            subprocess.check_output([shutil.which('pwsh') or 'powershell', '-NoProfile','-File',str(script),'-Action','Start','-Issue','999','-RepositoryRoot',str(repo)],stderr=subprocess.STDOUT)
            checkout=task_root/'issue-999'; self.assertEqual(b'first\nsecond\n',(checkout/'source.txt').read_bytes())
            self.assertEqual(b'',subprocess.check_output(['git','-C',str(checkout),'status','--porcelain']))


if __name__ == '__main__':
    unittest.main()
