# CURRENT DEV TASK — ISSUE #76 SPECIAL BROWSE V2 (ACTIVE / PRODUCTION IMPLEMENTATION)

最終同期: 2026-09-15

## Routing status

- **Issue #76 — Special browse taxonomy v2 final production implementation is active on this feature branch.**
- Implementation branch: `codex/issue76-special-v2-production`.
- Activation baseline: `24fafff4dbbef4a8cc81ac1f3e21c892b07a6d64`.
- Activation authority: latest Issue #76 comment `5678941812`.
- Integration: intentionally not performed; DEV review is the stop point.
- No successor Active DEV is designated after #76.
- #70, #64, #63, protected data, and canonical identity remain separate boundaries.

## Scope

Replace only the Special browse/navigation surface with the accepted v2 three-axis browse: `種類から探す`, `部位から探す`, and `テーマから探す`. Facets intersect with AND semantics while preserving existing search ranking/order and all existing Prompt/output/preset/Forge behavior.

## Safety boundaries

- Preserve the existing #56 Special v1 sidecar/evidence. Parse the accepted #76 evidence only at the explicit catalog-build boundary, then persist the resulting v2 mapping in `catalog.db`.
- Normal startup reads the precomputed `SpecialBrowseV2` classification from the catalog and does not parse or reconstruct the 2,788-row audit CSV overlay.
- Fixed-expanded axis headings are navigation labels only; only the Special root opens/closes. `1つ戻す` removes one latest facet condition and `全解除` clears v2 facets/history without changing an ordinary query.
- Preserve #72/#73/#74/#75/#77/#79/#80 behavior, including output-profile preview/copy equality and Forge bridge invariants.
- No new top-level folders, artifacts, WPF copy, #70/#64 data, taxonomy reclassification, canonical data, or protected data changes.

## Required validation

- Release build.
- All .NET tests.
- Focused #76 Special v2 navigation/overlay tests.
- #72/#73/#74/#75/#77/#79/#80 regression tests.
- `git diff --check`.
- Practical Windows/WQHD launch and Special v2 click-through where the environment permits.

## Completion

- DEV acceptance: pending DEV audit; report marker is `READY_FOR_DEV_AUDIT`.
- Main integration: not authorized for this implementation request; do not merge or close Issue #76.
