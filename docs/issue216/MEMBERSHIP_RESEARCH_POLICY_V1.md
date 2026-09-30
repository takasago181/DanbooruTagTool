# Issue #216 semantic-membership and Browse HOME policy

Status: execution policy for the additive Issue #216 coverage lane. The frozen cohort, HOME cardinality, root validation, and #180 baseline are unchanged. Issue #216 selects a **Browse HOME**: the single existing canonical Copyright root that makes an exact Character easiest to find with the least semantic confusion. This does not assert exclusive legal ownership or enumerate every appearance.

## Browse HOME priority (2026-09-30)

When exact accepted membership evidence supports multiple roots, select only from explicit, source-backed priority metadata on each exact source/member row (`browse_home_tier` and `browse_home_basis`):

1. Clear original work / IP root.
2. Independent Character brand or Character series root.
3. Officially established origin ecosystem (for example UTAU, VOCALOID, VOICEROID, CeVIO, or Synthesizer V), when the source establishes origin or primary identity rather than later product availability alone.
4. Stable official company or brand mascot root.

Priority values are 1–4 in that order. Tier `5` records a verified secondary product association that is retained as membership context but is not Browse HOME authority by itself. Each candidate root needs an exact accepted member mapping, an existing canonical Copyright root, an explicit tier, and a recorded basis. A unique higher-priority root may be selected. Same-tier validated roots, missing/contradictory priority evidence, or unresolved source scope stay in review/conflict. Candidate hints never set priority or HOME.

The mere existence of the same Character in several voice products is not a block. Later products remain membership/context; only a documented primary origin or independent brand root can outrank them. An exact official/curated membership source can be reused without searching for a Character-specific interview after identity and Browse HOME are established. Issue #180 artifacts and previously confirmed HOME values remain unchanged; all new decisions are additive in #216.

## Decision rule

`Character -> Browse HOME` is accepted when an exact, reviewed Character identity is explicitly included in accepted semantic-membership sources, the source scope supports an existing canonical Copyright root, and either that root is unique or an explicitly evidenced Browse HOME priority yields one winner. Same-tier validated roots remain unresolved. A candidate root only routes research; it never supplies membership evidence.

Accepted membership classes are:

1. Official Character rosters, directories, cast/member lists, and game rosters.
2. Existing validated Issue #180/#216 semantic memberships and repository evidence, including exact validated structural inheritance.
3. Separately accepted curated Character lists, including explicit Danbooru Copyright Character/member sections. A page's generic prose or first Copyright link is not a list.
4. Validated identity aliases and structural inheritance from a confirmed base, only where the exact edge and base HOME are validated.

Popularity, post counts, co-occurrence, RelatedCopyright, AI recall, fuzzy names, and candidate-root hints remain ineligible as HOME evidence. Multiple accepted roots with tied or missing priority evidence remain a conflict and receive no HOME.

## Review tiers

- **AUTO_ACCEPT**: a source is already accepted, the exact cohort identity is already mapped, its scope is recorded, its canonical root exists, and the combined accepted memberships resolve to one root or one explicitly higher Browse HOME priority. Reuse the membership row; do not search for a Character-specific source.
- **FAST_REVIEW**: no reusable exact membership has yet been joined. Review existing source registry inventories, approved curated lists, and one source-level official roster. Keep the batch at source/root level. If the exact identity and single-root membership are clear, add a reviewed mapping and bulk decision.
- **DEEP_RESEARCH**: only for actual identity collisions, competing roots, ambiguous subseries/root normalization, crossovers/guest identities, players/avatars, mascots, voice-synthesis or VTuber affiliation, or missing/contested source scope. Do not use it to reconfirm a membership already validated at work/series level.
- **TERMINAL_BLOCKED**: retain explicit `POLICY_BLOCKED`, `IDENTITY_BLOCKED`, `EVIDENCE_CONFLICT`, or researched-no-safe-evidence states. These are accounted outcomes, not HOME assignments.

## OVER_RESEARCH_CHECK

Before any Character-specific search, inspect `VALIDATED_SEMANTIC_MEMBERSHIPS_V1.csv` and verify:

1. Is there an accepted exact mapping for this Character in the right source scope?
2. Is the exact identity unique in the frozen cohort/catalog?
3. Does an existing #180 root-normalization rule cover the work/root?
4. Is there a genuinely competing accepted HOME, or only a candidate hint?
5. Is the decision already terminal?

If exact accepted membership, identity, and one unique or explicitly preferred root are already established, stop: `AUTO_ACCEPT`. No individual profile, interview, or press release is required. If only source discovery remains, stay in `FAST_REVIEW` and process a whole roster/source scope. Character-specific research is reserved for the listed DEEP_RESEARCH cases.

The table builder joins only `ACCEPTED` source records and `EXACT_COVERED` member mappings, and emits one row per cohort Character (plus one row per competing accepted source when necessary). It does not ingest candidate-root hints. `apply_validated_membership_batch.py` applies only exact memberships with one unique root or one explicit, non-tied Browse HOME priority and preserves existing non-UNRESEARCHED decisions.

## Bulk and provenance requirements

One accepted source scope may yield many decisions in one deterministic batch. Retain the source ID, exact source URL/scope, canonical Character, matched surface, mapping evidence, root normalization, and reason for every decision. Do not extend a roster to unnamed Characters or adjacent works. Check cohort membership, root existence, one-root cardinality, source scope, existing decisions, and unchanged #180 HOME before applying.

The immutable baseline cohort remains 13,983. The final Issue #216 gate remains `UNRESEARCHED=0`, complete provenance, deterministic reconstruction, focused tests, relevant #180 regression, reproducibility, CI, pushed branch, clean tree; no main merge, production apply, or Picker implementation.
