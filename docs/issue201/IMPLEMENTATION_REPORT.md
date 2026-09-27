# Issue #201 implementation and DEV/AUDIT handoff

## Scope and decision

Work was based on freshly fetched `origin/main` **`ade6f12e8d12709090a31d2caeb65e86016e5e14`**. The #132 final semantic ledger was read as immutable comparison provenance; no research branch was used as an implementation base, merged, or cherry-picked.

The live #64/#76 route projections already cover every accepted owner path tested here. The compared #132 semantic alternatives span unrelated owners and carry real false-positive risk, so no production taxonomy/catalog change met the Issue #201 systemic-fix bar. This change adds reproducible practical scenario coverage and updates project routing/state to hand those semantic clusters to DEV/AUDIT for authority decisions. It intentionally adds no per-row overlays, regex classifier, new index, or runtime dependency.

## A — #64 color / pattern

- Accepted #64 `COLOR_APPEARANCE`: 682 identities; current `COLOR_PATTERN_SHAPE` projection: 682; accepted-owner projection omissions: **0**.
- Against the independent #132 final semantic ledger: 1,188 expected color membership pairs are absent from the current route; 275 current color memberships are not reproduced by that ledger. These are two-way review deltas, not eligible row-level additions.
- The semantic candidates cross clothing, body, hair/face, objects, living nature, background, quality/style and text/symbol owners. Samples such as `above_clouds` and `american_flag` show why a color-name or broad owner rule risks unrelated results. No single owner correction was demonstrated to improve image-intent discovery without that risk.

## B — LIVING / NONHUMAN_TRANSFORM boundary

- Accepted #64 LIVING paths: 1,330; current LIVING projection: 1,330; owner projection omissions: **0**.
- The General taxonomy has no `NONHUMAN_TRANSFORM` genre; that route currently comes from Special #76. In comparison with #132 combined semantic routes, the discrepancy is 1,561 identity/route pairs: audit-expected but current-missing NONHUMAN 887; current NONHUMAN not in audit 54; audit-expected but current-missing LIVING 445; current LIVING not in audit 401.
- The disagreements span body parts, people, actions, living concepts, clothing, and transformation terms. No supported shared boundary rule can be applied without changing the accepted #64 or #76 semantics. Left for owner-level DEV/AUDIT review.

## C — local refinements and unreproduced routes

- Current route memberships not reproduced by the #132 ledger: 7,819 pairs / 7,593 identities.
- #132 route memberships missing from current production: 8,983 pairs / 8,398 identities.
- The accepted #64 local path projection has **0** missing local projections. The independent ledger has 6,433 local membership pairs / 6,252 identities not in the current local projection, spanning CLOTHING 2,670, OBJECT_PROP 1,645, ACTION_CONTACT 1,039, TEXT_SYMBOL 502, LIVING_NATURE 276, CLOTHING_STATE_EXPOSURE 258, EXPRESSION_EMOTION 32, and GAZE_ORIENTATION 11.
- This distribution does not identify one broken projection owner. Bulk addition/removal would change broad semantic categories, so it was not adopted.

## Practical image-intent scenario QA

Added `Issue201PracticalScenarioTests`, an opt-in gate against the isolated 124,895-row candidate catalog and the same `RuntimeCatalogIndex` / `UnifiedBrowseIndex` / Special Browse V2 composition used by production. The 12 test cases begin with descriptions of the image intent, apply the ordinary visible facets and content intent, inspect actual result examples, and require expected canonical identities. Japanese, English, and mixed searches for `striped_underwear` are also checked.

| Scenario | Intent and filters | Browse / search | Expected canonical identities reached |
|---|---|---:|---|
| Sexual breast + pose | `胸`; BREAST_NIPPLE + POSE_POSITION | 10 / 8 | `sideways_perpendicular_paizuri` |
| Sexual buttock + oral contact | `肛門 舐める`; BUTTOCK_ANAL + ACTION_CONTACT | 63 / 1 | `anilingus`, `ass-to-mouth` |
| Sexual mouth + action | `口`; MOUTH_ORAL + ACTION_CONTACT | 89 / 38 | `fellatio`, `cunnilingus` |
| Sexual female genital + pose | `女性器`; FEMALE_GENITAL + POSE_POSITION | 3 / 3 | `presenting_own_pussy` |
| Sexual male genital + action | `男性器`; MALE_GENITAL + ACTION_CONTACT | 113 / 1 | `fellatio`, `handjob` |
| Sexual BDSM/restraint + body/action | `拘束`; BDSM_RESTRAINT + ACTION_CONTACT | 163 / 55 | `bondage`, `bound_arms` |
| Sexual reproduction/pregnancy/lactation | `授乳`; REPRO_PREGNANCY_LACTATION | 28 / 5 | `breastfeeding`, `self_milking` |
| Sexual clothing/exposure + color/pattern | `縞模様の下着`; CLOTHING_EXPOSURE | 1,162 / 1 | `striped_underwear` |
| Sexual nonhuman/transform + body/action | `触手`; NONHUMAN_TRANSFORM | 52 / 20 | `tentacle_sex` |
| Sexual composition/camera | `胸元 構図`; COMPOSITION_CAMERA | 18 / 1 | `breast_focus`, `pov_breasts` |
| General-purpose contextual clothing | `縞模様の下着`; CLOTHING_EXPOSURE | 8,673 / 1 | `striped_underwear` |
| General-purpose contextual action | `手を置く`; ACTION_CONTACT / INTERACTION | 2,041 / 29 | `hand_on_another's_head` |

All expected identities were present. Reviewed examples were directly related to the intent; some scenarios intentionally have broad result totals because the visible facet returns a route/facet intersection. The isolated output report is `.audit/issue201/scenario-final.json` (workspace-only evidence).

Before/after examples are unchanged because no accepted systemic data edit was justified: `胸` + sexual + BREAST_NIPPLE + POSE_POSITION still reaches `sideways_perpendicular_paizuri`; `縞模様の下着` reaches `striped_underwear` in both Sexual and General Purpose. Japanese, English, and mixed searches each reach the canonical `striped_underwear` identity. This gate records existing practical paths and protects them while owner-level semantic decisions remain open; it does not claim a catalog discoverability delta.

## Catalog, regression, performance, and safety

- Protected source inputs were read from `C:\Codex\DanbooruTagTool`; all import-report source hashes matched the current protected-input records. Candidate outputs were written only under `.audit/issue201/` in this worktree.
- Baseline and candidate catalog: 124,895 rows; 131,072,000 bytes each; SHA-256 for both: `5759156ff79d794ddc70dd5459af9b80f8cb204c4527be16fd368ff40be9f141`. Catalog delta: **0 bytes / 0 rows / byte-identical**.
- General taxonomy: 30,629 identities; Proposed 28,226; browse-eligible 28,222. General body/theme facets: 346 identities / 355 assignments (BODY 247, THEME 108).
- Release solution build: PASS, 0 warnings / 0 errors. Full suite: PASS, 217 passed / 18 skipped / 0 failed. Focused #199 + #118 + #132 route regression: PASS, 15 passed / 2 skipped / 0 failed. Isolated production catalog/source-integrity + practical scenarios: PASS, 5 passed / 0 failed. Skipped tests are opt-in gates requiring separate protected staging/authority inputs.
- Issue #199 isolated performance gate (3 alternating measurements per side): no blocked search/Browse/memory gates; catalog bytes and retained managed memory unchanged. Open 1,098.6 → 1,117.3 ms; UnifiedBrowseIndex build 79.7 → 72.2 ms; index allocation 78,308,680 bytes both; index retained 22,410,560 bytes both; combined retained 199,935,856 bytes both. English/Japanese/mixed search increases were +2.15% / +1.59% / +1.43%; Browse medians remained 0.53–1.00 ms with body/theme and Sexual/General-purpose facet combinations within 2.8% of baseline.
- Canonical identities, canonical-English Prompt output, #118 content intent, #76 Special semantics, #199 General body/theme assignments, UnifiedBrowseIndex, DeepOnly, and explicit selection are preserved: production/Core/Data source code and catalog payload are unchanged; #199/#118/#132 focused regressions passed; scenario test exercises the existing index and content-intent filters.
- No production runtime or UserData operation was performed. Production/UserData state is therefore untouched by this work.

## DEV/AUDIT decision requested

Review the A/B/C semantic discrepancy clusters as owner-level proposals, especially the broad color/pattern owner boundaries, General-vs-Special LIVING/NONHUMAN scope, and high-volume CLOTHING / OBJECT_PROP / ACTION_CONTACT local refinements. Counts above are diagnostics, not row-fix targets. This branch does not merge to main or apply to production.
