# Issue #102 — Danbooru product-complete omission audit

## Result

- pinned Danbooru General canonical rows: **30,743**
- product General rows: **30,629**
- accepted Special rows checked: **2,983**
- canonical tags absent from both product General and every Special surface: **108**
- full adult/fetish/R18G fit review: **108/108**
- Special candidates: **4**
- definition-level semantic review: **3**
- General freshness candidates selected in this adult-focused pass: **9**

## Special candidates

- `speckled_areolae` — post_count `1839` — Deep breast/areola morphology is directly aligned with Special discovery; current Danbooru breast taxonomy lists it as a distinct areola description.
- `unzipping_another's_clothes` — post_count `169` — Specific actor-target clothing-state action is harder to discover than generic unzipping/open-clothes and fits Special relation/exposure discovery.
- `cospussy` — post_count `123` — Explicit niche genital/cosplay concept; current Danbooru new-tag reporting confirms it as a General canonical surface and it is absent from both product dictionaries.
- `open-chest_straitjacket` — post_count `104` — Combines restraint equipment with explicit chest-access/exposure geometry and is a strong deep-fetish discovery concept rather than ordinary clothing.

## Semantic review queue

- `offering_collar` — post_count `176` — Potential petplay/BDSM relation concept, but the canonical surface alone does not prove fetish semantics; verify Danbooru definition/examples before Special admission.
- `outstretched_stomach` — post_count `80` — Body-state wording can look fetish-relevant, but current indexed Danbooru context also places it in nonsexual taser/electrocution material; do not classify as adult without definition-level evidence.
- `tied_from_afar` — post_count `77` — Likely a remote/off-frame restraint topology concept and appears with ribbon-around-body material, but exact current semantics/status need direct verification before admission.

## Interpretation

This audit directly tested the failure mode: a real Danbooru General canonical identity exists but is absent from both product General and Special. The omission set is bounded to 108 rows and every row was reviewed for adult/fetish/BDSM/body-site/fluid/nonhuman/R18G Special fit. Keyword heuristics were used only as a review aid and never as an exclusion filter.

The result does **not** show a large high-frequency adult vocabulary collapse: the highest-count omission overall is 7,349 posts, while the strongest adult anatomy omission is `speckled_areolae` at 1,839 posts. However, the four Special candidates are real coverage gaps and should receive a separate promotion decision.

Rows marked `NO_SPECIAL_ADULT_ACTION` are not permanently rejected from product General. This pass only decides whether they expose an adult/niche Special coverage problem.

## Boundaries

- automatic production promotion: **NO**
- Issue #70 mutation: **NO**
- `UserData/user.db` mutation: **NO**
- pseudo-canonical creation: **NO**
- content filter used: **NO**

## Source

- Danbooru snapshot: `2026-09-02`
- SHA-256: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`
- source provenance is preserved in `source_provenance.txt`.
