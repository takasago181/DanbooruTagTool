# Special Core Dictionary — Final Freeze and Handoff

Date: 2026-09-10 JST
Status: **FINAL freeze record / naming-only handoff**
Issue: #43
Formal concept: **`Special Core Dictionary`**

## Frozen production snapshot

| Field | Value |
|---|---|
| Production snapshot commit | `490f5653460804c8a40cb48d093b91d5d8dd5d9c` |
| Production profile path | `data/generation/special2788_generation_profile.csv` |
| Row count | 2,788 |
| Unique identity count | 2,788 unique `SpecialID` values |
| Fixed order | `SpecialID` 1 through 2,788 |
| Production profile SHA-256 | `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd` |

The profile content, identity set, row order, and hash are recorded here as
the current production snapshot facts. This Issue #43 change does not rewrite
the profile or any other `data/**` file.

## Provenance chain

- **Issue #32 validation:** full 2,788-entry validation and completeness
  reconciliation; final evidence checkpoint `5605952933`.
- **Issue #48 promotion audit:** independent final promotion audit,
  `APPROVE_WITH_REQUIRED_PROMOTION_CONTRACT`; evidence checkpoint `5605993533`.
- **Issue #49 production promotion + post-write audit:** approved effective
  FIX subset promoted, post-write state `APPROVE_ISSUE49_POST_WRITE`, and
  fast-forwarded to production commit `490f565`. Supporting evidence is in
  `docs/issue49/protected_data_integrity.json` and the synchronized current
  state.

## Carry-forward assets — parked, not discarded

The following remain available for later separately gated work:

- Special `REVIEW`: **305**
- Special `IMAGE_TEST_REQUIRED`: **17**
- semantic-support `IMAGE_TEST_REQUIRED`: **33 rows**

These assets must not be silently promoted, deleted, counted as production
rows, or converted into a bulk PASS/REJECT. They remain candidates for #42,
#30, and Stage10 controlled image review under their own evidence gates.

## Intentional compatibility identifiers

The following intentionally remain `special2788` / `Special2788`:

- protected source and prompt-reference paths under `data/special2788/`;
- production profile path `data/generation/special2788_generation_profile.csv`;
- runtime and tool path literals, loader references, and internal source-lane
  keys;
- `special2788_version` and `special2788_hash` manifest/schema keys;
- protected hash manifests and integrity evidence;
- semantic/source rows and serialized or machine-readable evidence fields;
- historical reports, issue text, checkpoints, old commits, and audit records.

These are compatibility or historical identities, not competing formal product
concept names.

## Downstream handoff rule

KNOWLEDGE #44, PROMPT #5, #30, and #42 shall use **Special Core Dictionary**
when naming the formal concept. They shall use `Special2788` only when naming
the frozen physical snapshot/corpus, protected identifier, or immutable
evidence reference. `Core Tag Set` remains the user-selected generation
nucleus, and `Special` remains the default per-entry wording.

No downstream handoff implied by this record starts #36, #30 calibration,
#42, #5, or Stage10 production A/B. Those remain separately gated.

## Verification record

- Dictionary/profile content changed by this branch: **0**
- Production profile SHA before/after naming work: **unchanged** (value above)
- Production profile rows / unique identities / order: **2,788 / 2,788 / unchanged**
- #49 protected-after evidence set: **24 checked / 0 mismatches**
- Direct naming + Stage9/session focused suite: **92 passed**
- UI regression: **24 passed**
- Repository full suite: **classified** — initial `233 passed, 7 failed, 52
  errors`; with a safe workspace-local pytest basetemp, `285 passed, 7 failed,
  0 errors`. The seven failures are pre-existing protected-data/path-set and
  semantic-fixture baseline mismatches; the 52 setup errors are environment
  ACL failures. They do not identify a naming-diff failure.
- Repository-wide `FILE_HASHES.json`: **79 checked / 15 mismatches**. This
  includes mutable current documentation changed by this naming migration and
  pre-existing local baseline mismatches, so it is not reported as a clean
  repository-wide integrity PASS. No mismatching protected file was modified
  by this branch, and the 24-file #49 protected-after set remains clean.
- `git diff --check`: **PASS**

Root-cause audit: `docs/issue43/ISSUE43_HOLD_ROOT_CAUSE_AUDIT_20260910.md`.
The final verdict for Issue #43 is **`PASS_ISSUE43_FREEZE`**; the residual
failures are not caused by this naming-only branch.
