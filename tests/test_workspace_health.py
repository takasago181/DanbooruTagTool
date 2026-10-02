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


if __name__ == '__main__':
    unittest.main()
