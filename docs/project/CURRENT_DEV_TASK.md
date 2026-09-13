# CURRENT DEV TASK — ISSUE #64 MIRROR

> This file mirrors Issue #64 only. Issue #66 remains open for post-#64 General integration and final v1 acceptance. Always read `CURRENT_STATE.md` first and then fetch the live Issue for the lane you are actually working on.

最終同期: 2026-09-13

## Source

- Source Issue: **#64**
- Issue title: **[GENERAL-DICT][UI-TAXONOMY][DEV] Practical genre browsing for 30,629 Japanese-overlay entries**
- Issue state: **OPEN / ACTIVE DEV**
- DEV state: **GENERAL_30629_PRACTICAL_TAXONOMY / FULL ROLLOUT CANDIDATE BUILD**
- Upstream #63: **ACCEPTED / MERGED / CLOSED**
- Parallel app lane #66: **PHASE B WPF BASELINE MERGED TO MAIN / OPEN FOR POST-#64 INTEGRATION + FINAL ACCEPTANCE**
- Stage10 #65: **PAUSED BY USER PRIORITY until practical v1 app baseline**

## Current continuation checkpoint

Latest durable recovery checkpoint at this sync:
- Issue #64 latest stop/checkpoint comment: **`5652768534`**
- Working branch: `chatgpt/issue64-full-rollout`
- Last fully verified formal checkpoint: **rows 1–13,400 / 30,629 (43.75%)**
- PROPOSED: **12,679**
- UNRESOLVED: **721**
- confidence: **11,516 HIGH / 1,163 MEDIUM / 721 LOW**
- remaining: **17,229**
- next unprocessed global row: **13,401**
- latest `PROGRESS.md` stop-record commit: **`02fe457139fe5dc04e8e4caaf9bfff1d8d9816eb`**
- accepted pilot basis: `PILOT_ACCEPTED` / commit `5064429018123c80c32ac41af715668fb67fb74e`

The attempted 13,401–14,400 continuation reached the execution/tool-context limit before a complete verified ledger could be finalized. No partial classifications from that attempt are official. Resume from **13,401** and again target a full 1,000-row run. Internal checkpoints are allowed, but do not end below 1,000 without a concrete allowed stop condition.

Branch recovery files:
1. `docs/issue64/full_rollout/PROTOCOL.md`
2. `docs/issue64/full_rollout/MANIFEST.json`
3. `docs/issue64/full_rollout/PROGRESS.md`
4. immutable batch ledgers under `docs/issue64/full_rollout/batches/`

If the live Issue/branch reports newer progress, the newer live checkpoint wins.

## Goal

Give the exact production Japanese-overlay population a shallow practical Japanese-first browse taxonomy so a beginner can discover useful General tags without already knowing their names.

## Target population

- exact production Japanese overlay promoted through #36/#55
- expected canonical population: **30,629**
- runtime overlay normally: local protected `data/runtime/japanese_overlay.json`
- do not expand to the full 100k+ Danbooru universe
- do not mutate the Japanese overlay to add taxonomy fields

## Architecture

Taxonomy must be a **separate read-only sidecar keyed by canonical tag**.

Fixed boundaries:
- taxonomy is UI/discovery index, not canonical semantic authority
- Japanese display/search data remains separate
- canonical English identity unchanged
- multi-path allowed where useful
- no runtime LLM dependency
- unresolved/ambiguous rows may remain explicit during development

Issue #66 Phase B WPF baseline is already merged to main and includes the General provider/UI boundary. #64 must continue producing only its accepted taxonomy sidecar/audit artifacts; do not implement or redesign the WPF UI here.

## Required process

Pilot is already accepted. Current work is the full candidate-build rollout under the accepted pilot-v2 taxonomy/boundaries.

1. Continue sequentially from the latest live checkpoint; do not restart persisted rows.
2. Current formal resume point is row **13,401** unless a newer live checkpoint exists.
3. Target a full **1,000-row** continuation per run. Internal durable checkpoints are allowed, but do not stop below 1,000 without a concrete allowed stop condition.
4. Preserve accepted 17 top-level practical genres and max path depth 2 unless a new explicit review decision changes them.
5. Keep no visible catch-all.
6. Prefer semantic/object identity over incidental substring matches.
7. Keep ambiguous proper names/events/projects opaque or uncertain cases explicit as `UNRESOLVED` rather than force-fitting them.
8. Persist row-level results durably on the working branch and do not overwrite past immutable batch ledgers.
9. Treat a batch as formal only when ledger, summary, `MANIFEST.json`, and `PROGRESS.md` agree and can be re-read from GitHub.
10. Keep canonical/Japanese overlay/Special production data unchanged during candidate build.
11. After all 30,629 candidate rows are complete, perform the required distribution/boundary/unresolved audit before production acceptance.

## Hard boundaries

- No Special taxonomy redesign (#56 completed).
- No retranslation of the 30,629 Japanese overlay.
- No Issue #66 WPF UI/search redesign inside #64.
- Do not consume or modify the merged WPF provider boundary from #64; #66 will integrate the accepted #64 output after acceptance.
- No automatic support insertion or Prompt optimization/rewrite.
- No generation-effectiveness implementation inside #64.
- No Stage10 learning work inside #64.
- No recommendation-score redesign.
- No full 11M-post/~3GB statistics index requirement.
- No full 100k+ Danbooru taxonomy expansion.
- No canonical identity mutation.
- No protected overlay mutation.

Retired Issues #34/#42 are historical only and must not be treated as future Gates.

## Acceptance / return contract

Completion must provide:
- task branch and final commit SHA
- exact target population/source reproduction evidence
- accepted taxonomy and final distribution
- full coverage / catch-all pressure / unresolved accounting
- boundary/error audit
- changed files
- tests and results
- protected/canonical data unchanged confirmation
- unresolved items and required review disposition

Do not self-merge.

## Post-#64 route

After accepted integration:

`#64 accepted -> #66 consumes General taxonomy through merged provider boundary -> #66 final app/search/UI acceptance -> Windows/portable acceptance -> practical v1 baseline -> Stage10 resume`
