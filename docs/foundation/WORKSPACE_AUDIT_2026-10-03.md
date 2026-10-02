# Workspace recovery and recurrence audit — 2026-10-03

## Findings and exact scope

The persistent default entry was `C:/Codex/DanbooruTagTool`, still on
`codex/issue91-structural-hardening`, HEAD
`1a8c6898cb5a59be8779a85f4e086d94d7a6cc9e` (2026-09-16).
This branch has no commits unique to live main. It was a legacy checkout, not the
current main entry. The session kept entering it because the saved environment
cwd points there; creating a fresh task worktree never corrected that entry.

Initial porcelain reported **2,051 unstaged files / 0 staged**. Git's
`--ignore-space-at-eol` diff was empty. Raw HEAD-vs-file byte inspection of **all
tracked files** found **2,403 LF-equivalent differences, all exclusively CRLF/LF**.
The difference in counts reflects Git's stat/index/normalization cache, not extra
unsaved semantic changes. The read-only `-c core.autocrlf=true` diagnostic refreshed
that cache, so the initial pre-repair machine census already showed zero tracked
status changes. We therefore retained raw-byte evidence separately.

The repository had `core.autocrlf=false`, while Windows' system setting was true;
checkout bytes still had CRLF. There is no evidence identifying the exact process
that last changed the setting, and no claim that each run rewrote all 2,051 files.
The recurring problem was the mismatch plus an unchanged legacy default entry.

Root `ls-files --others --exclude-standard` initially returned **13,784 entries**,
including **23 nested-worktree directory entries**. Excluding registered child
checkouts leaves **13,761 actual local artifact/settings files**. They include:
- browser validation profiles/local settings: **11,702**;
- publish candidates/backups/recovery/validation outputs: **2,012**;
- logs/temp/cache: **34**;
- benchmark/research CSV: **5**;
- screenshots/other reviewed local files: **8**.

These are initial dominant-category counts; checkpoint notes/helpers inside staging
are more precisely B/I subtypes, retained rather than blindly treated as waste.
There were **43 registered worktrees**, many for closed Issues. Before exclusions,
ignored inventory found at least **38,263 files** across worktrees; some old backup
folders refused enumeration, so this is explicitly a lower bound.

Two other checkouts contain real uncommitted work:
- `C:/Users/takas/.codex/worktrees/8008/DanbooruTagTool`: **65** Issue180
  scripts/research/checkpoints under `.issue180_test_tmp`;
- `C:/Users/takas/.codex/worktrees/92f0/DanbooruTagTool`: **5** KNOWLEDGE #44
  textbook source/audit files (active long-term lane).

## Classification and disposition

| Class | Evidence | Decision |
|---|---|---|
| A source changes | root scripts/workflows differ only by EOL; no genuine unsaved production implementation | preserve bytes; do not commit EOL noise |
| B Issue work | 65 research files + 5 knowledge files, staging helper/checkpoint drafts | preserve; owner decides meaningful commits; no automatic commit/import into Foundation |
| C build/publish | candidates/backups/staging, ignored bin/obj | retain recovery copies; future publish uses TEMP/outside checkout; ignore known output families |
| D runtime | catalogs/candidate runtime folders | preserve; production runtime already lives at `C:/Codex/DanbooruTagTool-App` |
| E logs/temp/cache | UIA/Forge logs, validation browser caches | retain, ignore reviewed local-output names; do not publish |
| F tests | test/temp outputs, benchmarks | ignored/external result directories; no semantic authority promotion |
| G UserData/settings | browser profiles, production user.db/Library/LoRA DBs | protected; never cleanup/commit; production stores remain separate |
| H research/data | source shards, generated CSV, protected source/derived datasets | tracked accepted data stays tracked; local research retained; no Batch B evidence move |
| I metadata | manifests/checkpoints/bootstrap | accepted metadata remains tracked; local candidates retained/ignored |
| J other | screenshots/helper scratch | preserve; exact reviewed local prefix exclusions; no broad file deletion |

Old `scripts/issue70/build_compact_shards.py` writes tracked source shards and
metadata under docs. Such scripts are capable of generating tracked deltas;
**we did not run them**, and all observed root deltas are EOL-only. They are
historical tools, not a normal startup/build path. The two live Issue70 workflows
that can push main are separately disabled/archived in P0. Current Maintenance
compilation writes only a caller-selected fresh output, never source authority.

The current publish pipeline already uses TEMP and an outside-checkout output.
Default .NET bin/obj and some legacy tests stay ignored in the task checkout for
compatibility with source-relative regression fixtures. This is safer than moving
all test paths in Foundation; they do not dirty source control, and the Finish
tool refuses to remove any worktree containing ignored files. New publish,
validation, browser and test result output belongs in TEMP/configured artifact root.

## Recovery and changes made

No reset, clean, stash/drop, source overwrite, UserData removal, or research import.
Recovery files (local/protected, deliberately not uploaded):
- `.local/root-eol-recovery.zip`: 2,403 exact checkout bytes, 6,493,772 bytes,
  SHA256 `255aa068f32c80d79e17090cae97a4ea203b95771661184238ce9c5537f4a902`.
- `.local/uncommitted-research-recovery.zip`: 70 files, 474,364 bytes,
  SHA256 `281c9235803603d3a505e610c4ed9eefef385354e9cd157c098bf9b4f874aefb`.
- local raw-byte/research/inventory manifests remain beside those ZIPs.
- Post-repair verification: original 2,403 files and all 70 research files still
  match their captured bytes/hashes.

Local Git metadata changes:
- enabled worktree-specific config; **only the legacy root** gets
  `core.autocrlf=true`; task/build checkouts retain false for authority hash safety;
- common `.git/info/exclude` now excludes reviewed legacy worktree/staging/backup/
  browser/temp/log/screenshot families; no file is deleted;
- local `workspace-layout.json` records clean main/task/artifact/legacy entries;
- advanced local `main` from an ancestor (0 unique commits) to fetched main and
  created **`C:/Codex/DanbooruTagTool/.worktrees/main`**. Main is clean.

Versioned fixes:
- `.gitignore`: reviewed generated families, bin/obj/TestResults, local recovery;
- `.gitattributes`: explicit LF for C#/PowerShell/Python/source control text;
- `workspace_health.py`: read-only all-worktree machine census, ahead/behind,
  meaningful status/ignored classifications, duplicate nested-entry exclusion;
- `workspace_task.ps1`: clean-main fast-forward and one `dev/issue-N` primary
  checkout on Start; Finish refuses dirty/untracked/ignored/unmerged/detached or
  wrong-Issue paths and never force-removes/stashes/resets.

Only two worktrees were removed: `.worktree-issue225-stop` and
`.worktree-issue226-production-record`. Both had **zero staged/unstaged/untracked/
ignored files** and HEADs merged into live main. Branches/Git history were retained.
No other checkout or accepted/protected asset was moved/deleted. App-managed
worktrees were not touched; unrelated unique history and protected ignored files
are retained. Broad branch/evidence cleanup remains Batch B, not started here.

## Operating entry and lightweight diagnosis

Use the clean main entry for the saved project/new work; the old root is a
preserved compatibility/data/recovery entry, not a task source baseline. Existing
chat cwd cannot be remotely repointed by the available app tools. Even if a chat
starts in that root, it now reports clean and the layout points to current main.
Merge this PR before using the versioned helper from main; meanwhile it is present
in the Foundation task checkout.

```powershell
python -B scripts/maintenance/workspace_health.py --repository C:/Codex/DanbooruTagTool --ignored --output "$env:TEMP/DTT-workspaces.json"
./scripts/maintenance/workspace_task.ps1 -Action Start -Issue 999
# commit / PR / merge before retirement
./scripts/maintenance/workspace_task.ps1 -Action Finish -Issue 999
```

`--check` is an advisory nonzero result while >10 historical worktrees remain or
main is dirty. It never mutates anything. Remaining 42 checkouts/13 detached HEADs
are visible in the census; safe retirement still requires owner/recovery review.
The retained two uncommitted research/knowledge worktrees are explicitly separate
from Foundation. Source/main are clean after checkpoints, so P0 + Batch A may
continue safely. Recurrence is reduced by configuration repair, explicit output
families, a clean main entry and lifecycle guards, not by hiding meaningful source
changes or deleting historical work.

## All retained worktrees (post-repair inventory)

Foundation status below was captured during implementation; its changes are
committed for PR at the final checkpoint. Other worktree statuses are read-only
snapshots; concurrent owner work may change them.

| path | branch / HEAD | tracking / ahead-behind | staged / unstaged / untracked | ignored | disposition |
|---|---|---|---|---|---|
| `C:/Codex/DanbooruTagTool` | `codex/issue91-structural-hardening` / `1a8c6898cb5a` | `origin/codex/issue91-structural-hardening` / `0	0` | 0 / 0 / 0 | 27228 | legacy entry preserved, clean after configuration repair; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue117-helper` | `ops/issue117-local-runtime-preflight` / `d2228ef6fe0a` | `origin/ops/issue117-local-runtime-preflight` / `0	0` | 0 / 0 / 0 | 0 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue132-final-integrator` | `audit/issue132-final-reconcile-1` / `b387d5a669bc` | `none` / `n/a` | 0 / 0 / 0 | 3 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue132-final-reconcile-0` | `audit/issue132-final-reconcile-0` / `f3f7b14b76a1` | `none` / `n/a` | 0 / 0 / 0 | 0 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue132-final-reconcile-2` | `audit/issue132-final-finalizer` / `c1014b31cbfc` | `none` / `n/a` | 0 / 0 / 0 | 2 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue132-final-reconcile-3` | `audit/issue132-final-reconcile-3` / `53eaaaf7c3c8` | `none` / `n/a` | 0 / 0 / 0 | 2 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue175-reference-only` | `detached` / `45919734f6b0` | `none` / `n/a` | 0 / 0 / 0 | 854 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue180-final` | `detached` / `180d26b52f91` | `none` / `n/a` | 0 / 0 / 0 | 818 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue180-single-home-pilot` | `research/issue180-legacy-salvage` / `55a86ad4828a` | `origin/research/issue180-legacy-salvage` / `0	0` | 0 / 0 / 0 | 621 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue223` | `dev/issue223-browse-groups` / `e58824c02123` | `origin/dev/issue223-browse-groups` / `0	0` | 0 / 0 / 0 | 882 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue223-baseline` | `detached` / `84a4ac467cc5` | `none` / `n/a` | 0 / 0 / 0 | 814 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue223-production` | `docs/issue223-production-closeout` / `a487eb0c3fc0` | `origin/docs/issue223-production-closeout` / `0	0` | 0 / 0 / 0 | 814 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue226` | `dev/issue226-generation-image-library` / `b075447e866f` | `origin/dev/issue226-generation-image-library` / `0	0` | 0 / 0 / 0 | 879 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue226-merged` | `detached` / `49963dc129a1` | `none` / `n/a` | 0 / 0 / 0 | 828 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue228` | `codex/issue228-forge-api` / `2be77c2118f0` | `origin/codex/issue228-forge-api` / `0	0` | 0 / 0 / 0 | 846 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue229` | `codex/issue229-local-lora` / `ed81241ba073` | `origin/codex/issue229-local-lora` / `0	0` | 0 / 0 / 0 | 855 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue232` | `codex/issue232-prompt-intelligence` / `2f9d76b3d2bc` | `origin/codex/issue232-prompt-intelligence` / `0	0` | 0 / 0 / 0 | 858 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue245` | `codex/issue245-ui-audit` / `7dd9a7a2274d` | `origin/codex/issue245-ui-audit` / `0	0` | 0 / 0 / 0 | 1028 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue245-clean-main` | `detached` / `a96dcd10d77e` | `none` / `n/a` | 0 / 0 / 0 | 295 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-issue245-release` | `codex/issue245-lkg-closeout` / `c75a4795bd08` | `origin/codex/issue245-lkg-closeout` / `1	0` | 0 / 0 / 0 | 875 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktree-maint-github-authority-sync-20260916` | `maint/github-authority-sync-20260916` / `b3711dfcead1` | `origin/maint/github-authority-sync-20260916` / `0	0` | 0 / 0 / 0 | 295 | retain unique history; not proven merged |
| `C:/Codex/DanbooruTagTool/.worktree-runtime-performance-post131-20260920` | `audit/runtime-performance-post131` / `c392c86f16f5` | `origin/audit/runtime-performance-post131` / `0	0` | 0 / 0 / 0 | 811 | retain unique history; not proven merged |
| `C:/Codex/DanbooruTagTool/.worktrees/foundation-batch-a` | `foundation/batch-a` / `0d76ee2d6df2` | `origin/main` / `0	0` | 0 / 38 / 41 | 391 | Foundation active; commit/PR review STOP |
| `C:/Codex/DanbooruTagTool/.worktrees/issue109-b2` | `audit/issue109-special-reverse-audit` / `ac2be96b0ac3` | `origin/audit/issue109-special-reverse-audit` / `0	0` | 0 / 0 / 0 | 1 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktrees/issue94` | `audit/issue94-special-gap-audit` / `3d47a36374dd` | `origin/audit/issue94-special-gap-audit` / `0	4` | 0 / 0 / 0 | 5 | retain unique history; not proven merged; Issue closed |
| `C:/Codex/DanbooruTagTool/.worktrees/main` | `main` / `0d76ee2d6df2` | `origin/main` / `0	0` | 0 / 0 / 0 | 0 | clean main entry |
| `C:/Users/takas/.codex/worktrees/1ac3/DanbooruTagTool` | `dev/issue132-production-delta` / `171427140ab5` | `origin/dev/issue132-production-delta` / `0	0` | 0 / 0 / 0 | 596 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Users/takas/.codex/worktrees/1c9b/DanbooruTagTool` | `detached` / `4e85099737e0` | `none` / `n/a` | 0 / 0 / 0 | 0 | retain app-managed/other chat checkout; no owner-directed deletion |
| `C:/Users/takas/.codex/worktrees/4026/DanbooruTagTool` | `detached` / `0bf77e15d952` | `none` / `n/a` | 0 / 0 / 0 | 2 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/526c/DanbooruTagTool` | `detached` / `fd1b3829d0e7` | `none` / `n/a` | 0 / 0 / 0 | 35 | retain protected ignored files/other chat ownership |
| `C:/Users/takas/.codex/worktrees/6a5b/DanbooruTagTool` | `detached` / `c37e739ce24f` | `none` / `n/a` | 0 / 0 / 0 | 2 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/7073/DanbooruTagTool` | `audit/issue179-refresh-20261001` / `c42159c2ed8f` | `origin/audit/issue179-refresh-20261001` / `0	0` | 0 / 0 / 0 | 8807 | retain protected ignored files/other chat ownership; Issue closed |
| `C:/Users/takas/.codex/worktrees/8008/DanbooruTagTool` | `research/high-frequency-character-home-rescue` / `9b9364bfaecb` | `none` / `n/a` | 0 / 0 / 65 | 51 | retain unfinished research/knowledge (recovery ZIP) |
| `C:/Users/takas/.codex/worktrees/8b2a/DanbooruTagTool` | `detached` / `6235d9be9ac1` | `none` / `n/a` | 0 / 0 / 0 | 3 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/92f0/DanbooruTagTool` | `codex/issue44-smartphone-textbook` / `f6c5773c664a` | `origin/codex/issue44-smartphone-textbook` / `0	0` | 0 / 0 / 5 | 1895 | retain unfinished research/knowledge (recovery ZIP); Issue open |
| `C:/Users/takas/.codex/worktrees/93bb/DanbooruTagTool` | `detached` / `579d6ffe2e7b` | `none` / `n/a` | 0 / 0 / 0 | 2 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/edc4/DanbooruTagTool` | `detached` / `4e85099737e0` | `none` / `n/a` | 0 / 0 / 0 | 0 | retain app-managed/other chat checkout; no owner-directed deletion |
| `C:/Users/takas/.codex/worktrees/f008/DanbooruTagTool` | `maint/post-211-routing-finalization` / `dfd5544146c2` | `origin/maint/post-211-routing-finalization` / `0	0` | 0 / 0 / 0 | 1007 | retain protected ignored files/other chat ownership |
| `C:/Users/takas/.codex/worktrees/f8a0/DanbooruTagTool` | `detached` / `e4b2b6394dd2` | `none` / `n/a` | 0 / 0 / 0 | 6 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/fa41/DanbooruTagTool` | `research/ordinary-tag-practical-retrieval-audit` / `13485dfdd7f6` | `origin/research/ordinary-tag-practical-retrieval-audit` / `0	0` | 0 / 0 / 0 | 291 | retain unique history; not proven merged |
| `C:/Users/takas/.codex/worktrees/home-coverage/DanbooruTagTool` | `codex/issue216-unresolved-coverage` / `cc5b10c287df` | `origin/codex/issue216-unresolved-coverage` / `0	0` | 0 / 0 / 0 | 0 | retain app-managed/other chat checkout; no owner-directed deletion; Issue closed |
| `C:/Users/takas/.codex/worktrees/issue203-storage-runtime/DanbooruTagTool` | `codex/issue203-storage-runtime-guard` / `51268c7160ba` | `origin/codex/issue203-storage-runtime-guard` / `0	0` | 0 / 0 / 0 | 817 | retain unique history; not proven merged; Issue closed |
