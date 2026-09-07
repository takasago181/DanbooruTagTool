# CODEX REQUEST — RULESET2 ACCEPTED DICTIONARY CHECKPOINT

## Authority

Implement **only** the accepted Ruleset2 dictionary/search/model-aux integration from this package into the existing DanbooruTagTool repository.

Current source of truth:
- `01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv`
- `37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv`
- `38_ALIAS_STATISTICS_POLICY_v3.0.csv`
- `39_ALIAS_TWO_AXIS_POLICY_v3.0.md`
- `06_SEMANTIC336_ROUTING_OVERLAY.csv`
- `31_METADATA_RULESET2_MIGRATIONS_v3.0.csv`
- `49_FINAL_INDEPENDENT_SEMANTIC_CONTENT_AUDIT_2026-09-07.md`
- governance: `00_GOVERNANCE_RULES_v2.md`

Candidate SHA-256:
`12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02`

Source ID+Tag identity SHA-256:
`b2f126ae9d49493034245fe006aad8eceb12eb2bf08a45160995b8da10b07763`

## Scope

1. Integrate the accepted 2788-row Special candidate without changing source ID+Tag identity.
2. Integrate Ruleset2 curated metadata and Japanese gloss/search derivation.
3. Replace legacy Alias safe/risk authority with the two-axis authorities:
   - semantic relationship = file 37
   - statistics eligibility = file 38
4. Keep `04_ALIAS_RISK_OVERLAY.csv` and `05_ALIAS_DEFAULT_STATS_SAFE.csv` compatibility/audit-only; they must not own Prompt routing or statistics policy.
5. Integrate Semantic336 typed routing while preserving semantic ownership vs auxiliary-anchor separation.
6. Integrate model-aux source handling according to `13_MODEL_AUX_FULL_CROSSMATCH_SPEC.md`.
7. Preserve local / deterministic / non-LLM / offline runtime.
8. Preserve migration/provenance traceability.

## Pilot001 freeze — DO NOT MUTATE

Stage8C Phase1 Pilot001 acceptance is **NOT COMPLETE** and is outside this implementation scope.
Its frozen acceptance baseline remains unchanged:
- target: 21 Specials / 2 FamilyRuleIds
- SUPPORT_DEFINED = 28
- UNRESOLVED = 1
- NO_SUGGESTION = 0
- UNREVIEWED = 2759
- Special Support rows 39 -> 50
- Family rows 0 -> 1
- GFR_SELF_ACTION: RULES_DEFINED 15/15
- GFR_MACHINE_STRUCTURED: NO_COMMON_RULE 6/6
- ID88 explicit `solo=CORE_SUPPORT` must outrank Family OPTIONAL
- ID311 `riding machine` remains UNRESOLVED / 0 rows
- ID312 existing 5 rows remain unchanged

Do not change those values to make tests pass. If the dictionary integration causes a conflict, stop and report it.

## Explicit prohibitions

- Do not start new Stage8C curation.
- Do not mark Pilot001 accepted.
- Do not start Stage9.
- Do not start Stage10.
- Do not apply to production outside the requested repository working tree.
- Do not silently replace Special Prompt ownership through alias/canonical/model-form data.
- Do not infer MODEL_OBSERVED from current e621/Gelbooru presence.
- Do not merge LoRA triggers/helpers into semantic truth.
- Do not restore older v2.6/v2.9 rules as authority.

## Required validation before handoff

Run and report, from the integrated repository:
1. all existing unit/integration tests relevant to Stage6/7/8
2. full pytest/test suite
3. source ID+Tag identity equality
4. 2788 Special row count
5. Alias total 778 and two-axis policy counts
6. Semantic336 count = 336
7. protected/frozen hash checks already present in repository
8. Stage6 parity
9. Stage7/8 regressions, including frozen Stage8C Phase0/Pilot001-related tests
10. deterministic build/output comparison where supported
11. runtime external/network calls = 0
12. any model-aux source retrieval/hash verification required by the canonical spec; if unavailable, stop that FINAL sub-gate explicitly rather than fabricating success

## Handoff requirements

Return a self-contained handoff package containing:
- exact changed-file list
- patch/diff summary
- commands executed
- test results and counts
- hashes of protected/current authoritative artifacts
- any unresolved failures or unavailable external-source evidence
- explicit statements:
  - `Pilot001 acceptance: NOT COMPLETE`
  - `Stage9: NOT STARTED`
  - `Stage10: NOT STARTED`
  - `production applied: false` unless the user explicitly changed this instruction

Stop after producing the handoff. Do not advance stages autonomously.
