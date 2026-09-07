# Alias two-axis policy — Ruleset v2 / v3.0

## Decision

Alias relationship and statistics eligibility are independent axes.

- `37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv` is the authoritative semantic relationship table for all 778 Alias rows.
- `38_ALIAS_STATISTICS_POLICY_v3.0.csv` is the authoritative statistics-routing table for all 778 Alias rows.
- `04_ALIAS_RISK_OVERLAY.csv` and `05_ALIAS_DEFAULT_STATS_SAFE.csv` remain compatibility/audit views only. Their legacy statistics columns are not authoritative.

## Why

A source term can be semantically equivalent but lexically dangerous, or semantically non-equivalent while still providing strong related statistical evidence. A single `safe/risk` axis cannot represent both facts without contradiction.

Examples:

- `squirt gun -> water_gun`: lexical ambiguity exists, while `water_gun` can still be a strong statistical anchor for the water-gun concept.
- `anal sex -> anal`: target is related but broader, so it is not full-semantic identity even though it may be useful as related evidence.
- `naked sleeves -> detached_sleeves`: legacy naming risk is distinct from whether detached-sleeves statistics are useful.

## Runtime rule

Neither axis owns Prompt output. Runtime Prompt replacement remains prohibited unless a separate audited Prompt Route explicitly authorizes a form.
