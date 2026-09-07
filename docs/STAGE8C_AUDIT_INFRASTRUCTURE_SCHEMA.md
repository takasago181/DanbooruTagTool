# Stage 8C Phase 0 Audit Infrastructure

These files are audit-only. Runtime UI, SupportKnowledgeStore, Recommendation,
PromptSession, and Prompt formatting do not import them.

| File | Owner/key | Phase 0 content |
|---|---|---|
| `stage8c_review_status.csv` | original Special ID | 2,788 rows; Pilot 10 SUPPORT_DEFINED, 2,778 UNREVIEWED |
| `stage8c_family_rule_review.csv` | production FamilyRuleId | 25 inventory rows; two zero-member IDs are explicitly `NOT_APPLICABLE_NO_MEMBERS` |
| `stage8c_family_relation_proposals.csv` | stable proposal ID | header only; full pre-promotion family relation definition |
| `stage8c_family_candidate_applicability.csv` | proposal ID + member Special | header only |
| `stage8c_research_sources.csv` | stable source ID | package registry plus Stage 8B Pilot provenance |
| `stage8c_model_familiarity.csv` | model/version + canonical | header only; UNKNOWN is valid |
| `stage8c_non_tag_strategy.csv` | Special ID | header only |
| `stage10_test_slots.csv` | test profile + semantic slot | header only |
| `stage8c_practical_use.csv` | relation owner + candidate | header only |
| `stage8c_relation_evidence_events.csv` | stable evidence event ID | header only, append-only policy |

StaticFamily is an audit grouping loaded from the existing Promotion Plan. It
is not substituted for `FamilyRuleId`. Production family membership comes only
from each current Generation Profile `FamilyRuleId`.

An enabled family candidate may pass the applicability validator only when
every current member has exactly one recorded review with
`APPLIES_SAME_RELATION`. The review covers the full relation meaning: candidate,
slot, class, intent, combination, and reason semantics. A missing member or any
`DOES_NOT_APPLY`, `METADATA_DIFFERS`, or `UNRESOLVED` result blocks activation.
`UNIVERSAL_PASS` is impossible for a zero-member FamilyRuleId. A terminal
nonzero-member decision requires every member plus reason/evidence; a zero-member
terminal decision requires `NOT_APPLICABLE_NO_MEMBERS` and cannot own an enabled
family relation. The validator checks review completeness and contradiction; it
never infers semantic truth.

Evidence history is separate from the unique production relation definition.
Events retain model scope, test profile, seeds/condition hash, result reference,
positive through inconclusive effects, failures, and retraction/supersession.
Phase 0 leaves the production event ledger empty and emits a 39-row Stage 8B
Pilot dry-run preview under `benchmarks/stage8c`.

Practical-use and evidence records must reference an enabled production relation
or a structurally valid `DRAFT`, `READY_FOR_MEMBER_REVIEW`, or `UNIVERSAL_PASS`
family proposal. MODEL_OBSERVED and
USER_ENV_VERIFIED require reproducible test metadata and respectively a
CONTROLLED_TEST or USER_TEST source. A proposal-referenced evidence event records
its explicit `proposal_id`.

The primary generation-test scope is WAI-illustrious-SDXL v17 through Forge Neo.
Its exact training cutoff remains UNKNOWN. Upstream Illustrious or older NoobAI
dates cannot fill that value. Optional NoobAI comparison branches are recorded
separately as NoobAI XL 1.1 EPS and NoobAI XL V-Pred 1.0; neither is installed
or treated as an unqualified latest model. Semantic test slots preserve full Special coverage
when one concrete Prompt segment must be completed locally by the user.
