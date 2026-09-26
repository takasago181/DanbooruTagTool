# Issue #180 — Unknown qualifier triage result

Source: GitHub Actions run 35624333781.

- UNKNOWN_QUALIFIER Character rows: **13,753**
- distinct final qualifiers: **3,873**
- heuristic VARIANT_OR_ATTRIBUTE: **1,070 Character rows**
- IP_ROOT_OR_AMBIGUOUS_REVIEW: **12,683 Character rows**

This heuristic is triage only. It does not auto-approve HOME.

## High-yield review order

The largest IP-like qualifier families should be reviewed first because one approved qualifier→root normalization can unlock many Character candidates without relying on old relations:

1. fire_emblem — 577
2. girls'_frontline — 327
3. genshin_impact — 315
4. kemono_friends — 249
5. nikke — 237
6. granblue_fantasy — 207
7. project_moon — 133
8. reverse:1999 — 105
9. pgr — 95
10. zenless_zone_zero — 81
11. one_piece — 68
12. xenoblade — 61
13. honkai_impact — 59

These 13 families alone cover **2,514 Character rows** before semantic validation.

## Safety

Do not bulk-approve from frequency or qualifier spelling alone. Each family needs:
- canonical Copyright root exists or an explicit approved normalization;
- qualifier semantics actually denote that IP/root rather than a costume/subwork/attribute;
- conflict check against accepted authority;
- semantic sample including variants and long-tail;
- fail closed if root semantics are ambiguous.

The 1,070 heuristic variant/attribute rows should not be mapped directly from their final qualifier. They belong in base-Character/A4 inheritance or individual review lanes.
