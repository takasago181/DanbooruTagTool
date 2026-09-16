# Issue #104 — Danbooru General adult/fetish gaps missing from Special

## Result

- Danbooru General canonical: **30,743**
- accepted Special baseline: **2,983**
- General canonical not literally/identity-covered by Special: **28,826**
- strict canonical adult/fetish priority: **217**
- already reviewed/excluded by Issue #94: **11**
- missed by the old Issue #94 final-review prescreen and reviewed here: **206**
- additional high-frequency/opaque rescue rows reviewed: **30**
- Special candidates after product-fit review: **95**
- definition-level review queue: **16**

## Interpretation

The old Issue #94 bounded prescreen did not expose most of the strict adult/fetish-named General gaps to final human review. This audit therefore confirms a real Special deep-discovery coverage gap, while also rejecting broad General descriptors, memes, arbitrary object placements and lexical false positives instead of promoting every adult-looking tag.

The candidate subset is **audit evidence only**. It does not certify model-generation effectiveness and does not mutate production Special.

## Important source checks

- Danbooru Tagging Checklist identifies sex, BDSM, sex objects, body parts and guro as explicit/basic tagging areas.
- Danbooru `Tag group:Breasts tags` explicitly lists deep breast morphology, actions, body-part relations and breast-bondage identities used in this review.
- Danbooru leash documentation explicitly lists `viewer_on_leash` and `viewer_holding_leash` as perspective/action variants.
- Danbooru `standing_restraints`, `breast_zipper`, `breast_curtains`, `shibarikini`, and `hand_in_another's_panties` definitions were used as spot checks for the product-fit boundary.

## Boundaries

- automatic production promotion: **NO**
- content filter: **NO**
- Issue #70 mutation: **NO**
- UserData mutation: **NO**
- pseudo-canonical tags: **NO**

## Next gate

Review the remaining definition queue, then decide promotion of the candidate subset as a separate deterministic Special-expansion change. Do not silently add all General tags and do not treat post count alone as a promotion rule.
