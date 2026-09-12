# CURRENT DEV TASK — ISSUE #64 MIRROR

> This file mirrors Issue #64 only. The project currently has a second active DEV lane, Issue #66, for app/search/UI completion. Always read `CURRENT_STATE.md` first and then fetch the live Issue for the lane you are actually working on.

最終同期: 2026-09-13

## Source

- Source Issue: **#64**
- Issue title: **[GENERAL-DICT][UI-TAXONOMY][DEV] Practical genre browsing for 30,629 Japanese-overlay entries**
- Issue state: **OPEN / ACTIVE PARALLEL DEV**
- DEV state: **GENERAL_30629_PRACTICAL_TAXONOMY / FULL ROLLOUT CANDIDATE BUILD**
- Upstream #63: **ACCEPTED / MERGED / CLOSED**
- Parallel app lane: **#66 ACTIVE**
- Stage10 #65: **PAUSED BY USER PRIORITY until practical v1 app baseline**

## Current continuation checkpoint

Latest durable recovery checkpoint at this sync:
- Issue #64 checkpoint: **comment `5647331312`**
- Working branch: `chatgpt/issue64-full-rollout`
- Branch HEAD at checkpoint: `9683e4fe6ac035c601d545813c84deffdc187c3d`
- Accepted pilot basis: `PILOT_ACCEPTED` / commit `5064429018123c80c32ac41af715668fb67fb74e`
- Completed sequential rows: **5,300 / 30,629 (17.30%)**
- Cumulative: **5,153 PROPOSED / 147 UNRESOLVED**
- Remaining: **25,329**
- Next unprocessed global row: **5,301**

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

## Required process

Pilot is already accepted. Current work is the full candidate-build rollout under the accepted pilot-v2 taxonomy/boundaries.

1. Continue sequentially from the latest live checkpoint; do not restart persisted rows.
2. Preserve accepted 17 top-level practical genres and max path depth 2 unless a new explicit review decision changes them.
3. Keep no visible catch-all.
4. Prefer semantic/object identity over incidental substring matches.
5. Keep ambiguous proper names/events/projects explicit as `UNRESOLVED` rather than force-fitting them.
6. Persist row-level results durably on the working branch and do not overwrite past immutable batch ledgers.
7. Keep canonical/Japanese overlay/Special production data unchanged during candidate build.
8. After all 30,629 candidate rows are complete, perform the required distribution/boundary/unresolved audit before production acceptance.

## Hard boundaries

- No Special taxonomy redesign (#56 completed).
- No retranslation of the 30,629 Japanese overlay.
- No Issue #66 UI/search implementation inside #64.
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

`#64 accepted -> #66 consumes General taxonomy -> #66 final app/search/UI acceptance -> Windows acceptance -> v1 baseline`

Issue #66 may continue dependency-independent UI/search work in parallel while #64 is running.
