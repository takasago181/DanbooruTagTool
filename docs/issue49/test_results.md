# Issue #49 test results

Correction-gate branch: `codex/issue49-dict-promotion-latest-main`.
Reverified HEAD: `484bf928a1b1c8c07f349bcc1bc77681d72e2160`.
Latest-main base: `ad9d0f314151b94b7888e9059d4a77cf5cfc4e22`.

All pytest commands used `-p no:cacheprovider` and an explicit writable
`--basetemp` because the host's default pytest temp directory is inaccessible.

| Command | Result |
|---|---|
| `python -m pytest -p no:cacheprovider --basetemp <task-temp> -q tests/test_issue49_promotion.py tests/test_generation_profile.py tests/test_e2e_functional.py tests/test_e2e_verdict.py` | PASS — 45 passed |
| `python -m pytest -p no:cacheprovider --basetemp <task-temp> -q tests/test_stage0_integrity.py tests/test_stage9c_session.py tests/test_stage7a_ui.py` | 56 passed, 1 pre-existing environment failure |
| `python -m pytest -p no:cacheprovider --basetemp <task-temp> -q` | 282 passed, 7 failures |
| `git diff --check` | PASS |
| Issue #49 promotion preflight | PASS — 0 effective conflicts; all pre-write gates satisfied |
| Issue #49 post-write integrity report | PASS — no non-target protected changes; semantic paths unchanged |

The Stage 0 failure is the pre-existing local protected file
`data/source/danbooru2026_clean.parquet`, which is present locally but absent
from the repository's `FILE_HASHES.json`; it was not modified or added.

Six full-suite failures are Stage8 audit fixtures that still describe the
pre-promotion FamilyRule membership (the effective profile assignments move
audited Specials, including 680, between families). They are recorded for the
separate post-write audit; no semantic source or audit data was changed to mask
them.
