# Issue #132 body/theme architecture findings

These are research-only facet gaps for General identities. The route-candidate CSV contains only identity + existing-route membership pairs; facet IDs are never candidate additions and facet gaps do not qualify an identity for a route. A single identity can independently appear in both reports when it has separate evidence for an existing route and a missing facet.

- General-only identities missing at least one body facet: **252** (257 facet assignments).
- General-only identities missing at least one theme facet: **113** (113 facet assignments).
- General-only identities missing either: **359**.
- Sexual-lens subset (SEXUAL + CONTEXTUAL): body **109**, theme **12**.
- Identity overlap with route candidates (independent findings only): body **27**, theme **2**.
- The existing Japanese/English/alias search stays available for every row; these facets would narrow browse results by a generation axis.
- Route overlap and exact search-surface counts are in `body_theme_route_overlap.csv` and the full ledger.

## Facet membership sizes

| Axis | Facet | General-only identities | GeneralPurpose lens | Sexual lens | Already browseable |
|---|---|---:|---:|---:|---:|
| BODY | BREAST_NIPPLE | 77 | 74 | 55 | 75 |
| BODY | BUTTOCK_ANAL | 32 | 25 | 25 | 31 |
| BODY | FEMALE_GENITAL | 11 | 10 | 4 | 11 |
| BODY | MALE_GENITAL | 20 | 13 | 10 | 20 |
| BODY | MOUTH_ORAL | 117 | 114 | 20 | 117 |
| THEME | BDSM_RESTRAINT | 24 | 23 | 8 | 21 |
| THEME | INJURY_R18G | 82 | 82 | 2 | 82 |
| THEME | REPRO_PREGNANCY_LACTATION | 7 | 5 | 2 | 7 |

## Product judgment

The concentrated body-site gaps include 55 Sexual-lens identities for BREAST_NIPPLE, 25 for BUTTOCK_ANAL, and 20 for MOUTH_ORAL. That is a practical specialized browse axis even though the full-population share is small. Record this as `UNIFIED_FACET_ARCHITECTURE_CANDIDATE` for a separate owner/schema/UI/performance gate.
Theme gaps are smaller (12 General-only identities in the Sexual lens across the three themes), so they remain findings for the same architecture review rather than a separate v1 implementation proposal.

No result-filter latency, startup-memory, or index-build measurement was taken. The current product has no General body/theme runtime facet surface; performance and bake-boundary evidence must precede any implementation decision.
