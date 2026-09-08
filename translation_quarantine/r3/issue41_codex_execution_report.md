# Issue #41 Pilot execution report — frozen #32 bridge v2 rerun

## Status

- This report supersedes the earlier pre-v2 `HOLD_BRIDGE` execution notes below the migration boundary.
- Branch: `ui-ja/issue41-pilot`.
- Migration checkpoint consumed: Issue #41 comment `5589236828`.
- Final one-shot Actions run: `34259612736`.
- Verified quarantine-output commit: `3c22bad` (`#41: rerun pilot with frozen Issue32 bridge v2`).
- Pipeline result: bridge gate `READY`; R3 bridge availability `AVAILABLE=7`; Issue #41 effective-risk blind30 `BUILT=30`.
- Deterministic Issue #41 replay: `PASS` with zero semantic-artifact mismatches.
- This is a quarantine/Pilot result only. It does not authorize Stage10 production A/B or a main merge.

## Frozen Issue #32 bridge v2 identity

Only the official v2 snapshot was consumed:

- owner branch: `dict-validation/quarantine`
- commit: `9f1659cfabb885b2dfc0dd4fef3a6611f19bee11`
- path: `validation_quarantine/bridge_snapshots/ui_ja_issue41_overlap7_v2.json`
- Git blob: `974bb9c971caf632f8ec73dff39fe4c55e60efaa`
- semantic content identity: `sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5`
- authoritative overlap order: `bara`, `fishnets`, `loli`, `fellatio`, `pussy`, `anal`, `bound`
- all 7 rows: `meaning_relevant_status=RESOLVED`, `conflict_signal=false`, frozen/pinned/immutable
- v1 remains historical / `NOT_CONSUMABLE`.

The v2 content identity is not a raw-file SHA-256. The snapshot contract defines it as SHA-256 over canonical JSON of the ordered row identities. Each row's `meaning_fingerprint` is independently verified as SHA-256 over its exact `translation_visible_semantics` object.

## Consumer compatibility fixes made in Issue #41 scope

The first fail-closed reruns exposed two legacy consumer assumptions; neither was solved by weakening the gate.

1. `r3_issue41_bridge_status.py` assumed the #32 snapshot was JSONL. The official v2 is one JSON object containing a `rows` array. The reader now accepts the official object contract while preserving legacy JSONL fixture support, and malformed JSON/object structure still fails closed.
2. Base R3 meaning validation only understood the older `translation_visible_propositions` projection and unprefixed hash. The official v2 uses exact `translation_visible_semantics` and `sha256:`-prefixed fingerprints. `r3_common.py` now has a native v2 branch while leaving the legacy projection/hash path unchanged. `conflict_signal` is also consumed as an explicit bridge conflict signal.
3. The #39 deterministic verifier validates base-R3 blind artifacts, not Issue #41's effective-risk blind artifacts. A dedicated `r3_issue41_verify.py` now verifies the frozen v2 contract, bridge rows, masked Issue #41 blind30, protected boundaries, and replays the full Issue #41 pipeline twice.

Focused regression coverage added for the v2 JSON object reader, malformed-object fail-closed behavior, native v2 proposition/fingerprint handling, and explicit `conflict_signal` handling.

## Final clean rerun results

The final run started from a clean checkout of committed #41 code; no runtime source patch was used.

1. Exact snapshot validation
   - commit: PASS
   - Git blob: PASS
   - top-level semantic content identity: PASS
   - row meaning fingerprints: 7/7 PASS
   - status: 7/7 RESOLVED
   - conflict: 0/7
   - frozen/pinned/immutable: 7/7
2. Focused tests
   - `tests/test_r3_issue41_bridge_status.py`
   - `tests/test_r3_issue41_v2_contract.py`
   - result: `8 passed`
3. Issue #41 pipeline
   - schema: `issue41-pipeline-2`
   - fixed pilot membership: 100
   - normalized input: 69 approved + 31 explicit REVIEW = 169 evidence rows
   - current generation-profile rows: 2,788
   - current exact overlap: 7/100, matching the frozen v2 canonical set
   - current bridge-discovery generation-profile SHA-256: `8771d72738187d16235d33fb99d484b8e6d243b756a775fd5a04cb6970f3d60b`
   - Hard Adult design: `ok=true`, 64 challenge rows + 16 ambiguity probes
   - effective-risk overrides: 15; membership unchanged
   - effective-risk counts: `CRITICAL=41`, `HIGH_ANATOMY_ADULT=22`, `HIGH_POSE_ACTION=5`, `MEDIUM=22`, `LOW=10`
   - bridge status guard: `READY`, required=7, resolved=7, blocked=0
   - R3 bridge availability: `AVAILABLE=7`, `NOT_REQUIRED=93`, blocked=0
   - blind30: `BUILT`, selected=30
4. Deterministic replay verifier
   - original vs rerun1: PASS
   - rerun1 vs rerun2: PASS
   - original vs rerun2: PASS
   - mismatches: none
   - verifier result: `ok=true`, `deterministic_rerun_verification=PASS`

## Protected boundaries

The verified run reports and checks:

- `production_modified=false`
- `remaining_925_processed=false`
- `stage10_production_ab_started=false`
- no production `data/**` write
- no #32 verdict/candidate mutation
- no #35 UI change
- no `CURRENT_DEV_TASK.md` takeover
- no main merge

All generated execution evidence remains under `translation_quarantine/r3/**` on the Issue #41 branch.

## D-012 / denominator note

The current 2,788 Special rows remain the running-audit fixed denominator, not a permanent final-count promise. After #32 completes and before final freeze, completeness reconciliation must still check for genuine missing Special rows. Any genuine misses are handled as a delta audit; the existing 2,788 are not restarted.

## Current handoff state

The old `HOLD_BRIDGE` blocker is resolved for this Pilot input. The frozen v2 snapshot is consumed successfully, the 30-row masked Issue #41 blind package exists, and the complete Issue #41 generation path is deterministic under replay. Any next gate must consume these verified quarantine artifacts without weakening the bridge contract or crossing the protected production boundaries above.
