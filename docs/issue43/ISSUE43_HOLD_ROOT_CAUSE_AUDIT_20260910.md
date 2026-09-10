# Issue #43 Root-Cause Audit — 2026-09-10

## Verdict

**PASS_ISSUE43_FREEZE**

Issue #43 caused blockers: **0**.

The audit separates the naming-only branch from pre-existing local protected-data
recovery differences, stale semantic fixtures, mutable documentation hashes, and
the machine's pytest temporary-directory ACL failure. No dictionary or production
profile content was changed.

## Scope and comparison

- Branch: `codex/issue43-special-core-dictionary`
- HEAD: `702b9ad9d317b617e383ab2f939eb2f046e29363`
- Parent: `38ed3547f8cc3d185ebcd227cc3d27d52781cd2a`
- Production profile SHA: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`

The parent-to-HEAD diff contains naming prose, the naming/freeze records and
their focused test, plus one UI label change (`Special2788` to `Special Core
Dictionary`). It contains no `data/**` change, no profile/dictionary change,
and no Stage9 implementation change. The seven failing existing test files and
all data/semantic fixtures they exercise are outside the Issue #43 diff. The
parent full suite was not run in a separate checkout because that checkout does
not contain the local protected-data snapshot; the unchanged test/data boundary
and the controlled rerun below provide the root-cause separation without
copying or replacing protected data.

## Full-suite classification

Initial same-environment run: **233 passed / 7 failed / 52 errors**.

With only pytest's basetemp redirected to a workspace-local temporary directory:
**285 passed / 7 failed / 0 errors**. Therefore all 52 errors are environment
ACL errors, not Issue #43 failures.

### 7 failed

| Test | Classification | Cause |
|---|---|---|
| `tests/test_stage0_integrity.py::test_protected_source_files_match_hash_manifest` | `PROTECTED_DATA_RECOVERY_RELATED` | Local `data/source/danbooru2026_clean.parquet` is present but absent from the older manifest path set. |
| `tests/test_stage8c_phase0.py::test_stage8b_resolver_and_accepted_stage8c_production_hashes_are_protected` | `PRE_EXISTING_BASELINE` | Existing semantic-support protected hash differs from the recorded baseline. |
| `tests/test_stage8c_phase0.py::test_family_rule_inventory_uses_production_ids_and_counts` | `TEST_FIXTURE_STALE` | Stage8C family-review counts do not match the current profile members. |
| `tests/test_stage8c_phase0.py::test_terminal_family_review_requires_all_members_and_reason` | `TEST_FIXTURE_STALE` | The stale family count fails before the intended terminal-reason assertion. |
| `tests/test_stage8c_pilot001.py::test_frozen_request_and_exact_family_membership` | `TEST_FIXTURE_STALE` | Frozen pilot membership is stale relative to the current profile members. |
| `tests/test_stage8c_pilot001.py::test_self_action_promoted_family_rule_and_explicit_precedence` | `TEST_FIXTURE_STALE` | Promoted applicability covers the stale member set, not the current set. |
| `tests/test_stage8c_pilot001.py::test_machine_has_no_common_or_generic_family_rule` | `TEST_FIXTURE_STALE` | The same stale family-review counts fail validation first. |

None of these tests or their relevant data files are modified by the Issue #43
parent-to-HEAD diff.

### 52 errors

All 52 are `ENVIRONMENT_ACL`. Every failure occurs during pytest `tmp_path`
fixture setup while scanning:
`C:\Users\takas\AppData\Local\Temp\pytest-of-takas` (`PermissionError`,
WinError 5). The same 52 tests ran past setup when `--basetemp` was set to a
workspace-local temporary directory.

The complete error population is:

- `tests/test_generation_profile.py`: `test_absent_empty_and_unknown_profile_are_left_joins`, `test_malformed_profiles_rejected[change0]` through `[change4]`, `test_audit_only_semantic_promotion_is_rejected`, `test_profile_columns_duplicates_and_tag_drift_rejected`, `test_family_and_observation_validation`, `test_v2_metadata_does_not_change_fixture_statistics[192]`, `[1578]`, `[1117]` (12)
- `tests/test_ruleset2_integration.py`: `test_model_aux_local_source_rules_and_final_gate` (1)
- `tests/test_stage0_integrity.py`: `test_protected_check_rejects_missing_modified_and_unexpected_sources[none]`, `[missing]`, `[size]`, `[hash]`, `[directory]`, `[extra]` (6)
- `tests/test_stage3_knowledge.py`: `test_semantic_rejects_invalid_rows[change0]` through `[change6]`, `test_semantic_duplicate_and_multiple_candidates`, `test_loaders_reject_corruption` (9)
- `tests/test_stage5_runtime_index.py`: `test_true_one_two_three_and_five_and_post_ids`, `test_empty_and_unknown_tag_handling`, `test_candidate_aggregation_input_exclusion_and_global_counts`, `test_snapshot_mismatch_and_corruption_are_rejected`, `test_manifest_snapshot_mixing_and_hash_corruption_are_rejected` (5)
- `tests/test_stage6_recommendations.py`: `test_raw_statistics_and_core_and_runtime_only_exclusion`, `test_drop_one_and_combination_specificity`, `test_alias_logical_merge_deduplicates_and_semantic_is_never_candidate` (3)
- `tests/test_stage8a_semantics.py`: `test_semantic_loader_rejects_invalid_role_and_duplicate_canonical`, `test_hint_loader_rejects_invalid_enums[role-SUBJECT_BASIC-NOT_A_ROLE-invalid semantic role]`, `test_hint_loader_rejects_invalid_enums[bucket-,common,-,sometimes,-invalid bucket]`, `test_hint_loader_rejects_invalid_enums[kind-,CORE_BASIS,-,NOT_A_KIND,-invalid hint kind]` (4)
- `tests/test_stage8b_support.py`: `test_special_profile_loader_rejects_invalid_identity_and_enums[special_id-999999-unknown special_id]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[candidate_canonical-not_a_real_canonical-unknown candidate canonical]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[support_slot-NOT_A_SLOT-invalid support_slot]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[support_class-NOT_A_CLASS-invalid support_class]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[intent_axis-NOT_AN_AXIS-invalid intent_axis]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[intent_direction-SIDEWAYS-invalid intent_direction]`, `test_special_profile_loader_rejects_invalid_identity_and_enums[combination_mode-MAGICAL-invalid combination_mode]`, `test_enabled_row_requires_support_class_and_duplicate_is_error`, `test_observed_evidence_requires_test_profile_and_model_scope[MODEL_OBSERVED]`, `test_observed_evidence_requires_test_profile_and_model_scope[USER_ENV_VERIFIED]`, `test_disabled_row_is_loaded_for_audit_but_hidden_at_runtime`, `test_family_loader_requires_existing_stage6_family` (12)

Total: **12 + 1 + 6 + 9 + 5 + 3 + 4 + 12 = 52**; every one had the same ACL root cause.

## FILE_HASHES.json — all 15 mismatches

| Path | Classification | Meaning |
|---|---|---|
| `AGENTS.md` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `requirements-dev.txt` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `README_最初に読む.txt` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `PACKAGE_MANIFEST.json` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `FIRST_CODEX_REQUEST.txt` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `docs/EXISTING_TOOLS_POSITIONING.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/PRODUCT_GOAL_LOCK.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/ARCHITECTURE_POLICY.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/CORE_TAG_SET_SCHEMA.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/FLOWCHARTS.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/AUXILIARY_TAG_ROLE_POLICY.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/FEATURE_PRIORITY.md` | `ISSUE43_CAUSED` (intentional mutable-doc change) | Naming prose changed as authorized; not protected data. |
| `docs/CHATGPT_CODEX_HANDOFF.md` | `PRE_EXISTING_BASELINE` | Existing local baseline mismatch; outside the Issue #43 diff. |
| `data/special2788/illustrious_tag_knowledge_base_2788_README.md` | `PROTECTED_DATA_RECOVERY_RELATED` | Protected `data/**` file differs from the recorded hash; it was not changed by Issue #43. |

The eight intentional documentation mismatches are not blockers because they
are the authorized naming migration itself. No protected dictionary/profile
hash is an Issue #43 mutation.

## Integrity rechecks

- Production profile: SHA unchanged; **2,788 rows / 2,788 unique SpecialID / order 1..2788 unchanged**.
- Special dictionary: **2,788 rows / 2,788 unique IDs**.
- #49 protected-after evidence: **24 checked / 0 mismatches**.
- Branch diff under `data/**`: **0 files**; semantic mutation: **0**.
- Stage9 behavior: **0**; the only code diff is a UI label string, with no Stage9 implementation change.
- Unsafe rename: **0**, per the complete reference inventory.
- `git diff --check`: **PASS**.
- Issue #43 focused/protected evidence supplied for the gate: **92 passed**; this audit reproduced the naming/protection subset as **7 passed**.

## Final basis

The naming migration is isolated to intentional prose/label/freeze artifacts.
The only full-suite failures are pre-existing protected-data baseline and stale
semantic-fixture conditions. The 52 setup errors disappear under a safe local
pytest temporary directory and are therefore environment ACL failures. No
Issue #43 caused blocker remains.
