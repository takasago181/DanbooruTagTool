# Stage 8C Phase 0 Report

## v1.6 independent-audit correction pass

The Phase 0 correction pass closes the independent-audit findings without
changing runtime code or either production Support CSV. Family support now has a
full audit-only proposal ledger; applicability is keyed by `proposal_id` plus
original Special ID and validates the complete promoted metadata. An enabled
Family row requires a `UNIVERSAL_PASS` proposal with all current members, and a
zero-member family is always blocked.

The two zero-member production FamilyRuleIds, `GFR_ALIAS_REFERENCE` and
`GFR_SEMANTIC_SUPPORT`, are recorded as `NOT_APPLICABLE_NO_MEMBERS` with
membership evidence. They do not represent a Support assertion. StaticFamily
summaries now use the fixed resolver's effective relations, so future family
relations are included with resolver precedence rather than being silently
omitted.

Model-familiarity version/cutoff statuses are enum-validated. Practical-use and
evidence history can only reference an enabled production relation or a valid
pre-promotion proposal. MODEL_OBSERVED and USER_ENV_VERIFIED require source-kind
matching plus evidence/test/seed/condition/result references. The proposal and
evidence additions remain audit-only.

## v1.7 final guard correction

The pre-promotion lifecycle is cross-validated. `UNIVERSAL_PASS` requires the
exact current member set and one `APPLIES_SAME_RELATION` row per member;
`PROMOTED` additionally requires one exact enabled production family row with
matching full metadata. Active proposal ambiguity, zero-member promotable
states, production rows without a proven proposal, and terminal Family review
contradictions are rejected. Practical-use now carries optional `proposal_id`
and nonempty validators require relation/proposal context. Observed family
proposals require model/test scope. The research registry distinguishes NoobAI
XL 1.1 EPS from NoobAI XL V-Pred 1.0; neither is installed, and WAI v17 remains
primary with UNKNOWN cutoff.

## v1.7a final microfix

Pre-promotion FAMILY practical-use rows now reject `REJECTED` and `UNRESOLVED`
proposal IDs; only active lifecycle states can be referenced. Regression coverage
also distinguishes actual Family membership drift from Special term snapshot
drift and verifies effective resolver relations feed the StaticFamily counter
dimensions. This remains audit-only and does not alter production Support data.

## Result

Implemented Baseline / Audit Infrastructure only. No production Support
relation was added and no family rule was enabled. The fixed Stage 8B resolver,
relation model, UI, and tests match the v1.5 package baseline hashes exactly.

The generated review ledger contains exactly 2,788 unique original Special IDs
with zero term mismatch. The ten Stage 8B Pilot IDs are resolver-confirmed
`SUPPORT_DEFINED`; 2,778 remain `UNREVIEWED`. No canonical, Alias, or Semantic
identity was substituted for the original review owner.

## Inventory and coverage

- Production FamilyRuleId inventory: 25 rows with member counts derived from
  current Generation Profiles. The two zero-member IDs are explicitly
  `NOT_APPLICABLE_NO_MEMBERS`; all nonempty families remain `UNREVIEWED`.
- StaticFamily planning summary: all 25 groups, derived from the existing
  Promotion Plan and kept separate from FamilyRuleId.
- Production Special relations: 39, unchanged.
- Production family relations: 0, unchanged.
- Static NeedsSpatialAssignment: YES 216; CONDITIONAL 677.
- Actual `SPATIAL_ASSIGNMENT` relations: 0. No canonical was generated from the
  static need values.
- Coverage audit: 2,788 rows, all internal consistency checks PASS.

The applicability validator now keys each member review to a full audit-only
family proposal. It requires every FamilyRuleId member to record
`APPLIES_SAME_RELATION`; zero-member families cannot pass vacuously. Synthetic
tests cover a complete pass, missing member, `METADATA_DIFFERS`, nonmember,
zero-member, and terminal decision boundaries. Phase 0 does not add any real
applicability decision or enable a family row.

## Research, test, and evidence boundaries

The audit-only source registry has 15 entries: the supplied initial references
plus the fixed Stage 8B Pilot snapshot provenance. Validators do not infer
semantic truth. Model familiarity, non-tag strategy, Stage 10 semantic test
slots, and practical-use ledgers are header-only. WAI-illustrious-SDXL v17 with
Forge Neo is recorded as the primary user scope and its exact cutoff remains
UNKNOWN.

The production evidence-event ledger is empty. Practical-use and evidence event
validators now require an enabled production relation or a valid family proposal.
Observed evidence also requires a reproducible test profile, source kind, seeds,
condition hash, and result reference. A deterministic 39-row benchmark
shows how current Stage 8B semantic evidence can be seeded later without
duplicating production owner+canonical relations. It records INCONCLUSIVE rather
than inventing generation success. Negative, neutral, mixed, and inconclusive
results and separate model scopes are accepted by validation.

TagComplete Neo, Forge Couple, ControlNet, ADetailer Neo, Dynamic Prompts Neo,
and WD14 Tagger remain external responsibilities. Phase 0 adds no runtime
integration or duplicate implementation. Semantic test-slot metadata keeps
future coverage available when a concrete Prompt segment must be completed by
the user locally.

## Changed and added files

- Added `danbooru_tag_tool/stage8c_audit.py` for audit-only schemas and validators.
- Added `tools/build_stage8c_phase0.py` and
  `tools/stage8c_coverage_audit.py`.
- Added `tests/test_stage8c_phase0.py`.
- Added nine audit-only data/ledger files plus the StaticFamily strategy input.
- Added eight generated benchmark/audit files under `benchmarks/stage8c`.
- Updated `docs/SEMANTIC_SUPPORT_KNOWLEDGE_SCHEMA.md` only to correct the family
  owner to `family_rule_id` and include `SOURCE_VERIFIED`.
- Added this report, the Phase 0 decision, and audit schema document.

## Validation

- v1.7a Phase 0 targeted tests: `21 passed in 0.77s`.
- v1.7a Phase 0 plus Stage 7A/7B/8A/8B targeted regression:
  `86 passed in 4.40s`.
- v1.7a full pytest: `199 passed in 25.71s`.
- Stage 6 parity: base_count 3,735 and candidate count 5,918; common/rare order
  and raw values identical.
- Stage 7B async source matches FINAL and the A→D coalescing regression passes.
- Stage 8A and Stage 8B multi-relation regressions pass.
- Sixteen generated ledgers/audits were byte-identical in the last executable
  verification; v1.7 rerun also passed with the revised 16-artifact set.
- Stage 8B protected mismatch count: 0.
- Special2788 SHA-256:
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`.
- Runtime LLM/network/API calls: 0.

## Remaining work

The 2,778 `UNREVIEWED` Specials, all 25 FamilyRuleId reviews, model familiarity,
non-tag routing, practical-use records, and production evidence events are
deliberately unresolved because Phase 0 creates infrastructure only. They are
not inferred or mass-filled. Stage 8C Phase 1, Stage 9, and Stage 10 were not
started. Stage 8C FINAL is left to later independent audit.

The pre-change baseline and prior handoff are stored under
`backups/stage8c_phase0_baseline_20260906`; the expanded v1.5 specification is
under `backups/stage8c_v1_5_spec_package_20260906`.
