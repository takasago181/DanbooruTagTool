# Issue #180 — Full Character preflight result

Status: RESEARCH / NO MERGE / NO PRODUCTION APPLY

Source: successful GitHub Actions run 35623801609, head `4fc9fe160d136c69c78c618cf3a659b5bac8f4f0`.

## Full population

- Character rows: **35,890**
- APPROVED_QUALIFIER_CANDIDATE: **5,337** (14.87%)
- UNKNOWN_QUALIFIER: **13,753** (38.32%)
- UNQUALIFIED: **16,800** (46.81%)
- total accounted: **35,890 / 35,890**

No legacy relation data was used as HOME authority. Accepted source and production were not modified.

## Approved qualifier candidate distribution

- fate_(series): 1,112
- azur_lane: 798
- arknights: 713
- kantai_collection: 685
- umamusume: 512
- blue_archive: 473
- pokemon: 446
- honkai:_star_rail: 209
- princess_connect!: 117
- wuthering_waves: 100
- girls_und_panzer: 68
- touhou: 62
- hololive: 22
- vocaloid: 20

These are **mechanical candidates**, not accepted relations.

## Unknown qualifier structure

There are about **3,874 distinct unknown final qualifiers**. High-volume IP-like qualifiers include:
`fire_emblem` 577, `girls'_frontline` 327, `genshin_impact` 315, `kemono_friends` 249, `nikke` 237, `granblue_fantasy` 207, `project_moon` 133, `reverse:1999` 105, `pgr` 95, `zenless_zone_zero` 81, `one_piece` 68, `xenoblade` 61, and `honkai_impact` 59.

The same unknown bucket also contains many **non-Copyright / variant qualifiers**, for example:
`1st_costume` 315, `character` 96, `vtuber` 104, `new_year` 48, `2nd_costume` 38, `casual` 32, `stand` 28, `timeskip` 27, `female` 24, `male` 22, `summer` 22, `racehorse` 22, `3rd_costume` 22, `school_uniform` 20, `5th_costume` 20, `human` 18.

Therefore final qualifier alone cannot be treated as Copyright authority globally.

## Expansion decision

The next high-yield lane is **qualifier taxonomy**, not relation guessing:

1. IP_ROOT_CANDIDATE — independently verify qualifier→canonical Copyright root.
2. VARIANT_OR_ATTRIBUTE — do not map qualifier to HOME; resolve base Character then A4 inheritance if official.
3. GENERIC_OR_AMBIGUOUS — manual/semantic review.
4. UNKNOWN — fail closed.

Prioritize high-count IP-like qualifiers first. Each newly approved root can safely unlock many Character candidates without touching unqualified rows.

The 16,800 unqualified rows remain a separate curated-list / exact-authority problem and must not inherit from old RelatedCopyright.

## Gate

Do not promote the 5,337 candidates yet. First sample/audit each approved root family and build the unknown-qualifier taxonomy. Wrong relation remains worse than no relation.
