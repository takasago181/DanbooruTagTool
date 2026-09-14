# CURRENT DEV TASK — ISSUE #64 MIRROR

> This file mirrors Issue #64 only. Issue #66 remains open for post-#64 General integration and final v1 acceptance. Always read `CURRENT_STATE.md` first and then fetch the live Issue for the lane you are actually working on.

最終同期: 2026-09-14

## Source

- Source Issue: **#64**
- Issue title: **[GENERAL-DICT][UI-TAXONOMY][DEV] Practical genre browsing for 30,629 Japanese-overlay entries**
- Issue state: **OPEN / FINAL BOUNDED REVIEW COMPLETE / CLEAN CANDIDATE PENDING DEV REVIEW**
- DEV state: **GENERAL_30629_PRACTICAL_TAXONOMY / ACCEPT_FOR_PRODUCTION_INTEGRATION CANDIDATE**
- Upstream #63: **ACCEPTED / MERGED / CLOSED**
- Parallel app lane #66: **PHASE B WPF BASELINE MERGED TO MAIN / OPEN FOR POST-#64 INTEGRATION + FINAL ACCEPTANCE**
- Stage10 #65: **PAUSED BY USER PRIORITY until practical v1 app baseline**

## Current continuation checkpoint

Latest DEV review: Issue #64 comment **`5660957158`**. The full effective candidate and final bounded review are on:
- Rework branch: `codex/issue64-bounded-rework`
- Rework commit: **`7e10185a311ae8f0239cad0eb1bc879f7c69a2da`**
- Clean integration candidate: `codex/issue64-clean-integration-candidate`, based on live main **`3f4e47d7331809b2e6a234824799fb3bc179bae8`**

Effective state:
- population: **30,629 / 30,629**, exact ordered unique target
- PROPOSED: **28,226**
- UNRESOLVED: **2,403**
- confidence: **25,097 HIGH / 3,129 MEDIUM / 2,403 LOW**
- bounded residual candidates: **76 reviewed**, no full-population semantic reread
- final bounded verdict: **`ACCEPT_FOR_PRODUCTION_INTEGRATION`**

The candidate is pending DEV review. Issue #64 remains open; do not merge it or start #66 General integration until the clean candidate is accepted.

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

Issue #66 Phase B WPF baseline is already merged to main and includes the General provider/UI boundary. This candidate contains no #66 code; after DEV accepts it, #66 may consume the sidecar through that existing boundary.

## Required process

The 30,629-row effective candidate and bounded correction audit are complete. The final DEV-side verdict is `ACCEPT_FOR_PRODUCTION_INTEGRATION`; the clean candidate is awaiting DEV review.

1. Review branch `codex/issue64-clean-integration-candidate` against its declared live-main base.
2. Verify the candidate validator and provenance manifest.
3. Do not restart classification or perform a full-population semantic reread.
4. Do not merge, close Issue #64, or start #66 General integration before DEV accepts the clean candidate.
5. Preserve unresolved rows as explicit unresolved; do not add taxonomy nodes to force coverage.

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

After DEV accepts the clean candidate:

`#64 clean candidate accepted -> #66 consumes General taxonomy through the existing provider boundary -> #66 final app/search/UI acceptance -> practical v1 baseline -> Stage10 resume`
