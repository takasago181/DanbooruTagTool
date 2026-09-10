# Protected Data Recovery — Audit Bundle Closure

Date: 2026-09-10
Branch: `dict-validation/quarantine`

## Final verdict

`PROTECTED_DATA_RECOVERY_COMPLETE`

The protected-data recovery blocker was resolved with an existing canonical
Generation Profile v2.1 handoff artifact. No production profile, runtime
index, alternate snapshot, or unrelated protected file was changed.

The full pytest command was executed. Its non-zero result is classified below:
the two assertion failures and 52 collection/setup errors are pre-existing
environment or known protected-data-baseline issues, not failures caused by
the recovery. The recovery-specific targeted suite passed completely.

## Phase 1 — provenance audit

Classification: `EXACT_REVIEW_ARTIFACT_FOUND`

The authoritative provenance is independently recorded in:

- `docs/stage_reports/GENERATION_PROFILE_V2_1_REPORT.md`
- `docs/handoff_archive/stage6_5_pre_20260906_/CHATGPT_HANDOFF/HANDOFF_MANIFEST.md`
- Git history and the existing Stage 6.5 handoff bundle

The v2.1 report states that the final audit corrected SpecialID 152 to
`INSERTION_STRUCTURED / bodypart_action` and SpecialID 697 to
`ACTION_INTERACTION / action`. The handoff manifest records the same two
corrections, removal of `ACTOR_SEPARATION_REQUIRED` from both rows, and the
177-row correction contract.

The exact review artifact was found at:

`docs/handoff_archive/stage6_5_pre_20260906_/CHATGPT_HANDOFF/data/generation/audit/APPROVED_STATIC_1352_REVIEW_v1.csv`

It was copied byte-for-byte to the protected production audit path after SHA
verification. The exact corrections artifact was likewise found at:

`docs/handoff_archive/stage6_5_pre_20260906_/CHATGPT_HANDOFF/data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv`

## Phase 2 — review artifact restoration

| artifact | rows | restored size | restored SHA-256 |
|---|---:|---:|---|
| `APPROVED_STATIC_1352_REVIEW_v1.csv` | 1,352 | 546,994 | `c7321362439bb7afe3adf4629c42625580e1826c811fe4df5f266ad837bca581` |
| `HIGH_CONFIDENCE_CORRECTIONS_v1.csv` | 177 | 36,157 | `7bf6218f4d9456596c19e32a79ca02cb747c07371b859e5b565ff7a7e2231c64` |

The previously present review artifact had 1,352 records but retained old
values for exactly IDs 152 and 697. The restored handoff artifact has the
following final values:

| SpecialID | old review value | restored review value | production profile |
|---:|---|---|---|
| 152 | `MULTI_ACTOR_INTERACTION / compound_action` | `INSERTION_STRUCTURED / bodypart_action` | exact match |
| 697 | `MULTI_ACTOR_INTERACTION / compound_action` | `ACTION_INTERACTION / action` | exact match |

The review schema and ID set are unchanged. Parsed record comparison proves
that the other 1,350 records are unchanged. The artifact's CRLF byte
representation is preserved from the canonical handoff; this is an artifact
representation difference, not a content reconstruction.

## Phase 3 — three-way audit bundle consistency

The restored review, 177-row corrections table, and current production profile
were compared by SpecialID. All 1,352 review proposed values match the
production profile; no bundle mismatches remain.

The corrections table has the canonical v2.1 counts:

- rows: 177
- Family changes: 153
- Role changes: 162
- PromptUseMode changes: 116

The production profile was not modified. The review was brought up to the
already-authoritative production/profile and handoff values.

## Current protected-data inventory

The current inventory contains 90 files and 11,068,121,292 bytes including
the already-known unused extra
`data/source/danbooru2026_clean.parquet` (ThetaCursed snapshot), which remains
untouched and excluded from the protected recovery comparison.

After excluding that known unexpected extra, the inventory is:

- files: 89
- bytes: 7,127,477,433
- accident-before reference: 7,127,474,426 bytes
- delta: +3,007 bytes

The delta consists of the previously audited +1,232-byte scan/reference
difference plus +1,775 bytes from restoring the canonical CRLF review and
177-row audit artifacts. The restored artifacts are the formally evidenced
v2.1 audit bundle, not a numeric adjustment or alternate snapshot.

The remaining known representation/reference differences are documented in
`docs/recovery/PROTECTED_DATA_RECOVERY_DELTA_CLOSURE_20260910.md`, including
the +40-byte README difference and tracked-file CRLF/EOL differences.

Recovery state:

- missing files: 0
- exact source recovery: 4/4
- exact runtime rebuild: 8/8 SHA match
- runtime metadata: 3/3 valid new-snapshot metadata
- runtime index total: 2,989,206,293 bytes
- runtime source: exact pinned source SHA
- unique local loss: 0 confirmed
- alternate snapshot used: 0
- production profile changed: no
- runtime index regenerated in this closure: no

## Regression results

### Runtime index integrity

`tools/verify_runtime_index.py` passed against the existing pinned runtime
source and runtime index:

- `pass: true`
- `global_count_match: true`
- one-, two-, three-, and five-tag true-AND queries: PASS
- small, medium, and large candidate cases: PASS

### Targeted regression

The required gate passed:

`python -m pytest -q tests/test_generation_profile.py::test_v2_1_review_sets_match_production_exactly`

Result: `1 passed`.

The targeted recovery/regression suite passed:

Result: `201 passed`.

### Full pytest

Command: `python -m pytest -q`

Result: `221 passed, 2 failed, 52 errors, 2 warnings`.

The non-zero result is not recovery-caused:

1. `tests/test_stage0_integrity.py::test_protected_source_files_match_hash_manifest`
   fails because the known unused ThetaCursed parquet remains present. It was
   intentionally not deleted and is excluded from the recovery comparison.
2. `tests/test_stage8c_phase0.py::test_stage8b_resolver_and_accepted_stage8c_production_hashes_are_protected`
   reports the pre-existing `semantic_support_profiles.csv` current hash
   versus the older test expectation. The file was not changed in this
   closure, and production data was not edited to make the test pass.
3. The 52 errors are pytest temporary-directory permission failures under
   `C:\Users\takas\AppData\Local\Temp\pytest-of-takas`, not test assertion
   failures from the restored audit bundle.

No recovery-caused full-suite failure remains. No code or production profile
was changed to mask any failure.

## Scope boundary

No `git clean`, protected-data deletion, junction/symlink, runtime-index
regeneration, alternate snapshot substitution, #35 completion, #49 start,
Stage 10 start, or main merge was performed.
