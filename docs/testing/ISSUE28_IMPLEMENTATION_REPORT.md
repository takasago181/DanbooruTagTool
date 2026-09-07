# Issue #28 Automated E2E functional gate

Date: 2026-09-08. DEV implementation by Codex.
Branch: `codex/issue28-e2e-verdict`.
Base main: `f60ff9074a5d8f3db8f7ab7ffa8691e8ef02c75f`.
CURRENT_STATE active DEV and CURRENT_DEV_TASK Source both identify #28.
Stage9 overall PASS is already recorded by DEV/AUDIT on main; this report does not redo that decision.

## Implementation

- Added three automated functional paths using real Stage7AApp, Tk widgets/event loop, search presenter, protected local knowledge, RuntimeIndex/CanonicalOverlay, asynchronous RecommendationController/RecommendationEngine, semantic adapters and Stage9 Composer session.
- Search `blindfold` -> select Special ID 1816 -> wait for real worker results -> select real common and rare notebook buttons. Both buckets must be nonempty; the rare selection uses a distinct candidate. No candidate results or GUI widgets are mocked.
- Verify independent semantic/statistical lanes, all eight raw statistical evidence fields, snapshot identity, stable INCLUDE/EXCLUDE and unchosen DEFAULT across reordered results; semantic INCLUDE is exercised separately. DEFAULT means absence of a decision, not an added reset-to-default UI control.
- Manual search/add/remove, chip removal, Tk preview and copy button/clipboard equality are checked. Existing text clipboard is restored when available.
- Twelve variant combinations exercise four model families and counts 0/1/2, Special placement, explicit role inputs/weight text, LoRA contraction and metadata. Complete baseline ComposeResult and variant are restored each time. Synthetic weight/LoRA strings are test inputs, not model grammar recommendations or image-generation calls.
- Stale callback and queued result, wrong core, unknown status, invalid Special/manual/candidate IDs and malformed current-request result are checked against unchanged state.
- `--e2e-report PATH.json` writes JSON and sibling Markdown using standard pytest hooks. Required GUI test IDs must pass. Failures (including teardown), interrupted/failed runs -> FAIL; missing/skip-only required paths -> BLOCKED. BLOCKED changes a nominally successful pytest exit to 2.
- Reports capture command, environment, timestamp, source commit, working-tree state, tested-file SHA256, test outcomes, selected-state evidence and actual structured/flattened Prompt output.

## E2E-discovered production defect

Initial real malformed-result test failed: `_show_recommendation_result` replaced its current result before candidate validation. The session could also update one lane before the other failed.
The minimal fix builds/validates both candidate lanes before assignment; UI accepts the new result only after successful registration. Invalid status/payload leaves the prior valid state intact. Added two focused session regression cases for unknown canonical and invalid approved-role input.
No ranking, metric, selection policy, role inference, grammar or source data was changed to make the test pass.

## Tests and environment

Windows local protected-data environment; Python 3.12; real Tk 8.6.15 with withdrawn root (no mocked rendering). This is NOT GitHub Actions evidence. No display server or package installation was required.

Commands:

```powershell
python -m pytest -q tests/test_e2e_functional.py tests/test_e2e_verdict.py tests/test_stage9c_session.py --e2e-report docs/testing/issue28_focused.json --basetemp .pytest-issue28-focused-final
python -m pytest -q --e2e-report docs/testing/issue28_full.json --basetemp .pytest-issue28-full-final
git diff --check
```

- Development focused run: 31 passed.
- Stage0 protected + Stage7A/B + Stage8A/B/C + Ruleset2 + Stage9A/B regression selection: 145 passed.
- Development full run: 285 passed in 58.34s, no skips/failures.
- Negative gate probe: running only `tests/test_e2e_verdict.py` with `--e2e-report` produced BLOCKED and process exit 2, despite all five selected tests passing. Missing GUI paths cannot yield E2E PASS.
- Final commit-associated focused/full evidence is in `issue28_focused.json/.md` and `issue28_full.json/.md`; their source commit and hashes identify the tested code. The later evidence-only commit necessarily differs from the tested source commit.

## Protected surfaces

Unchanged: FILE_HASHES.json, PACKAGE_MANIFEST.json, all source/Special dictionaries, derived/runtime/index data, Ruleset2, Stage8C authority CSVs/family rules, Stage8B support logic, Stage6 recommendation metrics and Stage9A/B implementations. Stage0 hash/size/path-set checks remain enabled, including Issue #26 protections.
The only changed surface hash is the explicit UI byte hash in test_stage8c_phase0.py, for the demonstrated input-validation correction: `cb7fa90dceff84c41d895a0744bdade3da5343c5aaa5dbb5a13db486cecd6258` (Windows CRLF). No protected hash assertion was removed or bypassed.

## Changed / new files

Modified: `danbooru_tag_tool/ui.py`, `danbooru_tag_tool/stage9c_session.py`, `tests/test_stage9c_session.py`, `tests/test_stage8c_phase0.py`.
New: `conftest.py`, `tools/e2e_verdict.py`, `tests/test_e2e_functional.py`, `tests/test_e2e_verdict.py`, this report, and four focused/full JSON/Markdown evidence files.
Recovery/review: feature-branch Git history and remote push. No local protected data was deleted, moved, backed up into Git or regenerated. No ZIP is required for code review.

## Limits and exact stop

- This verifies local functional behavior, not visual layout, OS mouse/keyboard injection, all 2,788 Specials, performance under concurrent Forge use, or image quality. Hidden Tk uses real widgets and commands but is not a manual desktop visual inspection.
- Variant/state controls absent from the UI are exercised through the existing production session API; no new experimental UI was added.
- Local protected data and compatible index are required. Tk/data absence yields BLOCKED, not a mock fallback. Fresh clone/CI alone is not assumed to contain these files.
- No GitHub Actions workflow or Stage10 image runner/scoring system was added. No #4/#5/#6 work was substituted.
- DEV must inspect the remote branch, code, machine/human reports, protected results and limits, then record Issue #28 evidence. Stop at that DEV review boundary; do not mark management gates complete or start Stage10 production A/B based on Codex's report alone.
