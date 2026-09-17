# Issue #118 — Safe General refined v5 semantic review

Research evidence only. Reviewer provenance: `ASSISTANT_SEMANTIC_REVIEW`.
This is not HUMAN_REVIEWED production authority.

## Fresh reintroduced holdout

`reintroduced_holdout_sample_v5.csv` contains 11 identities that were newly reintroduced by the v5 narrower predicate and were absent from all earlier v2/v3/v4 samples.

### NON_SEXUAL — 7

- `arm_garter`
- `heart_o-ring`
- `rabbit_o-ring`
- `black_arm_garter`
- `tail_garter`
- `ankle_garter`
- `cat_o-ring`

These denote ordinary accessory/location-specific concepts without sexual intent in the concept itself.

### CONTEXTUAL — 4

- `black_garter`
- `blue_garter`
- `o-ring_suspenders`
- `o-ring_belt`

The generic garter concepts and O-ring garment constructions naturally occur in both ordinary fashion/costume and sexualized/fetish styling. They therefore must not be AUTO_HIGH_CONF NON_SEXUAL.

## v5 verdict

- proposed NON_SEXUAL: 11
- confirmed NON_SEXUAL: 7
- CONTEXTUAL counterexamples: 4
- SEXUAL counterexamples: 0
- precision for the newly reintroduced v5 holdout: 7 / 11

Therefore v5 does **not** pass the promotion gate.

## Additional adversarial inventory findings

A no-new-GitHub-request scan of the already fetched v2 candidate inventory also found further low-frequency boundary concepts that random validation missed:

- `gravure_swimsuit_(idolmaster)`
- `speculum`
- `laddered_bodystocking`
- `divine_bustier_(dq)`

These should conservatively leave AUTO_NON_SEXUAL eligibility pending explicit semantic treatment. This does not assign them SEXUAL; it only prevents unsafe bulk promotion.

## Next refinement

v6 should:

1. keep location-specific ordinary garters (`arm_garter`, `ankle_garter`, `tail_garter`, `sleeve_garter`) eligible;
2. exclude generic/color garters such as `black_garter` / `blue_garter`;
3. add O-ring belt/suspenders to the contextual-risk exclusion;
4. add narrow red-team risk terms for `gravure`, `speculum`, `bodystocking`, and `bustier`;
5. keep all review verdict generation separate from materialization code;
6. perform no production/main/#117/catalog/UserData mutation.
