# Protected data recovery final closure — 2026-09-10

## Final verdict

`RECOVERY_HOLD`

The 177-row candidate passed the requested independent Phase 1 comparison,
but the first production-contract test after installing it failed. The
candidate was not kept: the protected audit input was restored byte-for-byte
to its pre-attempt 175-row state. No production profile or other protected
data was modified.

## Phase 1 — candidate independent confirmation

Candidate provenance:

`docs/handoff_archive/stage6_5_pre_20260906_/CHATGPT_HANDOFF/data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv`

| item | current 175-row file | candidate |
|---|---:|---:|
| rows | 175 | 177 |
| size | 35,507 bytes | 36,157 bytes |
| SHA-256 | `22c76da0cb3a2b58c36b405609823e11c332ae5565c1c4bd35501a3c0be2bbf5` | `7bf6218f4d9456596c19e32a79ca02cb747c07371b859e5b565ff7a7e2231c64` |
| schema | identical | identical |
| duplicate SpecialID | none | none |

The existing 175 rows were byte-for-byte CSV-record matches. Candidate-only
rows were exactly SpecialID `152` and `697`; no unexpected row was found.

| SpecialID | candidate correction | production profile |
|---:|---|---|
| 152 | `MULTI_ACTOR_INTERACTION` → `INSERTION_STRUCTURED`, role `compound_action` → `bodypart_action` | `INSERTION_STRUCTURED` / `bodypart_action` |
| 697 | `MULTI_ACTOR_INTERACTION` → `ACTION_INTERACTION`, role `compound_action` → `action` | `ACTION_INTERACTION` / `action` |

The candidate SHA matched the supplied SHA exactly. Phase 1 therefore passed.

## Phase 2 — attempted restoration and safe rollback

Before restoration, the target file was recorded as:

- rows: 175
- size: 35,507 bytes
- SHA-256: `22c76da0cb3a2b58c36b405609823e11c332ae5565c1c4bd35501a3c0be2bbf5`

The candidate was copied byte-for-byte, not edited or line-ending converted.
The immediate post-copy state was 177 rows, 36,157 bytes, and SHA-256
`7bf6218f4d9456596c19e32a79ca02cb747c07371b859e5b565ff7a7e2231c64`.

The subsequent production-contract test failed. To avoid leaving an
unverified candidate in protected data, the original 175-row file was copied
back from the SHA-verified existing backup:

`backups/family_v2_1_final_audit_fix_20260906_0415/data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv`

Final target state:

- rows: 175
- size: 35,507 bytes
- SHA-256: `22c76da0cb3a2b58c36b405609823e11c332ae5565c1c4bd35501a3c0be2bbf5`

## Failure cause

The failed test was:

`tests/test_generation_profile.py::test_v2_1_review_sets_match_production_exactly`

With the candidate installed, the 177-row count assertion passed, but the
test then found that the retained `APPROVED_STATIC_1352_REVIEW_v1.csv` still
proposes the pre-final values for both rows:

| SpecialID | review proposed value | current production profile |
|---:|---|---|
| 152 | `MULTI_ACTOR_INTERACTION` / `compound_action` | `INSERTION_STRUCTURED` / `bodypart_action` |
| 697 | `MULTI_ACTOR_INTERACTION` / `compound_action` | `ACTION_INTERACTION` / `action` |

Therefore the 177-row candidate alone is not sufficient evidence of a
complete, internally consistent v2.1 audit bundle. It is a historical
candidate containing the two final correction rows, but another protected
audit input remains on the older contract. No file was edited to force the
test to pass.

## Regression results

- Runtime index integrity: PASS before this repair attempt; true-AND cases and
  global-count match passed.
- Previous targeted suite: 200 passed / 1 failed while the 175-row file was
  present.
- Candidate-specific test after restoration: failed at the review/profile
  contract after the 177-row count passed.
- Full `python -m pytest -q`: not run because the recovery-specific contract
  remained inconsistent.
- Runtime index was not regenerated.

## Final protected-data inventory

After rollback, excluding the already-rejected unused
`data/source/danbooru2026_clean.parquet`:

- files: 89
- bytes: 7,127,475,658
- accident-before reference: 89 files / 7,127,474,426 bytes
- delta: +1,232 bytes
- known README difference: +40 bytes
- remaining known delta: +1,192 bytes, still covered by the prior
  scan-group/EOL accounting, but not sufficient to close the content-level
  audit inconsistency

Current group totals:

| group | files | bytes |
|---|---:|---:|
| `data/source/` excluding ThetaCursed extra | 1 | 3,436,154 |
| `data/derived/` | 16 | 25,336,393 |
| `data/generation/` | 10 | 2,493,262 |
| `data/runtime/` | 1 | 2,236,277 |
| `data/runtime_index/` | 11 | 2,989,206,293 |
| `data/runtime_source/` | 1 | 4,088,245,636 |
| `data/special2788/` | 25 | 1,756,179 |
| `data/japanese/` | 5 | 14,510,223 |
| `data/semantic/` | 19 | 255,241 |

Maintained recovery facts:

- identified missing: 0
- exact source recovery: 4/4
- exact runtime rebuild: 8/8 SHA-matched
- new snapshot metadata: 3/3 valid
- unexpected ThetaCursed Parquet: unused and excluded
- unique local loss: 0 confirmed
- recovery-attempt hash mismatch in final state: 0; final state is the
  original 175-row SHA, not the candidate SHA

## Safety and stop point

- No alternate snapshot was used.
- No production profile was changed.
- No unknown file was deleted.
- No `git clean`, junction, symlink, main merge, #35 completion, #49 start,
  or Stage10 start was performed.
- The unresolved blocker is the inconsistent v2.1 audit bundle, specifically
  the 175-row `APPROVED_STATIC_1352_REVIEW_v1.csv` versus the final profile
  values for IDs 152 and 697.

Stop at `RECOVERY_HOLD`.
