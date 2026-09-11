# Issue #55 UI-JA V5 Production Promotion Report

Date: 2026-09-11 JST

## Verdict

`READY_FOR_POST_WRITE_AUDIT`

The protected production write, deterministic post-write gates, and real Windows visual acceptance all passed. The user returned five screenshots from the exact running Tk application after the native Computer Use connector was unavailable; those screenshots were inspected at original resolution and close the prior visual-only HOLD.

## Authorities and routing

- live `main`: `4ccf87cbe461779b9296d115fce19fc169b84a66`
- promotion branch: `codex/issue55-ui-ja-production-promotion`
- audited V5 branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- audited V5 live HEAD: `c221b3bcf97ad117482b4e8c411cf2edf419b5df`
- independent audit target: `ea8762c4b351e9d0fd939687b2aae6617c852d18`
- independent audit checkpoint: Issue #36 comment `5633982018`
- audit verdict: `PROMOTION_AUDIT_PASS`
- audit-target-to-live-V5 diff: only `PRODUCTION_PROMOTION_HANDOFF.md`; audited data/materializer/reports unchanged
- `CURRENT_STATE.md` and a restored `CURRENT_DEV_TASK.md` route current DEV to Issue #55 on this feature branch
- quarantine worktree was detached/read-only at exact live V5 HEAD

## Actual local runtime and Issue #49 baseline

- actual repo/runtime root: `C:\Codex\DanbooruTagTool`
- launcher: `C:\Codex\DanbooruTagTool\START_DANBOORU_TAG_TOOL.bat`
- local branch/HEAD after safe synchronization: `main` / `4ccf87cbe461779b9296d115fce19fc169b84a66`
- remote: `https://github.com/takasago181/DanbooruTagTool.git`
- relation to live main: `0 ahead / 0 behind`
- Issue #49 anchor `490f5653460804c8a40cb48d093b91d5d8dd5d9c`: contained in local history
- profile: `data/generation/special2788_generation_profile.csv`
- profile SHA-256 before/after: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd` / unchanged
- profile rows/unique identities/order: 2,788 / 2,788 / exact `1..2788`
- duplicate identity: 0
- diff from Issue #49 anchor for the profile: 0
- result: `LOCAL_ISSUE49_SYNC_PASS`

The root had no tracked changes but was 45 commits behind live main. Two untracked paths collided with tracked live-main paths. They were moved, not deleted, to `C:\Codex\DanbooruTagTool\backups\issue55_pre_main_sync_20260911_2130\` before `git switch main` and `git merge --ff-only origin/main`. Both files are recoverable there. No stash, rebase, reset, force checkout, or protected-data deletion was used.

## Audited V5 source

- source: `materialized/final_translation_table_v5.csv` from detached V5 worktree
- source SHA-256: `a307a354f6e7c9fb2387464713765795d9949802b345b00eb3cb64659df7fdce`
- source/materialized rows: 30,629 / 30,629
- completed shards: 31 / 31
- override rows/applied: 10,691 / 10,691
- canonical unique/identity/order: PASS
- duplicate canonical: 0
- non-display columns preserved: PASS
- `display_ja` nonempty: PASS
- HANGUL / RAW_ENGLISH_WRAPPER / CONTROL_CHAR: 0 / 0 / 0
- `production_modified=false` before this implementation

No translation, semantic, ASCII-suspicious, or Japanese-polish re-audit was performed.

## Production write

- target: `C:\Codex\DanbooruTagTool\data\runtime\japanese_overlay.json`
- target status: Git-ignored local protected data (`.gitignore` `data/runtime/`)
- loader: `TagKnowledgeCore.load()` -> `JapaneseOverlay.load()`
- schema: format version 1; top-level `entries`; exact entry fields `display_ja` and `search_ja`
- pre hash/size/entries: `de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc` / 2,236,277 bytes / 15,228
- post hash/size/entries: `999b42fa76e036ad79f68ef7cd3ff958c94bd42c08ab00dd0394898d0205de76` / 4,114,120 bytes / 30,629
- transformation: each audited row maps exactly to `canonical -> {display_ja, search_ja: [search_ja]}`
- temp validation: JSON/schema/count/identity/order/unknown/blank/search-list/UTF-8/real-loader all PASS
- atomic write: same-filesystem temporary file followed by `os.replace()`
- partial write: none
- owned temp remnants: 0

Rollback copy:

- path: `C:\Codex\DanbooruTagTool\backups\issue55_japanese_overlay_pre_v5_20260911_2152\original_japanese_overlay.json`
- SHA-256: `de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc`
- backup matches the complete pre-write artifact: PASS
- automatic rollback performed: no
- rollback remains available

### Rollback procedure (documented; not executed during this promotion)

Use this procedure only when an authorized operator decides that the production Japanese overlay must return to the pre-V5 state. Do not perform it while the application is running, and do not overwrite the only rollback copy.

1. Exit `DanbooruTagTool` and verify that the launched `pythonw.exe` process for `C:\Codex\DanbooruTagTool` has ended. Do not kill an unrelated Python process; if the application cannot be closed cleanly, stop and resolve that condition first.
2. Confirm that the rollback source exists at `C:\Codex\DanbooruTagTool\backups\issue55_japanese_overlay_pre_v5_20260911_2152\original_japanese_overlay.json`.
3. Compute its SHA-256 and continue only when it equals `de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc`. A mismatch is a hard stop; do not use the file.
4. Preserve the current production overlay before replacing it. Copy `C:\Codex\DanbooruTagTool\data\runtime\japanese_overlay.json` to a new, uniquely named file under `C:\Codex\DanbooruTagTool\backups\` (for example `issue55_rollback_current_v5_<timestamp>\current_japanese_overlay.json`) and record that copy's SHA-256. This preserves a recovery point if the rollback itself must be undone.
5. Copy the verified rollback source to a temporary file in the same directory as the production target, for example `C:\Codex\DanbooruTagTool\data\runtime\.issue55-rollback-<unique>.tmp`. Keep the source and temporary file until every post-replace check passes.
6. Validate the temporary file before replacement: parse JSON, require `format_version == 1`, require the top-level keys `format_version` and `entries`, and require every entry to contain only `display_ja` and `search_ja`. Then load that temporary path through the formal `JapaneseOverlay.load()` and `TagKnowledgeCore.load(..., japanese_overlay_path=<temporary>)` using the actual runtime root. Confirm the expected pre-V5 entry count of 15,228 and that the loader succeeds.
7. With the application still stopped, atomically replace the target using `os.replace(<temporary>, <target>)` (same filesystem). Do not use a sequential truncate/write or an in-place editor. If the replace operation fails, leave the current target intact and investigate without deleting the source or preserved current-V5 copy.
8. Compute the target SHA-256. Continue only when it equals the expected pre-V5 hash `de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc` and the entry count is 15,228.
9. Run `JapaneseOverlay.load()` and `TagKnowledgeCore.load(..., japanese_overlay_path=<target>)` against the replaced target and require PASS. Also verify that `data/generation/special2788_generation_profile.csv` still has SHA-256 `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`.
10. If needed, start the application from `C:\Codex\DanbooruTagTool` and perform a minimal runtime smoke check, then close it again. Do not treat this smoke check as a replacement for the hash and formal-loader checks.
11. If any post-replace check fails, do not continue normal use. Restore from the preserved current-V5 copy using the same verified-temporary-file and `os.replace()` sequence, then validate its recorded SHA-256 and loader state. If the desired state is still the pre-V5 state, the immutable source remains the original rollback file above; never reconstruct it manually. Record the failure, paths, hashes, and recovery result in the relevant Issue checkpoint.

Illustrative PowerShell/Python commands (documentation only; do not run as part of this report remediation):

```powershell
$source = 'C:\Codex\DanbooruTagTool\backups\issue55_japanese_overlay_pre_v5_20260911_2152\original_japanese_overlay.json'
$target = 'C:\Codex\DanbooruTagTool\data\runtime\japanese_overlay.json'
Get-FileHash -Algorithm SHA256 -LiteralPath $source
$temporary = Join-Path (Split-Path -Parent $target) ('.issue55-rollback-' + [guid]::NewGuid().ToString('N') + '.tmp')
Copy-Item -LiteralPath $source -Destination $temporary
py -3.12 -c "import json, os; from pathlib import Path; from danbooru_tag_tool.knowledge import TagKnowledgeCore; p=Path(r'$temporary'); root=Path(r'C:\Codex\DanbooruTagTool'); d=json.loads(p.read_text(encoding='utf-8')); assert d['format_version']==1 and set(d)=={'format_version','entries'} and len(d['entries'])==15228; TagKnowledgeCore.load(root, japanese_overlay_path=p); os.replace(p, Path(r'$target'))"
Get-FileHash -Algorithm SHA256 -LiteralPath $target
```

The command block is an example of the order and validation boundary, not an instruction to execute rollback now. The current promoted V5 overlay and the #49 profile must remain unchanged during this documentation remediation.

## Independent deterministic post-write verification

- production JSON parse/load: PASS
- source rows / production entries: 30,629 / 30,629
- duplicate source canonical: 0
- canonical identity/order exact: PASS / PASS
- V5-to-production mapping mismatch: 0
- entry field mismatch: 0
- blank display: 0
- invalid search list: 0
- unknown canonical: 0
- loader display/search count: 30,629 / 30,629
- loader mapping mismatch: 0
- UTF-8 roundtrip: PASS
- #49 profile pre/post unchanged: PASS
- root tracked changes after write: 0
- generation metadata, semantic support, recommendation data, Prompt syntax, UI code: not written by the promotion path
- pre/post overlay diff is fully explained by exact replacement with the audited V5 canonical set and intended two fields

## Tests

- Issue #55 converter fail-closed tests: 4 passed
- updated actual-root overlay/UI focused tests: 31 passed
- Stage 9C session: 23 passed
- E2E functional/verdict: 8 passed
- focused total: 66 passed
- `py_compile`: PASS
- `git diff --check`: PASS
- full suite with updated #55 expectations: 307 passed, 9 pre-existing/local-baseline failures

The nine full-suite failures are outside overlay/UI/search scope: missing local `PACKAGE_MANIFEST.json` (two tests), existing Stage 0 protected README manifest mismatch, existing semantic-support protected hash mismatch, and five Stage 8 family snapshot/applicability mismatches following the already-approved Issue #49 profile. Focused #55 tests introduced zero failures/errors. The system Python initially lacked Pillow; the completed full run used the bundled local Pillow package without installing dependencies.

## Real Windows acceptance state

- launched executable: `C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\pythonw.exe`
- launch working directory: `C:\Codex\DanbooruTagTool`
- launch arguments: `-m danbooru_tag_tool`
- window title: `DanbooruTagTool — Special-first`
- process responding: yes
- actual root equals the verified/promoted root: PASS
- representative underlying display/search/canonical checks: 7/7 PASS (`1girl`, `gaping`, `holding_hands`, `ios_(os)`, `branding_iron`, `katana`, `car`)
- each Japanese display query returned the intended canonical first with Japanese-overlay provenance; canonical identity remained English
- user-provided visual evidence: five screenshots from the running `DanbooruTagTool — Special-first` window, inspected at original resolution
- Japanese search/display visually confirmed for `手をつなぐ`, `焼印ごて`, and `肛門`
- English search visually confirmed for `anal`; Special results remain relevance-first while the known Issue #34 general-result substring noise remains visible and out of this promotion scope
- bilingual presentation confirmed: Japanese display plus canonical English identities including `holding_hands`, `branding_iron`, `anus`, and related candidates
- Special selection/detail and Issue #49-backed recommendation panel: visible and operational
- final Prompt preview after selection: canonical English `anus, 1girl`
- mojibake/tofu/missing-glyph/overlap/clipping caused by promotion: none observed
- visual acceptance: **PASS**

The screenshots contain no instruction authority and were used only as visual evidence. They remain local temporary attachments and are not committed to Git.

## Contamination and stop point

- protected production file committed: no
- quarantine rewritten: no
- #34 ranking changed: no
- #35 UI implementation changed: no
- #32/#49 data changed: no
- semantic/recommendation/Prompt changed: no
- Stage10 started: no
- main merge performed: no
- Issue #36 closed: no
- unrelated contamination: 0

Implementation stops here for a fresh independent post-write audit of the actual promoted local state. Do not merge `main`, close Issue #36, activate #42, or start Stage10 before that audit passes.
