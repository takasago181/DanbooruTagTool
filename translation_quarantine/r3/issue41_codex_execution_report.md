# Issue #41 Codex execution report

## Source-of-truth recovery

- GitHub issue: #41, latest comment `Codex execution slot — run the real #41 pipeline on the repository`
- Branch: `ui-ja/issue41-pilot`
- Expected starting HEAD: `2c17d369e386f5b20881d4244fced22373c5fab5`
- Actual starting HEAD: `2c17d369e386f5b20881d4244fced22373c5fab5`
- Audited R3 base ancestry: `53f02d9b3419db8fd9099b38204c29eed289ee8e` (ancestor)
- `CURRENT_STATE.md`, `PERMANENT_RULES.md`, and `CURRENT_DEV_TASK.md` were reread. The active DEV mirror remains Issue #35 and was not taken over.

## Commands and results

1. `python -m pytest -q tests/test_r3_issue41_effective_risk.py tests/test_r3_issue41_normalize_evidence.py tests/test_r3_issue41_bridge_discovery.py tests/test_r3_hard_adult_gate.py tests/test_r3_hard_adult_frozen_assets.py`
   - Result: `4 passed, 4 errors, 1 failed`.
   - Four errors are the known Windows pytest temp-directory `WinError 5` ACL failure.
   - The real frozen-assets test failed independently: `HAP-003` requires `anal object insertion`, absent from the 64-row challenge set.
2. `python -m translation_quarantine.r3.r3_issue41_pipeline .`
   - Result: exit 1; fail-closed at Hard Adult design validation with the same `HAP-003` error.
3. Post-gate components were run independently only to capture current repo evidence; this is not a pipeline PASS:
   - frozen-input normalization;
   - exact-canonical bridge discovery;
   - audited R3 run with the generated bridge requirements and no fabricated #32 snapshot;
   - effective-risk overlay.
4. `python translation_quarantine/r3/r3_verify.py --output translation_quarantine/r3 --rerun`
   - Result: exit 1 with `blind30 must contain exactly 30 selected rows`.
   - This is expected after the bridge gate: blind30 was not built.
5. `python -m pytest -q tests/test_stage0_integrity.py`
   - Result: `4 passed, 6 errors`; the errors are the same pytest temp-directory ACL failure.

## Current repo evidence

- Frozen fresh100: 100 rows; fixed membership/ordinals unchanged.
- Normalized input: 69 approved + 31 explicit REVIEW; 169 evidence rows.
- Exact generation-profile overlap: 7/100 (`bara`, `fishnets`, `loli`, `fellatio`, `pussy`, `anal`, `bound`).
- Generation profile rows: 2,788; SHA-256: `3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835`.
- #32 snapshot: not supplied/available. Bridge availability: `AVAILABLE=0`, `NOT_REQUIRED=93`, `BRIDGE_MISSING=7`, `BLOCKED_BRIDGE=0`.
- Effective-risk overrides: 15; counts `CRITICAL=41`, `HIGH_ANATOMY_ADULT=22`, `HIGH_POSE_ACTION=5`, `LOW=10`, `MEDIUM=22`.
- Effective-risk membership: unchanged.
- Blind30: `NOT_BUILT`, selected 0. No blind review was performed.
- Deterministic replay: not PASS; official verifier stopped because blind30 was not built.
- `production_modified=false`; `remaining_925_processed=false` in the regenerated R3 summary. No Stage10 production A/B was started.

## Boundary and unresolved items

- `data/**` has no Git diff. `CURRENT_STATE.md`, `CURRENT_DEV_TASK.md`, UI files, ranking logic, #32 verdict/candidate data, and main were not edited.
- Regenerated quarantine artifacts are limited to `translation_quarantine/r3/**`.
- The expected `issue41_normalization_summary.json` name from the execution-slot checklist is not emitted by the current normalizer; the current implementation emits `issue41_frozen_input_summary.json` instead.
- Final outcome is `HOLD_BRIDGE` / blocked before blind30, with an additional Hard Adult design validation defect. No production promotion is authorized.
