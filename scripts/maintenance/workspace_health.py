"""Read-only workspace census. Never cleans, resets, stashes or deletes files."""
import argparse
import collections
import datetime
import json
import pathlib
import subprocess


def git(root, *args):
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', 'replace'))
    return p.stdout.decode('utf-8', 'replace')


def classify(path):
    p = path.lower()
    if '.issue180_test_tmp/' in p or 'docs/knowledge/textbook/' in p or p.startswith('.tmp-') and p.endswith('.py') or p.startswith('.staging-') and p.endswith(('.md', '.py')):
        return 'B historical/unfinished Issue work'
    if 'userdata' in p or 'user.db' in p or '.staging-chrome-' in p:
        return 'G user-owned/local settings'
    if '/bin/' in p or '/obj/' in p or p.startswith(('.staging-', '.backup-')) or p.endswith(('.exe', '.dll', '.pdb')):
        return 'C build/publish/recovery'
    if 'testresults' in p or 'pytest' in p or 'test-output' in p:
        return 'F test output'
    if any(x in p for x in ('cache', 'temp', '.tmp', 'log')):
        return 'E logs/temp/cache'
    if 'runtime' in p or p.endswith('.db'):
        return 'D runtime'
    if p.startswith(('data/', 'docs/issue')) or p.endswith(('.csv', '.xlsx')):
        return 'H research/generated data'
    if p.endswith(('manifest.json', 'checkpoint.json')):
        return 'I generated metadata'
    if p.startswith(('src/', 'scripts/', '.github/')):
        return 'A source/tooling'
    return 'J other/review'


def census(repository, ignored=False):
    blocks = git(repository, 'worktree', 'list', '--porcelain').strip().split('\n\n')
    roots = [b.splitlines()[0][9:] for b in blocks]
    records = []
    for block, root in zip(blocks, roots):
        fields = dict(line.split(' ', 1) if ' ' in line else (line, True) for line in block.splitlines())
        item = {'path': root, 'head': fields.get('HEAD'), 'branch': fields.get('branch'), 'detached': 'detached' in fields}
        try:
            staged = git(root, 'diff', '--cached', '--name-only', '-z').split('\0')[:-1]
            unstaged = git(root, 'diff', '--name-only', '-z').split('\0')[:-1]
            untracked = git(root, 'ls-files', '--others', '--exclude-standard', '-z').split('\0')[:-1]
            nested = [str(pathlib.Path(r).relative_to(root)).replace('\\', '/') + '/' for r in roots if r != root and pathlib.Path(r).is_relative_to(root)]
            nested_entries = [p for p in untracked if any(p.startswith(n) for n in nested)]
            untracked = [p for p in untracked if p not in nested_entries]
            item.update(staged=staged, unstaged=unstaged, untracked=untracked, nested_worktree_entries=nested_entries,
                        classes=dict(collections.Counter(classify(p) for p in staged + unstaged + untracked)))
            item['eol_or_trailing_whitespace_only'] = len(unstaged) - len(git(root, 'diff', '--ignore-space-at-eol', '--name-only', '-z').split('\0')[:-1])
            item['tracking'] = git(root, 'for-each-ref', '--format=%(upstream:short)', fields.get('branch', 'HEAD')).strip() if item['branch'] else ''
            item['ahead_behind'] = git(root, 'rev-list', '--left-right', '--count', 'HEAD...' + item['tracking']).strip() if item['tracking'] else None
            item['unique_vs_main'] = int(git(root, 'rev-list', '--count', 'origin/main..HEAD').strip())
            item['head_date'] = git(root, 'show', '-s', '--format=%cI', 'HEAD').strip()
            if ignored:
                p = subprocess.run(['git', '-C', root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z'], capture_output=True)
                paths = p.stdout.decode('utf-8', 'replace').split('\0')[:-1]
                paths = [p for p in paths if not any(p.startswith(n) for n in nested)]
                item['ignored_count'] = len(paths)
                item['ignored_classes'] = dict(collections.Counter(classify(p) for p in paths))
                item['ignored_top_directories'] = dict(collections.Counter(p.split('/')[0] for p in paths))
                item['inventory_warnings'] = p.stderr.decode('utf-8', 'replace')
            item['clean'] = not (staged or unstaged or untracked)
            item['retirement_candidate'] = item['clean'] and item['unique_vs_main'] == 0
        except (RuntimeError, OSError) as ex:
            item['error'] = str(ex)
        records.append(item)
    return {'schema': 'workspace-health-v1', 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'main': git(repository, 'rev-parse', 'origin/main').strip(), 'worktrees': records,
            'policy': 'Ignored files are protected, not garbage. Retirement candidates require ownership/recovery review; this tool never removes them.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repository', default='.')
    ap.add_argument('--output')
    ap.add_argument('--ignored', action='store_true')
    ap.add_argument('--check', action='store_true', help='Nonzero if main is dirty or >10 historical worktrees remain; does not block a scoped task branch.')
    args = ap.parse_args()
    result = census(args.repository, args.ignored)
    if args.output:
        pathlib.Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for r in result['worktrees']:
        print(f"{r['path']}: {r.get('branch') or 'DETACHED'} staged={len(r.get('staged', []))} unstaged={len(r.get('unstaged', []))} untracked={len(r.get('untracked', []))} ignored={r.get('ignored_count', 'not scanned')} unique={r.get('unique_vs_main', '?')}")
    if args.check:
        raise SystemExit(int(any(r.get('branch') == 'refs/heads/main' and not r.get('clean') for r in result['worktrees']) or len(result['worktrees']) > 10))
