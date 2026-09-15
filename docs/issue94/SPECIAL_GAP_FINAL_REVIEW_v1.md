# Issue #94 Special gap final human review v1

Status: **324/324 FINAL HUMAN REVIEW COMPLETE / NO PRODUCTION MUTATION**

Source queue: `docs/issue94/special_gap_final_review_queue_v1.csv`

## Final counts

- total reviewed: **324**
- `CANDIDATE`: **195**
- `GENERAL_ONLY`: **124**
- `DUPLICATE_ALREADY_COVERED`: **5**
- `NEEDS_REVIEW`: **0**
- `CONTENT_FILTER_USED=NO`
- `PRODUCTION_FILES_CHANGED=NO`
- `ISSUE70_MUTATED=NO`

## Decision rule

This is a human product-fit review, not another lexical prescreen. The default for a v2 `LIKELY_CANDIDATE` row is `CANDIDATE`, except for the explicit 117 demotions below. The four v2 `POSSIBLE_DUPLICATE` rows remain `DUPLICATE_ALREADY_COVERED`. The nine v2 boundary rows and fourteen protected human-override rows are resolved explicitly below.

The main consistency rule is that Special remains a deep discovery dictionary, not an exhaustive Cartesian expansion of ordinary General concepts. Ordinary hand/leg poses, ordinary garment layering, generic see-through-by-garment variants, ordinary unworn/wet garment states, ordinary eye/hair coverage, and generic body-site decoration combinations stay in General unless the whole concept adds a distinctly niche relation, exposure state, sexual/BDSM/device interaction, reproductive/R18G state, specialized pose, or otherwise difficult-to-discover concept.

Content severity was not used as an exclusion reason.

## Explicit v2 Candidate -> GENERAL_ONLY demotions (117)

- `arm_between_another's_legs`
- `arm_on_own_leg`
- `arms_between_legs`
- `ascot_between_breasts`
- `between_breasts`
- `between_legs`
- `between_thighs`
- `bikini_bottom_under_shorts`
- `bikini_over_clothes`
- `bikini_top_under_shirt`
- `bikini_under_clothes`
- `bikini_under_skirt`
- `bite_mark_on_leg`
- `bite_mark_on_thigh`
- `blush_visible_through_clothes`
- `bodysuit_under_clothes`
- `bra_over_clothes`
- `bruise_on_leg`
- `buruma_under_skirt`
- `covered_armpit`
- `covered_eyes`
- `covered_navel`
- `eye_over_eye`
- `eyes_over_blush`
- `eyes_visible_through_hair`
- `eyes_visible_through_headwear`
- `grabbing_own_thigh`
- `hair_between_breasts`
- `hair_over_ass`
- `hair_over_breasts`
- `hair_over_crotch`
- `hair_over_eyes`
- `hair_over_one_breast`
- `hair_over_one_eye`
- `hand_on_own_leg`
- `hands_on_own_leg`
- `hands_on_own_legs`
- `hands_on_own_thigh`
- `hands_on_own_thighs`
- `hands_under_legs`
- `hanging_legs`
- `holding_another's_leg`
- `holding_another's_legs`
- `holding_own_leg`
- `hugging_own_leg`
- `hugging_own_legs`
- `jacket_over_swimsuit`
- `leg_between_thighs`
- `leg_lift`
- `leg_tattoo`
- `legs_apart`
- `leotard_under_clothes`
- `looking_through_own_legs`
- `mole_on_leg`
- `ok_sign_over_eye`
- `one_eye_covered`
- `panties_over_bodysuit`
- `panties_over_clothes`
- `panties_over_garter_belt`
- `panties_over_leggings`
- `panties_over_pantyhose`
- `panties_under_bike_shorts`
- `panties_under_bloomers`
- `panties_under_bodysuit`
- `panties_under_buruma`
- `panties_under_leotard`
- `panties_under_pantyhose`
- `panties_under_shorts`
- `panties_under_swimsuit`
- `pantyhose_under_buruma`
- `pantyhose_under_leotard`
- `pantyhose_under_pants`
- `pantyhose_under_shorts`
- `pantyhose_under_swimsuit`
- `scar_on_leg`
- `see-through_bikini`
- `see-through_bodysuit`
- `see-through_bra`
- `see-through_breast_curtains`
- `see-through_dress`
- `see-through_dress_layer`
- `see-through_kimono`
- `see-through_leotard`
- `see-through_midriff`
- `see-through_one-piece_swimsuit`
- `see-through_panties`
- `see-through_pants`
- `see-through_pantyhose`
- `see-through_shirt`
- `see-through_shorts`
- `see-through_skirt`
- `see-through_skirt_layer`
- `see-through_slingshot_swimsuit`
- `see-through_socks`
- `see-through_sports_bra`
- `see-through_underwear`
- `sitting_between_legs`
- `spiral-only_eyes`
- `swimsuit_over_clothes`
- `swimsuit_under_clothes`
- `swimsuit_under_swimsuit`
- `through_clothes`
- `unworn_bikini`
- `unworn_bikini_bottom`
- `unworn_bikini_top`
- `unworn_bra`
- `unworn_male_underwear`
- `unworn_panties`
- `unworn_swimsuit`
- `v_over_eye`
- `w_over_eye`
- `wet_bikini`
- `wet_bra`
- `wet_male_underwear`
- `wet_panties`
- `wet_swimsuit`
- `wings_over_eyes`

All remaining v2 `LIKELY_CANDIDATE` rows are final `CANDIDATE` rows.

## Boundary rows resolved (9)

### CANDIDATE

- `breast_rest`
- `clothes_lift`
- `clothes_pull`
- `gigantic_breasts`
- `holding_pregnancy_test`

### GENERAL_ONLY

- `hand_on_own_thigh`
- `pregnancy_test`
- `sperm_cell`

### DUPLICATE_ALREADY_COVERED

- `no_pants` — existing Special semantic `pants no` already covers the substantive no-pants state.

## Human-override-protected rows resolved (14)

### CANDIDATE

- `blood_on_hand`
- `hand_under_clothes`
- `huge_ass`
- `leash_in_mouth`
- `lifting_own_clothes`
- `pov_crotch`
- `public_urination`
- `skindentation`
- `thick_thighs`
- `thigh_gap`

### GENERAL_ONLY

- `necktie_between_breasts`
- `thighhighs_under_boots`
- `mixed-sex_bathing`
- `same-sex_bathing`

## Existing overlap duplicates retained (4)

- `no_bra`
- `open_towel`
- `spread_ass`
- `wide_spread_legs`

## Family-level rationale

### Kept strongly in Special

- BDSM/restraint/gag/device states and interactions.
- Sexual or intimate body-site actions/relations that are not ordinary generic poses.
- Displaced/exposure clothing states such as lifts, peeks, around-one-leg states, and clothing-barrier sexual actions.
- Complex visibility relations where the relation itself is the discovery concept, not merely a transparent garment subtype.
- R18G localized blood/source states.
- Reproduction/lactation/pregnancy subtypes.
- Specialized sex/BDSM poses and sex-device states.
- Selected deep morphology concepts (`skindentation`, `thigh_gap`, `thick_thighs`, `huge_ass`, `gigantic_breasts`) where the named concept itself is useful discovery vocabulary.

### Kept in General

- Ordinary self/other hand-leg positioning and hugging/holding-leg poses without a stronger niche relation.
- Garment-under-garment layering combinations.
- Straightforward `see-through + garment` combinations; Special already has the general see-through concept and General can carry the canonical garment subtype.
- Ordinary unworn/wet garment states.
- Ordinary eye/hair coverage or gesture compositions.
- Generic body-mark + non-intimate site combinations such as leg tattoo/scar/mole/bruise.
- Ordinary scene distinctions such as same-sex/mixed-sex bathing.

## Remaining work

The General->Special gap-review decision is now complete for the 324-row final queue. The next Issue #94 step is to materialize the **195 final candidate rows** as a candidate-subset artifact with source identity/post-count/aliases and to keep the **124 General-only + 5 duplicate rows** as the explicit rejection/exclusion ledger. This still must not mutate production Special data until a separate promotion step is approved.