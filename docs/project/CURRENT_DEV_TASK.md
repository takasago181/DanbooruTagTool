# CURRENT DEV TASK — ISSUE #66 MIRROR

> This file mirrors the current #66 DEV lane only. Always read `CURRENT_STATE.md` first, then fetch the live Issue and latest DEV comment. Issue #64 taxonomy is accepted and integrated; its remaining WPF consumption belongs to #66.

最終同期: 2026-09-14

## Source

- Source Issue: **#66**
- Issue title: **[V1-APP][UI][PARALLEL-WITH-64] Beginner-first app completion and UI integration**
- Issue state: **OPEN / ACTIVE DEV**
- Current DEV state: **ACCEPTED GENERAL TAXONOMY INTEGRATION + FINAL PRACTICAL-V1 ACCEPTANCE**
- WPF Phase B baseline: accepted and merged at `837d08f259c52811ec7a97ae6235cd22e4e2d35c`
- UX Refinement Passes 1/2: accepted and merged at `3f4e47d7331809b2e6a234824799fb3bc179bae8`
- Accepted #64 production taxonomy: fast-forwarded to main at `d69e8b06916b637efd03c05b820ad13dd05e8ec1`
- Stage10 #65: **PAUSED BY USER PRIORITY until practical v1 app baseline**

## Current continuation checkpoint

Latest #66 DEV review: comment **`5659601590`** accepted the clean UX integration candidate. The reviewed WPF UX is now in main. The latest #64 acceptance comment **`5661435196`** accepted the General production sidecar and authorized its fast-forward; that candidate is now in main.

Accepted General production evidence:
- population: **30,629 / 30,629**, ordered and unique
- PROPOSED: **28,226** / UNRESOLVED: **2,403**
- effective sidecar SHA-256: `a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9`
- taxonomy SHA-256: `7311fa1bf1523fcd83134c975b579289d7dbc8aa4cdb1313952d906fc2beb70f`
- canonical sequence SHA-256: `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b`
- post-merge validator: PASS; focused test: **1 passed**; `git diff --check`: PASS

The current management sync only changes routing documents. It does not implement General browse or modify taxonomy rows.

## Goal

Complete the beginner-first v1 flow:

`既存Promptを理解 -> 日本語/英語で検索・browse -> 自分で選択/編集 -> canonical-English Promptを出力`

The WPF app must consume the accepted General taxonomy without changing canonical identity or Japanese overlay semantics.

## Next #66 work

1. Inspect the merged General sidecar and the existing `IGeneralBrowseProvider` / catalog importer boundary.
2. Integrate only the accepted sidecar into the rebuildable product catalog and expose shallow practical General browse through the existing provider/UI architecture.
3. Keep unresolved rows explicit and non-browsable; do not invent a catch-all or new taxonomy.
4. Rebuild/refresh the catalog through an explicit import/build operation, not routine app startup.
5. Add focused tests for General provider/catalog browse and rerun Japanese, English, mixed-search, and existing Prompt regressions.
6. Complete practical Windows acceptance for General browse, Prompt editing, visible English preview/copy, persistence, and recovery.

## Fixed product and data boundaries

- Keep Japanese display/search overlay separate from taxonomy sidecar.
- Do not edit or reclassify the accepted #64 taxonomy.
- Do not alter canonical identity, Special #56 data, #63 product-fit data, protected/source data, or unrelated legacy assets.
- Do not integrate any unaccepted taxonomy candidate.
- Do not add hidden Prompt insertion, optimization, conflict removal, or model rewrite.
- Preserve Prompt order, raw surface, duplicates, and visible-state = copied-Prompt behavior.
- Keep the existing App/Core/Data boundaries and General provider contract.
- Portable packaging is optional and is not a practical-v1 completion Gate.
- Stage10 #65 remains paused until practical v1 acceptance.

## Final practical-v1 acceptance

Complete when:
- existing Prompt can be loaded and understood without destructive rewriting;
- Japanese, English, and mixed search are usable with strong intent ahead of incidental substring/fuzzy matches;
- Special browse and accepted General browse are usable;
- explicit add/remove/reorder/multi-select/Undo/Redo work in practical Windows use;
- copied Prompt matches the visible explicit workspace;
- unknown/raw surfaces and imported duplicates remain preserved unless explicitly edited;
- focused/regression tests pass or known debt is clearly separated;
- final Windows interaction acceptance passes;
- protected/canonical data remains unchanged.

## Stop / handoff

Do not begin Stage10 or unrelated cleanup as part of #66. After General integration and final practical-v1 acceptance evidence is complete, return branch/commit, changed files, tests, Windows evidence, protected-data impact, and unresolved items for DEV review. Do not self-merge or close #66.
