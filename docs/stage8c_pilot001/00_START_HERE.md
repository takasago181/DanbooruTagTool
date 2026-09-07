# DanbooruTagTool — Stage8C Phase1 Pilot001 implementation request
Date: 2026-09-07

## Current authoritative state

Ruleset2 dictionary/search/model-aux integration has completed its Codex implementation handoff and ChatGPT independent inspection found no blocking contradiction in the supplied delta package.

This package now opens **only Stage8C Phase1 Pilot001 implementation**.

Do not reopen the Ruleset2 dictionary content audit.
Do not redesign Stage8C Phase0.
Do not start Stage9 or Stage10.
Do not mark production applied beyond the Pilot001 relations explicitly accepted by this request.

The nested `CHATGPT_HANDOFF_RULESET2_INTEGRATED.zip` is the immediately preceding integration handoff and must be treated as the current implementation context, not as permission to alter its frozen authorities.

## Frozen Pilot001 scope

Target: exactly 21 Specials across 2 FamilyRuleIds.

### GFR_SELF_ACTION
- 15 members
- Family proposal ID: `FRP_P1_SELF_ACTION_SOLO_V1`
- candidate: `solo`
- support_slot: `SUBJECT_BASIC`
- support_class: `OPTIONAL_VARIATION`
- priority: `10`
- intent: `COMPOSITION / NEUTRAL`
- combination: `CONTEXTUAL`
- evidence boundary: `SEMANTIC_CURATED / NOT_TESTED`
- expected family review result: `RULES_DEFINED 15/15`
- ID88 `masturbation` already has explicit `solo=CORE_SUPPORT`; explicit relation must continue to win over the Family OPTIONAL relation.

### GFR_MACHINE_STRUCTURED
- 6 members
- Family review result intentionally: `NO_COMMON_RULE 6/6`
- Do not add generic `machine` or `sex_toy` merely to increase coverage.

Special-specific expected relations:
- ID310 `milking machine`: 2 rows
- ID311 `riding machine`: `UNRESOLVED`, 0 rows
- ID312 `sex machine`: existing 5 rows unchanged
- ID313 `sybian`: 4 rows
- ID314 `robot sex`: 3 rows
- ID1159 `bead sex machine`: 2 rows

## Frozen expected post-application state

These are acceptance expectations, **not quotas to force**:
- SUPPORT_DEFINED = 28
- UNRESOLVED = 1
- NO_SUGGESTION = 0
- UNREVIEWED = 2759
- Special Support rows: 39 -> 50
- Family Support relation rows: 0 -> 1

If semantic implementation naturally produces different counts, STOP and report the discrepancy. Do not pad or mutate unrelated Specials to make the numbers match.

## Required invariants

- Preserve all 2,788 Special identities.
- Preserve Ruleset2 Candidate, Alias two-axis authorities, Semantic336 ownership/routing, and source hashes.
- Preserve Stage8B explicit-over-Family precedence.
- ID88 explicit CORE_SUPPORT must beat Family OPTIONAL_VARIATION.
- ID311 stays unresolved with zero support rows.
- ID312 existing five rows stay byte/semantic-equivalent unless serialization metadata necessarily changes; no relation content change.
- Do not create a common MACHINE_STRUCTURED family rule.
- No unrelated review-state changes.
- No Stage9/Stage10 work.
- Runtime remains local, deterministic, non-LLM, offline.

Read `14_CODEX_REQUEST_STAGE8C_PILOT001.md` for the exact implementation and validation requirements.
