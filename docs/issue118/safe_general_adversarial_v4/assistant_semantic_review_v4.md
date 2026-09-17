# Issue #118 — Safe General adversarial v4 semantic review

Research evidence only. This is **not** HUMAN_REVIEWED production authority and does not mutate main, #117, catalog.db, or UserData.db.

Reviewer provenance: `ASSISTANT_SEMANTIC_REVIEW`.

## Clean fresh holdout

`clean_holdout_sample_v4.csv` was independently inspected after materialization.

- rows: 120
- reviewed as NON_SEXUAL: 120
- SEXUAL counterexamples: 0
- CONTEXTUAL counterexamples: 0
- overlap with v2/v3 validation samples: 0 (materializer invariant)

Result: the already-clean v4 pool did not expose a new semantic counterexample in this 120-row holdout.

## Risk discovery findings

The adversarial scan successfully caught important false AUTO_NON_SEXUAL candidates that were missed by v2 random validation, including:

- `multiple_condoms`
- `okamoto_condoms`
- `too_many_condoms`
- `pornstar`
- `stripper`
- Playboy Bunny variants
- slingshot-swimsuit variants

These must not be bulk-promoted as high-confidence NON_SEXUAL solely from their General path.

However, the v4 exclusion layer is intentionally conservative and discovery review found over-exclusion:

- generic `cage`, `rectangular_cage`, `suspended_cage`, `bug_cage`, `holding_cage` are ordinary non-sexual cage concepts; `head_cage` remains a boundary/restraint risk.
- `sleeve_garter` is ordinary clothing/accessory usage and demonstrates that a blanket `garter` token exclusion is too broad.
- generic harness/garter wording should not be excluded merely by token; keep narrower fetish/intimate forms such as garter belt/garter straps, body/chest harness, O-ring constructions, etc. as conservative review risks.

## Decision

Proceed to a refined v5 exclusion predicate:

1. keep contraception/sexual-role/Playboy-Bunny/slingshot-swimsuit risk exclusions;
2. replace blanket `cage` with targeted `head_cage` / stripper-related handling;
3. remove blanket `garter` and `harness` clothing-token exclusions;
4. retain narrower garter-belt/garter-strap/O-ring/body-harness patterns;
5. keep `choker` / `corset` conservative auto-exclusion for now because both have ordinary and fetish/sexualized usage;
6. validate only the newly reintroduced cohort with a fresh sample that excludes every v2/v3/v4 sample used to tune the predicate.

No promotion to research sidecar v3 is authorized by this note. Review verdict generation must remain separate from materialization/promotion code.
