# Issue #94 Special gap prescreen v1

Status: **FULL 29,021-ROW PRESCREEN COMPLETE / CALIBRATION CHECKED / NO PRODUCTION MUTATION**

## Scope and authority

This is a content-neutral first-pass prioritisation of the deterministic `GENERAL_ONLY_GAP` inventory. `LIKELY_CANDIDATE` is not a final Special admission decision. `POSSIBLE_DUPLICATE` remains reviewable, and ambiguous Special aliases are not resolved to a single canonical.

- canonical snapshot: `2026-09-02`
- input General gaps: **29,021**
- total prescreened: **29,021**
- `CONTENT_FILTER_USED=NO`
- production Special/General/catalog/UserData and Issue #70: unchanged

## Prescreen status

| status | count |
|---|---:|
| `LIKELY_CANDIDATE` | 1,954 |
| `LIKELY_GENERAL_ONLY` | 26,063 |
| `POSSIBLE_DUPLICATE` | 4 |
| `NEEDS_REVIEW` | 1,000 |

## Confidence and review priority

| confidence | count |  | priority | count |
|---|---:|---|---|---:|
| `HIGH` | 4,729 |  | `P0` | 1,188 |
| `MEDIUM` | 23,292 |  | `P1` | 1,766 |
| `LOW` | 1,000 |  | `P2` | 4 |
| — | — |  | `P3` | 26,063 |

## Concept area

| area | count |
|---|---:|
| `GENERAL_APPEARANCE_OBJECT` | 21,167 |
| `COLOR_APPEARANCE` | 1,919 |
| `BODY_MORPHOLOGY` | 1,485 |
| `CLOTHING_EXPOSURE` | 1,301 |
| `ACTION_CONTACT` | 1,296 |
| `BODY_RELATION_STATE` | 832 |
| `NONHUMAN_TRANSFORM` | 367 |
| `DEVICE_ADORNMENT` | 221 |
| `PLACE_BACKGROUND` | 203 |
| `FLUID_REPRODUCTION` | 117 |
| `POSE_POSITION` | 113 |

## Existing 130-row calibration

- effective human calibration rows: **130**
- calibration rows present in the 29,021-row input: **118**
- calibration rows outside the 29,021-row input: **12**
- raw heuristic matches before applying calibration anchors: **118 / 118 (100.0%)**
- raw heuristic mismatches: **0**
- final output retains the effective human-reviewed status for these 130 rows as calibration anchors; this does not turn them into a population-wide human review.

Human anchor distribution:

- `CANDIDATE`: 87
- `DUPLICATE_ALREADY_COVERED`: 16
- `NEEDS_REVIEW`: 9
- `OUTSIDE_SPECIAL_NONCONTENT`: 18

### Raw heuristic mismatches

None.

### Calibration rows outside the input gap inventory

These reviewed rows are preserved in the branch evidence but were not part of the deterministic `GENERAL_ONLY_GAP` population, so they are not duplicated into the 29,021-row prescreen CSV:

- `areola_slip`
- `asymmetrical_docking`
- `cleavage_cutout`
- `female_pubic_hair`
- `male_pubic_hair`
- `micro_pasties`
- `no_panties`
- `oral_invitation`
- `piledriver_(sex)`
- `revealing_clothes`
- `sex_from_behind`
- `symmetrical_docking`

## Calibration interpretation

The calibration set is a purposive boundary sample, not a statistical holdout. Mismatches are retained above so later human review can correct the rule surface; no content category is used as an exclusion filter.

## Random spot-check samples

Deterministic seed: `9401`. Each sample is drawn from the final prescreen output after calibration anchors are applied.

### `LIKELY_CANDIDATE` (50 rows)

| canonical | nearest Special | area | priority |
|---|---|---|---|
| `hair_half_over_shoulder` | `off shoulder (SpecialID 2230; score=0.472)` | `BODY_RELATION_STATE` | `P0` |
| `phone_between_breasts` | `alcohol between breasts (SpecialID 2710; score=0.702)` | `BODY_RELATION_STATE` | `P0` |
| `type_91_armor-piercing_shell` | `piercing (SpecialID 1833; score=0.590)` | `DEVICE_ADORNMENT` | `P0` |
| `camera_around_neck` | `tentacle around neck (SpecialID 1879; score=0.665)` | `BODY_RELATION_STATE` | `P0` |
| `finger_on_eyewear` | `cum on eyewear (SpecialID 352; score=0.653)` | `BODY_RELATION_STATE` | `P0` |
| `scar_on_leg` | `cum on leg (SpecialID 1273; score=0.676)` | `BODY_RELATION_STATE` | `P0` |
| `one_eye_covered` | `penis over one eye (SpecialID 823; score=0.504)` | `BODY_RELATION_STATE` | `P0` |
| `licking_own_arm` | `licking own penis (SpecialID 1494; score=0.671)` | `BODY_RELATION_STATE` | `P0` |
| `butterfly_on_face` | `testicles on face (SpecialID 960; score=0.625)` | `BODY_RELATION_STATE` | `P0` |
| `see-through_nightgown` | `see-through (SpecialID 2135; score=0.793)` | `ACTION_CONTACT` | `P0` |
| `thick_chest_hair` | `thick testicle hair (SpecialID 1232; score=0.693)` | `BODY_RELATION_STATE` | `P0` |
| `grabbed_breast_over_shoulder` | `breast (SpecialID 2632; score=0.559)` | `BODY_RELATION_STATE` | `P0` |
| `gauze_on_hand` | `cum on hand (SpecialID 1271; score=0.671)` | `BODY_RELATION_STATE` | `P0` |
| `hanging_from_tree` | `fingering from behind (SpecialID 816; score=0.441)` | `ACTION_CONTACT` | `P1` |
| `cat_on_head` | `penis on head (SpecialID 815; score=0.633)` | `BODY_RELATION_STATE` | `P0` |
| `fan_between_breasts` | `cum between breasts (SpecialID 1290; score=0.712)` | `BODY_RELATION_STATE` | `P0` |
| `unworn_kimono` | `naked kimono (SpecialID 2396; score=0.530)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `bite_mark_on_hand` | `cum on hand (SpecialID 1271; score=0.603)` | `BODY_RELATION_STATE` | `P0` |
| `covered_eyes` | `covered penis (SpecialID 683; score=0.602)` | `BODY_RELATION_STATE` | `P0` |
| `hand_on_wall` | `cum on wall (SpecialID 1125; score=0.646)` | `BODY_RELATION_STATE` | `P0` |
| `lap_pov` | `futanari pov (SpecialID 2746; score=0.479)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `hand_on_belt` | `hand on own penis (SpecialID 797; score=0.593)` | `BODY_RELATION_STATE` | `P0` |
| `toy_boat` | `toy insertion (SpecialID 307; score=0.456)` | `DEVICE_ADORNMENT` | `P1` |
| `unworn_wig` | `unworn gag (SpecialID 2518; score=0.602)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `mouth_piercing` | `piercing (SpecialID 1833; score=0.777)` | `DEVICE_ADORNMENT` | `P1` |
| `fluid_on_breasts` | `cum on breasts (SpecialID 554; score=0.693)` | `FLUID_REPRODUCTION` | `P0` |
| `headphones_around_neck` | `tentacle around neck (SpecialID 1879; score=0.655)` | `BODY_RELATION_STATE` | `P0` |
| `jacket_on_arm` | `cum on arm (SpecialID 1265; score=0.646)` | `BODY_RELATION_STATE` | `P0` |
| `perineum_piercing` | `piercing (SpecialID 1833; score=0.738)` | `DEVICE_ADORNMENT` | `P1` |
| `unworn_sandals` | `unworn blindfold (SpecialID 2431; score=0.542)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `licking_leg` | `licking nipple (SpecialID 751; score=0.602)` | `BODY_RELATION_STATE` | `P1` |
| `see-through_underwear` | `see-through (SpecialID 2135; score=0.793)` | `CLOTHING_EXPOSURE` | `P0` |
| `unusually_open_eyes` | `rape eyes (SpecialID 1379; score=0.482)` | `BODY_RELATION_STATE` | `P0` |
| `standing_on_box` | `standing sex (SpecialID 132; score=0.558)` | `ACTION_CONTACT` | `P0` |
| `wing_piercing` | `piercing (SpecialID 1833; score=0.793)` | `DEVICE_ADORNMENT` | `P1` |
| `hands_on_own_crotch` | `crotch (SpecialID 2361; score=0.616)` | `BODY_RELATION_STATE` | `P0` |
| `tail-shaped_hair` | `tentacle hair (SpecialID 1881; score=0.504)` | `NONHUMAN_TRANSFORM` | `P0` |
| `blood_on_feet` | `blood (SpecialID 2164; score=0.667)` | `FLUID_REPRODUCTION` | `P0` |
| `holding_own_ankles` | `holding tentacle (SpecialID 1868; score=0.543)` | `ACTION_CONTACT` | `P1` |
| `standing_on_sword` | `standing sex (SpecialID 132; score=0.535)` | `ACTION_CONTACT` | `P0` |
| `bodysuit_only` | `bodysuit (SpecialID 2078; score=0.793)` | `CLOTHING_EXPOSURE` | `P1` |
| `eyes_on_wings` | `bound wings (SpecialID 2456; score=0.525)` | `BODY_RELATION_STATE` | `P0` |
| `tongue_piercing` | `piercing (SpecialID 1833; score=0.763)` | `DEVICE_ADORNMENT` | `P1` |
| `hoshino_ai's_pose` | `bound puppy pose (SpecialID 2451; score=0.368)` | `POSE_POSITION` | `P1` |
| `muzzle_gag` | `gag (SpecialID 1825; score=0.658)` | `DEVICE_ADORNMENT` | `P1` |
| `standing_on_chair` | `standing missionary (SpecialID 131; score=0.550)` | `ACTION_CONTACT` | `P0` |
| `fake_pregnancy` | `fake penis shadow (SpecialID 1117; score=0.486)` | `FLUID_REPRODUCTION` | `P1` |
| `holding_another's_finger` | `grabbing another's skirt (SpecialID 2308; score=0.542)` | `BODY_RELATION_STATE` | `P0` |
| `eyebrows_visible_through_headband` | `see through (SpecialID 2134; score=0.420)` | `ACTION_CONTACT` | `P1` |
| `butterfly_on_head` | `penis on head (SpecialID 815; score=0.603)` | `BODY_RELATION_STATE` | `P0` |

### `LIKELY_GENERAL_ONLY` (50 rows)

| canonical | nearest Special | area | priority |
|---|---|---|---|
| `chanchanko_(clothes)` | `handjob over clothes (SpecialID 871; score=0.495)` | `CLOTHING_EXPOSURE` | `P3` |
| `spider_web_hair_ornament` | `tentacle hair ornament (SpecialID 1882; score=0.626)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `miniskirt_day` | `paizuri day (SpecialID 953; score=0.467)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `looking_at_breasts` | `looking at penis (SpecialID 735; score=0.677)` | `BODY_MORPHOLOGY` | `P3` |
| `presenting_removed_panties` | `panties (SpecialID 2112; score=0.608)` | `CLOTHING_EXPOSURE` | `P3` |
| `cheese_trail` | `cum trail (SpecialID 1343; score=0.542)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `evening` | `anilingus (SpecialID 101; score=0.225)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `thistle` | `doggystyle (SpecialID 120; score=0.212)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `nail_biting` | `nipple biting (SpecialID 1487; score=0.617)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `wan_squad_of_gensokyo_(touhou)` | `cleft of venus (SpecialID 2015; score=0.288)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `plastic_spoon` | `fellatio (SpecialID 104; score=0.214)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `dixie_cup_hat` | `open cup (SpecialID 2132; score=0.439)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `musical_note_hair_ornament` | `tentacle hair ornament (SpecialID 1882; score=0.632)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `custard` | `coitus (SpecialID 76; score=0.208)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `raana_the_cat` | `all the way through (SpecialID 1863; score=0.375)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `book_focus` | `breast focus (SpecialID 2176; score=0.528)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `zero_suit` | `tenga suit (SpecialID 1138; score=0.526)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `stuck_in_a_box` | `dick in a box (SpecialID 1116; score=0.749)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `mona_(genshin_impact)_(cosplay)` | `amazon position (SpecialID 118; score=0.137)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `pocket_square` | `pocket pussy (SpecialID 609; score=0.530)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `excalibolg` | `fellatio (SpecialID 104; score=0.200)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `pooka_(odin_sphere)` | `building sex (SpecialID 72; score=0.174)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `blazblue_insignia` | `bare anus (SpecialID 4; score=0.208)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `belly_riding` | `dildo riding (SpecialID 272; score=0.542)` | `BODY_MORPHOLOGY` | `P3` |
| `jack-o'-lantern_hair_ornament` | `tentacle hair ornament (SpecialID 1882; score=0.618)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `eevee_backpack` | `backjob (SpecialID 71; score=0.171)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `paw_stick` | `face fucking (SpecialID 110; score=0.171)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `kazamatsuri_institute_high_school_uniform` | `naked school attendance (SpecialID 2413; score=0.300)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `lightning_bolt-shaped_pupils` | `penis-shaped jewelry (SpecialID 1207; score=0.356)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `gold_ship_(umamusume)_(cosplay)` | `gold pasties (SpecialID 2460; score=0.382)` | `COLOR_APPEARANCE` | `P3` |
| `automaton_(object)` | `cum on object (SpecialID 964; score=0.544)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `van` | `anus (SpecialID 1; score=0.257)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `yukari_is_merry_theory_(touhou)` | `orgy is the new black (SpecialID 1512; score=0.248)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `accurate_lolita_coord` | `after frottage (SpecialID 69; score=0.180)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `frilled_collar` | `open collar (SpecialID 2232; score=0.530)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `test_tube_rack` | `pee tube (SpecialID 1510; score=0.470)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `spinning_top` | `girl on top (SpecialID 1749; score=0.460)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `lightning_ahoge` | `cuddling handjob (SpecialID 19; score=0.203)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `white_robe` | `open robe (SpecialID 2234; score=0.526)` | `COLOR_APPEARANCE` | `P3` |
| `meslamtaea_(fate)` | `ear sex (SpecialID 22; score=0.150)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `green_coat` | `green anus (SpecialID 1216; score=0.557)` | `COLOR_APPEARANCE` | `P3` |
| `chipped_sword` | `sword-swallowing fellatio (SpecialID 996; score=0.343)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `no_toilet_paper` | `human toilet (SpecialID 454; score=0.492)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `mood_(umamusume)` | `clothed sex (SpecialID 15; score=0.167)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `heishou_pack-wei_branch_(identity)_(project_moon)` | `amazon position (SpecialID 118; score=0.113)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `white_pantyhose` | `crotchless pantyhose (SpecialID 2094; score=0.550)` | `COLOR_APPEARANCE` | `P3` |
| `stelle_(honkai:_star_rail)_(cosplay)` | `star pasties (SpecialID 2397; score=0.358)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `pumpkin_hat_ornament` | `penis ornament (SpecialID 1114; score=0.516)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |
| `green_capelet` | `green nipples (SpecialID 895; score=0.553)` | `COLOR_APPEARANCE` | `P3` |
| `palestine` | `after masturbation (SpecialID 84; score=0.200)` | `GENERAL_APPEARANCE_OBJECT` | `P3` |

### `POSSIBLE_DUPLICATE` (4 rows)

| canonical | nearest Special | area | priority |
|---|---|---|---|
| `no_bra` | `bra no (SpecialID 2178; score=0.775)` | `CLOTHING_EXPOSURE` | `P2` |
| `spread_ass` | `ass spread (SpecialID 1809; score=0.820)` | `BODY_MORPHOLOGY` | `P2` |
| `open_towel` | `towel open (SpecialID 2278; score=0.775)` | `GENERAL_APPEARANCE_OBJECT` | `P2` |
| `wide_spread_legs` | `spread legs (SpecialID 2360; score=0.850)` | `BODY_MORPHOLOGY` | `P2` |

### `NEEDS_REVIEW` (50 rows)

| canonical | nearest Special | area | priority |
|---|---|---|---|
| `petals_on_ground` | `stepped on (SpecialID 1964; score=0.398)` | `ACTION_CONTACT` | `P1` |
| `hair_through_headwear` | `see through (SpecialID 2134; score=0.450)` | `ACTION_CONTACT` | `P1` |
| `weapon_on_wall` | `cum on wall (SpecialID 1125; score=0.621)` | `ACTION_CONTACT` | `P1` |
| `holding_towel` | `holding tentacle (SpecialID 1868; score=0.583)` | `ACTION_CONTACT` | `P1` |
| `tail_armor` | `naked armor (SpecialID 2438; score=0.542)` | `NONHUMAN_TRANSFORM` | `P1` |
| `hat_under_hood` | `under boob (SpecialID 2642; score=0.525)` | `ACTION_CONTACT` | `P1` |
| `holding_scale` | `holding tentacle (SpecialID 1868; score=0.583)` | `ACTION_CONTACT` | `P1` |
| `hat_on_horn` | `cum on hat (SpecialID 1330; score=0.548)` | `ACTION_CONTACT` | `P1` |
| `dance_on_the_galaxy_(idolmaster)` | `on side (SpecialID 1754; score=0.347)` | `ACTION_CONTACT` | `P1` |
| `tail_ring` | `labia ring (SpecialID 972; score=0.573)` | `NONHUMAN_TRANSFORM` | `P1` |
| `forked_tail` | `bound tail (SpecialID 1906; score=0.542)` | `NONHUMAN_TRANSFORM` | `P1` |
| `holding_board` | `holding blindfold (SpecialID 2471; score=0.572)` | `ACTION_CONTACT` | `P1` |
| `holding_hairband` | `holding dildo (SpecialID 1381; score=0.552)` | `ACTION_CONTACT` | `P1` |
| `holding_fireworks` | `holding dildo (SpecialID 1381; score=0.542)` | `ACTION_CONTACT` | `P1` |
| `under-rim_eyewear` | `cum on eyewear (SpecialID 352; score=0.447)` | `ACTION_CONTACT` | `P1` |
| `implied_after_fight` | `implied after fingering (SpecialID 1236; score=0.698)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `leaning_against_vehicle` | `building sex (SpecialID 72; score=0.180)` | `ACTION_CONTACT` | `P1` |
| `holding_flute` | `holding cum (SpecialID 400; score=0.579)` | `ACTION_CONTACT` | `P1` |
| `holding_hookah` | `holding dildo (SpecialID 1381; score=0.542)` | `ACTION_CONTACT` | `P1` |
| `inconvenient_tail` | `cum on tail (SpecialID 383; score=0.482)` | `NONHUMAN_TRANSFORM` | `P1` |
| `holding_creature` | `holding cum (SpecialID 400; score=0.575)` | `ACTION_CONTACT` | `P1` |
| `holding_jewelry` | `vaginal jewelry (SpecialID 1499; score=0.542)` | `ACTION_CONTACT` | `P1` |
| `drawing_on_air` | `penis drawing (SpecialID 1565; score=0.458)` | `ACTION_CONTACT` | `P1` |
| `holding_shirt` | `lift shirt (SpecialID 2755; score=0.555)` | `ACTION_CONTACT` | `P1` |
| `holding_broom` | `holding cum (SpecialID 400; score=0.579)` | `ACTION_CONTACT` | `P1` |
| `holding_snowman` | `holding cum (SpecialID 400; score=0.553)` | `ACTION_CONTACT` | `P1` |
| `holding_plate` | `holding dildo (SpecialID 1381; score=0.553)` | `ACTION_CONTACT` | `P1` |
| `looking_through_magnifying_glass` | `fingering through panties (SpecialID 176; score=0.403)` | `ACTION_CONTACT` | `P1` |
| `breaking_through_wall` | `see through (SpecialID 2134; score=0.478)` | `ACTION_CONTACT` | `P1` |
| `chocolate_on_body` | `chocolate on pussy (SpecialID 889; score=0.693)` | `ACTION_CONTACT` | `P1` |
| `holding_ice` | `holding cum (SpecialID 400; score=0.610)` | `ACTION_CONTACT` | `P1` |
| `arms_on_knees` | `bound knees (SpecialID 1904; score=0.525)` | `ACTION_CONTACT` | `P1` |
| `spiked_tail` | `spiked dildo (SpecialID 285; score=0.594)` | `NONHUMAN_TRANSFORM` | `P1` |
| `animal_ear_hood` | `animal insertion (SpecialID 492; score=0.515)` | `NONHUMAN_TRANSFORM` | `P1` |
| `cat_under_faucet_(meme)` | `cat testicles (SpecialID 1165; score=0.390)` | `ACTION_CONTACT` | `P1` |
| `holding_ukulele` | `holding cum (SpecialID 400; score=0.553)` | `ACTION_CONTACT` | `P1` |
| `forced_to_watch` | `forced (SpecialID 1806; score=0.674)` | `GENERAL_APPEARANCE_OBJECT` | `P1` |
| `holding_stake` | `holding tentacle (SpecialID 1868; score=0.583)` | `ACTION_CONTACT` | `P1` |
| `holding_spoon` | `holding dildo (SpecialID 1381; score=0.553)` | `ACTION_CONTACT` | `P1` |
| `holding_club` | `holding cum (SpecialID 400; score=0.633)` | `ACTION_CONTACT` | `P1` |
| `holding_briefcase` | `holding tentacle (SpecialID 1868; score=0.542)` | `ACTION_CONTACT` | `P1` |
| `king_gainer_over!` | `bent over (SpecialID 1745; score=0.433)` | `ACTION_CONTACT` | `P1` |
| `holding_torpedo` | `holding dildo (SpecialID 1381; score=0.563)` | `ACTION_CONTACT` | `P1` |
| `kneeling_on_liquid` | `squirting liquid (SpecialID 954; score=0.490)` | `ACTION_CONTACT` | `P1` |
| `death_devil_(k-on!)` | `death (SpecialID 2165; score=0.588)` | `ACTION_CONTACT` | `P1` |
| `covered_kneepits` | `covered penis (SpecialID 683; score=0.583)` | `ACTION_CONTACT` | `P1` |
| `holding_pillow` | `holding dildo (SpecialID 1381; score=0.608)` | `ACTION_CONTACT` | `P1` |
| `convenient_tail` | `convenient tentacle (SpecialID 1864; score=0.612)` | `NONHUMAN_TRANSFORM` | `P1` |
| `animal_ear_helmet` | `animal insertion (SpecialID 492; score=0.498)` | `NONHUMAN_TRANSFORM` | `P1` |
| `elbows_on_table` | `trampling table (SpecialID 1973; score=0.465)` | `ACTION_CONTACT` | `P1` |

## Guardrails and next step

- This file does not promote any row into Special.
- Adult, explicit, fetish, BDSM, body-fluid, anatomical, gore, violent, taboo, and grotesque content are not exclusion reasons; the pass remains content-neutral.
- Human review should start with P0/P1 rows, especially low-frequency but structurally specific concepts and all `NEEDS_REVIEW` rows.
- Before any Special production change, human review must decide final candidate status and preserve an explicit rationale per row.

## Reproducibility

- scanner input SHA-256: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`
- Special profile rows: 2,788; semantic rows: 336
- exact Special identity rows: 1,674; unique Alias target rows: 767; ambiguous Alias rows: 11
- `PRODUCTION_FILES_CHANGED=NO`
- `ISSUE70_MUTATED=NO`
