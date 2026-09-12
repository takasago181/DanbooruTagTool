# CURRENT DEV TASK — ISSUE #64 MIRROR

> The live GitHub Issue is the executable task authority. Read `CURRENT_STATE.md`, then fetch Issue #64 and its latest checkpoint before implementation. If this mirror differs from the live Issue, fail closed and do not guess from chat history.

最終同期: 2026-09-12

## Source

- Source Issue: **#64**
- Issue title: **[GENERAL-DICT][UI-TAXONOMY][DEV] Practical genre browsing for 30,629 Japanese-overlay entries**
- Issue state: **OPEN / CURRENT CORE DEV**
- DEV state: **GENERAL_30629_PRACTICAL_TAXONOMY**
- Upstream #63: **ACCEPTED / MERGED / CLOSED**
- Stage10 production A/B: **NOT A v1 BLOCKER / NOT STARTED**

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

Do not classify all 30,629 blindly in one pass.

1. Reproduce/materialize the exact target population.
2. Inspect distribution and representative samples across high-usage, ordinary, rare, compound and ambiguous tags.
3. Propose/freeze a small practical taxonomy based on user discovery value, not ontology purity.
4. Run a reproducible pilot.
5. Audit boundary/error patterns.
6. Stop for DEV/AUDIT pilot acceptance.
7. Expand to all 30,629 only after pilot acceptance.
8. Validate 30,629/30,629 reachability or explicit unresolved accounting.

Initial top-level genre candidates from the live Issue are suggestions, not frozen truth. Merge/split/rename them if real data shows a better practical structure.

## Product behavior target

Examples:

`General -> 構図・画角 -> ...`

`General -> 表情・感情 -> ...`

Visible identity remains Japanese-first + canonical English. Final Prompt payload remains canonical English.

## Hard boundaries

- No Special taxonomy redesign (#56 completed).
- No retranslation of the 30,629 Japanese overlay.
- No #34 bilingual ranking redesign.
- No #42 broad v1 UI/product-scope implementation.
- No automatic support insertion or Prompt optimization/rewrite.
- No generation-effectiveness / Stage10 work.
- No recommendation-score redesign.
- No full 11M-post/~3GB statistics index requirement.
- No full 100k+ Danbooru taxonomy expansion.
- No canonical identity mutation.
- No protected overlay mutation.

## Acceptance / return contract

Implementation must provide:
- task branch and commit SHA
- exact target population/source reproduction evidence
- proposed/frozen taxonomy and rationale
- pilot selection/method/results
- taxonomy distribution / catch-all pressure / unresolved counts
- changed files
- tests and results
- protected/canonical data unchanged confirmation
- unresolved items

Codex/implementation work must stop for DEV/AUDIT before merge. Do not self-merge.

## Post-#64 route

After accepted integration:

`#64 -> #34 bilingual search relevance/noise -> #42 v1 scope lock -> v1 UI integration / Windows acceptance`

Issue #5 / Stage10 is a future generation-effectiveness lane only if an adopted feature later requires empirical image evidence.
