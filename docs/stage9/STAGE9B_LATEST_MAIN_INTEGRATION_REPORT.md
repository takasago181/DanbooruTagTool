# Stage9B Latest-Main Integration Report

Date: 2026-09-08 JST
Current DEV Issue: #2 `[Stage9B][DEV] Runtime Composer Stage9B`
Status: integrated on review branch; DEV decision required for a latest-main protected-test failure unrelated to Stage9B files.

## Integration

- Latest main base: `7799704f4929baaa689e38579095c98856d6d715`
- Audited Stage9B commit: `eb4048f68f28ea53c3fc1c47a8b3671065be8dbf`
- Integration branch: `codex/stage9b-main-integration`
- Integration commit: `8c88a85`
- Method: cherry-pick onto latest main. No conflicts occurred.
- Only Stage9B production/report/test files differ from `origin/main`:
  - `danbooru_tag_tool/prompt_composer.py`
  - `danbooru_tag_tool/stage9b_runtime.py`
  - `docs/stage9/STAGE9B_IMPLEMENTATION_REPORT.md`
  - `tests/test_stage9b_runtime.py`

## Reverification

- Stage9A regression + Stage9B focused: **36 passed**
- Ruleset2 + Stage8C regression: **34 passed**
- `git diff --check origin/main..HEAD`: PASS
- Protected regression: **107 passed, 1 failed**

The sole failure is `tests/test_stage0_integrity.py::test_protected_source_files_match_hash_manifest`.
It is not caused by the Stage9B integration diff. Latest `origin/main` already contains the directory `data/special2788/prompt_reference/`, added by `b0ecbed0fc2edccbec3b1cc28cc7cbfea3384f69`, while the unchanged test iterates every direct child of `data/special2788/` and asserts each child is a file. The new directory therefore fails `path.is_file()` before a hash is read.

No source data, manifest, Stage0 test, or prompt-reference file was changed here. This integration task must not speculate about whether the intended resolution is to change the test, manifest policy, or data layout.

## Exact stopping point

Stage9B was integrated without conflicts and its focused/regression coverage passes. Stop before Stage9C/9D and Stage10. DEV must decide how to resolve or formally classify the existing latest-main Stage0 protected-test failure, then verify the remote integration branch and record the Issue #2 completion evidence.
