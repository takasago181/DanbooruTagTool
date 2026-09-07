# Stage 8C Phase 0 Decision

## Decision

Create audit infrastructure before any production coverage expansion. Seed the
review ledger from original Special IDs, marking only the ten already enabled
Stage 8B Pilot profiles `SUPPORT_DEFINED`. Keep all other IDs `UNREVIEWED`.
Inventory production FamilyRuleIds independently. Leave nonempty families
`UNREVIEWED`; mark the two production zero-member IDs
`NOT_APPLICABLE_NO_MEMBERS` with membership evidence. This is an audit boundary,
not curation or a production Family Support rule.

Effective coverage is derived through the fixed Stage 8B resolver. It is never
entered into the review ledger. StaticFamily remains a 25-group planning view
from the existing static audit; FamilyRuleId membership comes only from the
current production Generation Profile.

Keep `semantic_support_profiles.csv` at 39 rows and
`family_support_rules.csv` header-only. Full family relation metadata is held
first in an audit-only proposal ledger; member applicability is keyed by proposal
ID and cannot be vacuously universal. The family applicability validator is
proven with synthetic fixtures and cannot activate a production rule. The
Stage 8B loader/resolver/relation model and UI remain byte-identical.

## External knowledge boundary

Register review sources for later curation while keeping runtime calls at zero.
Model familiarity, non-tag routing, semantic test slots, practical-use records,
and append-only evidence history receive validated schemas but no Phase 0
production assertions. Existing Forge Neo extensions retain their own duties;
none is reimplemented or invoked.

WAI-illustrious-SDXL v17 and Forge Neo are the primary future test scope. The
exact WAI v17 cutoff is UNKNOWN. Optional NoobAI references distinguish the EPS
1.1 and V-Pred 1.0 branches and are not installed. Model-family lineage and historical snapshots
remain secondary evidence and cannot overwrite current project canonical truth.

## Stop

This decision completes infrastructure only. It does not make Stage 8C FINAL,
start Family Rule review, curate the remaining 2,778 Specials, or start Stage 9
or Stage 10.
