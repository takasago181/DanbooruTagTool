# Special Core Dictionary — Reference Inventory

Date: 2026-09-10 JST
Baseline: `origin/main` at `38ed354` before Issue #43 edits
Scan: tracked files only, case-insensitive `Special2788|special2788`
Coverage: **95 paths / 316 matching lines**

This is a path/context inventory, not a blind replacement list. Each tracked
path containing a match is listed once under its primary action. A mixed path
explicitly separates its safe prose edit from retained technical references.
The three final counts are path/context records: **24 RENAME_NOW, 38
COMPATIBILITY_KEEP, 33 HISTORICAL_NEVER_REWRITE**.

## A. RENAME_NOW — 24 paths

| Path | Context | Classification | Action / reason |
|---|---|---|---|
| `danbooru_tag_tool/ui.py` | results frame label | A | Renamed current user-facing label to `Special Core Dictionary`; no runtime semantics changed. |
| `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md` | Special-first/product concept | A | Updated current spec prose; retained snapshot heading and manifest keys. |
| `docs/CORE_TAG_SET_SCHEMA.md` | Core source definition | A | Dictionary concept is now distinct from `Core Tag Set`; path identity retained in explanatory note. |
| `docs/EXISTING_TOOLS_POSITIONING.md` | product core list | A | Updated current product terminology. |
| `docs/FEATURE_PRIORITY.md` | v1 MUST item | A | Updated current product terminology. |
| `docs/FLOWCHARTS.md` | Core/Auxiliary flow label | A | Updated diagram concept label only. |
| `docs/GENERATION_JAPANESE_OVERLAY_SCHEMA.md` | presentation wording | A | Updated current architecture prose; data/runtime overlay unchanged. |
| `docs/GENERATION_PROFILE_SCHEMA.md` | profile title and concept prose | A | Updated title/prose; physical `special2788_*` path remains B. |
| `docs/GENERATION_PROFILE_V2_MIGRATION.md` | migration concept prose | A | Updated current migration wording; primary IDs unchanged. |
| `docs/PRODUCT_GOAL_LOCK.md` | product goal/main role | A | Updated current product terminology. |
| `docs/architecture/IMPLEMENTATION_BASELINE.md` | product purpose/table | A | Updated concept wording; protected path/hash rows remain B. |
| `docs/decisions/RECOMMENDATION_RANKING_DECISION.md` | current product-purpose paragraph | A | Updated terminology; ranking/statistics semantics unchanged. |
| `docs/project/CURRENT_DEV_TASK.md` | current DEV naming contract | A | Already synchronized to final name; no rewrite needed. |
| `docs/project/CURRENT_STATE.md` | current routing state | A | Already synchronized to final name; historical qualifiers retained. |
| `docs/project/DECISIONS.md` | current frozen concept reference | A | Updated wording while explicitly retaining physical identifiers. |
| `docs/project/PROMPT_USER_BURDEN_POLICY.md` | active policy wording | A | Already distinguishes formal name from historical corpus; no rewrite needed. |
| `docs/project/WORKSTREAMS.md` | active workstream and freeze wording | A | Updated current workstream terminology. |
| `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md` | active Stage9 concept statements | A | Updated concept statements; preserved `Special2788` snapshot qualifier. |
| `docs/stages/STAGE_10_PREP.md` | current Stage10-prep concept/HOLD wording | A | Updated downstream terminology; Stage10 remains unstarted. |
| `docs/stages/STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md` | PROMPT guidance | A | Updated concept guidance; physical prompt-reference paths remain B. |
| `docs/testing/ISSUE30_AUTOMATION_DRY_RUN_TASK_20260908.md` | #30 current boundary | A | Updated production-verdict wording; no automation behavior changed. |
| `docs/testing/ISSUE30_HUMAN_GOLDEN_LABEL_CONTACT_SHEET_TASK_20260908.md` | #30 HOLD condition | A | Updated freeze terminology; task remains paused. |
| `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md` | #30 representative design | A | Updated concept terminology; snapshot note retained. |
| `docs/testing/ISSUE30_VERDICT_ROUTING_GOLDEN_SET_TASK_20260908.md` | #30 routing limitation | A | Updated terminology; routing semantics unchanged. |

## B. COMPATIBILITY_KEEP — 38 paths

| Path | Context | Classification | Action / reason |
|---|---|---|---|
| `.gitignore` | protected data globs | B | Keep physical protected paths. |
| `AGENTS.md` | governance/invariant paths and product rules | B | Keep operational contract and protected identifiers. |
| `FILE_HASHES.json` | protected hash manifest paths | B | Never rename hash authority entries. |
| `PACKAGE_MANIFEST.json` | package purpose/path fields | B | Keep machine-readable manifest keys and paths. |
| `README_MANAGEMENT.md` | protected-data policy | B | Keep compatibility safety wording. |
| `danbooru_tag_tool/generation_profile.py` | loader/profile path | B | Keep runtime identifier/path. |
| `danbooru_tag_tool/knowledge.py` | source/linkage path | B | Keep runtime path. |
| `danbooru_tag_tool/ruleset2.py` | immutable source path | B | Keep authority path and technical wording. |
| `danbooru_tag_tool/search.py` | source-lane internal key | B | Keep serialized/internal `special2788` source key. |
| `data/semantic/semantic_support_profiles.csv` | 58 owner/source references | B | Data content and semantic identity are protected. |
| `data/special2788/prompt_reference/MANIFEST.txt` | reference manifest | B | Keep protected directory/file identity. |
| `data/special2788/prompt_reference/README.md` | reference corpus documentation | B | Keep snapshot/path identity. |
| `docs/CHATGPT_CODEX_HANDOFF.md` | protected handoff rules | B | Keep safety/path terminology. |
| `docs/decisions/PROFILE_PROMOTION_DECISION.md` | production profile technical references | B | Keep promotion evidence/path identity. |
| `docs/project/PERMANENT_RULES.md` | permanent protected-data rules | B | Keep operational and compatibility identifiers. |
| `docs/ruleset2/00_GOVERNANCE_RULES_v2.md` | source-term snapshot rule | B | Keep technical source snapshot term. |
| `docs/ruleset2/14_CODEX_REQUEST.md` | candidate path | B | Keep machine-readable/protected path. |
| `templates/BUILD_MANIFEST.template.json` | `special2788_version/hash` keys | B | Schema/serialized keys are intentionally unchanged. |
| `tests/test_e2e_functional.py` | protected paths | B | Tests must continue to validate existing identities. |
| `tests/test_final_spec.py` | historical/spec presence assertion | B | Keep compatibility expectation. |
| `tests/test_generation_profile.py` | profile/source constants | B | Keep runtime compatibility constants. |
| `tests/test_issue49_promotion.py` | #49 production target | B | Keep audit/replay path. |
| `tests/test_ruleset2_integration.py` | protected authority paths | B | Keep integrity tests. |
| `tests/test_stage0_integrity.py` | path-set/hash checks | B | Keep protected boundary. |
| `tests/test_stage3_knowledge.py` | derived linkage paths | B | Keep data identity. |
| `tests/test_stage7a_ui.py` | protected hashes | B | Keep integrity authority; UI text is separately tested. |
| `tests/test_stage8c_pilot001.py` | frozen manifest path | B | Keep evidence identity. |
| `tests/test_static_data.py` | protected source/linkage paths | B | Keep data identity. |
| `tools/apply_stage8c_pilot001.py` | evidence reference field | B | Keep serialized evidence identifier. |
| `tools/build_generation_profile_v2.py` | source/output paths | B | Keep production build compatibility. |
| `tools/build_runtime_index.py` | runtime hash/version keys | B | Keep machine-readable schema. |
| `tools/build_user_ranking_review.py` | source/reference paths and prose generator | B | Keep generated evidence and source identity. |
| `tools/issue49_promotion.py` | promotion target paths | B | Keep replayable promotion machinery. |
| `tools/model_aux_crossmatch.py` | optional source argument help | B | Keep tool compatibility. |
| `tools/stage5_post_audit.py` | protected directory scan | B | Keep audit boundary. |
| `tools/stage6_ranking_evaluation.py` | source path | B | Keep statistics input identity. |
| `tools/stage8a_verify.py` | protected paths/hashes | B | Keep verification authority. |
| `tools/stage8b_verify.py` | protected paths/hashes | B | Keep verification authority. |

## C. HISTORICAL_NEVER_REWRITE — 33 paths

| Path | Context | Classification | Action / reason |
|---|---|---|---|
| `FIRST_CODEX_REQUEST.txt` | original kickoff wording | C | Historical document; never rewrite. |
| `README_最初に読む.txt` | original reading guide | C | Historical guide; never rewrite. |
| `references/trial_v0.2_code/README_使い方.txt` | trial-era reference | C | Historical reference; never rewrite. |
| `references/legacy_prototype_code/QA_REPORT.md` | legacy QA evidence | C | Historical evidence; never rewrite. |
| `references/legacy_prototype_code/engine.py` | legacy code/path | C | Historical code; not production input. |
| `references/legacy_prototype_code/test_engine.py` | legacy test/schema | C | Historical code/evidence; never rewrite. |
| `docs/decisions/GENERATION_FAMILY_STRUCTURAL_AUDIT_v1.md` | audit report | C | Historical audit evidence; never rewrite. |
| `docs/issue49/applied_diff_report.json` | #49 applied evidence | C | Immutable promotion evidence. |
| `docs/issue49/effective_candidate_manifest.json` | #49 manifest | C | Immutable promotion evidence. |
| `docs/issue49/implementation_completion_report.md` | #49 completion report | C | Historical report; preserve exact snapshot wording. |
| `docs/issue49/protected_data_integrity.json` | #49 integrity evidence | C | Protected audit evidence; never rewrite. |
| `docs/ruleset2/49_FINAL_INDEPENDENT_SEMANTIC_CONTENT_AUDIT_2026-09-07.md` | final audit report | C | Historical audit evidence. |
| `docs/stage8c_finalization/00_START_HERE.md` | completed gate instructions | C | Historical stage record. |
| `docs/stage8c_finalization/EXIT_PILOT_MANIFEST.json` | frozen manifest | C | Immutable stage evidence. |
| `docs/stage8c_test_only_correction/STAGE8C_TEST_ONLY_CORRECTION_REQUEST.md` | completed correction request | C | Historical request. |
| `docs/stage9/STAGE9A_IMPLEMENTATION_REPORT.md` | Stage9A report | C | Historical implementation report. |
| `docs/stage9/STAGE9B_IMPLEMENTATION_REPORT.md` | Stage9B report | C | Historical implementation report. |
| `docs/stage9/STAGE9B_LATEST_MAIN_INTEGRATION_REPORT.md` | integration report | C | Historical integration evidence. |
| `docs/stage9/STAGE9C9D_IMPLEMENTATION_REPORT.md` | Stage9C/9D report | C | Historical implementation/evidence report. |
| `docs/stage_reports/GENERATION_PROFILE_PHASE1_REPORT.md` | phase report | C | Historical report. |
| `docs/stage_reports/GENERATION_PROFILE_V2_1_REPORT.md` | v2.1 report | C | Historical report. |
| `docs/stage_reports/GENERATION_PROFILE_V2_REPORT.md` | v2 report | C | Historical report. |
| `docs/stage_reports/ROOT_LAYOUT_REORGANIZATION_REPORT.md` | layout report | C | Historical report. |
| `docs/stage_reports/RULESET2_INTEGRATION_REPORT_2026-09-07.md` | integration report | C | Historical report. |
| `docs/stage_reports/STAGE6_5_JAPANESE_OVERLAY_REPORT.md` | overlay report | C | Historical report. |
| `docs/stage_reports/STAGE7A_SPECIAL_FIRST_UI_REPORT.md` | UI report | C | Historical report. |
| `docs/stage_reports/STAGE7B_RECOMMENDATION_UI_REPORT.md` | recommendation report | C | Historical report. |
| `docs/stage_reports/STAGE8A_V2_GENERATION_MEANING_REPORT.md` | meaning report | C | Historical report. |
| `docs/stage_reports/STAGE8B_SUPPORT_KNOWLEDGE_REPORT.md` | support report | C | Historical report. |
| `docs/stage_reports/STAGE8C_PHASE0_REPORT.md` | phase report | C | Historical report. |
| `docs/stage_reports/STAGE8C_PILOT001_IMPLEMENTATION_REPORT_2026-09-07.md` | pilot report | C | Historical report. |
| `docs/stage_reports/USER_RANKING_REVIEW.md` | saved ranking review | C | Historical saved evaluation evidence. |
| `docs/testing/issue28_full.json` | completed E2E evidence | C | Immutable test evidence. |

## Inventory conclusion

No unsafe rename was identified. All A records were limited to current prose or
the one user-facing label. All B records retain physical/runtime/schema/hash
compatibility. All C records remain byte-for-byte untouched as historical
evidence. No `data/**` content, canonical identity, or Stage9 behavior is part
of this naming migration.
