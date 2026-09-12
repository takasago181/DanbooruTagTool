# Issue #64 boundary audit — revision 2

2026-09-12. Responds to [DEV/AUDIT HOLD](https://github.com/takasago181/DanbooruTagTool/issues/64#issuecomment-5644982292). Current proposal: 253 rows; 248 with paths, five unresolved; all reviewed flags false. The prior submission remains at commit `144adfd8f70718ab2eae4c76774b0bd6e86a16d9`.

## Rechecked definitions

| Case | Observed definition and revised path |
| --- | --- |
| `aa-12` | Wiki identifies the item as a combat shotgun → OBJECT_PROP/WEAPON. [Wiki](https://danbooru.donmai.us/wiki_pages/aa-12) |
| `hand_in_bra` | Hand in own or another's bra → ACTION_CONTACT/INTERACTION. The definition does not establish sexual purpose or clothing removal. [Wiki](https://danbooru.donmai.us/wiki_pages/hand_in_bra) |
| `koe_naki_sakana` | Song wiki says it is recognizable by a character's distinctive outfit → CLOTHING/COSTUME discovery proposal; canonical remains the song. [Wiki](https://danbooru.donmai.us/wiki_pages/koe_naki_sakana) |
| `light_in_heart` | A glow at the chest → LIGHT_TIME_WEATHER. [Wiki](https://danbooru.donmai.us/wiki_pages/light_in_heart) |
| `naked_dress` | A person wears a dress but is visibly naked underneath → CLOTHING_STATE_EXPOSURE. [Wiki](https://danbooru.donmai.us/wiki_pages/naked_dress) |
| `ribbon_bar` | Military/police uniform service ribbon → CLOTHING/ACCESSORY. [Wiki](https://danbooru.donmai.us/wiki_pages/ribbon_bar) |
| `screen_zoom` | Stage performance projected onto a physical background screen → STYLE_QUALITY_META primary, PLACE_BACKGROUND secondary. [Wiki](https://danbooru.donmai.us/wiki_pages/screen_zoom) |
| `zoom_layer` | Magnified layer of the illustration; explicitly distinct from the screen projection called screen_zoom → STYLE primary, composition secondary. [Wiki](https://danbooru.donmai.us/wiki_pages/zoom_layer) |
| `viewer_on_leash` | POV image with viewer at receiving end of a leash → interaction primary, composition secondary. [Wiki](https://danbooru.donmai.us/wiki_pages/viewer_on_leash) |
| `bootes_(constellation)`, `cancer_(constellation)` | Named star patterns → PLACE_BACKGROUND, not weather or a literal animal. [Bootes](https://danbooru.donmai.us/wiki_pages/bootes_%28constellation%29), [Cancer](https://danbooru.donmai.us/wiki_pages/cancer_%28constellation%29) |
| `constellation_(love_live!)` | A costume set, not a celestial pattern → CLOTHING/COSTUME. [Wiki](https://danbooru.donmai.us/wiki_pages/constellation_%28love_live%21%29) |
| `small_chastity_cage` | Specific physical device → OBJECT_PROP without DAILY subtype. Known object, unsuitable narrow subtype. [Wiki](https://danbooru.donmai.us/wiki_pages/small_chastity_cage) |
| `maid` | Wearing a maid uniform is the tagging criterion even when not performing the job → CLOTHING/UNIFORM primary, PERSON_COUNT secondary. [Wiki](https://danbooru.donmai.us/wiki_pages/maid) |
| `witch`, `jester` | Role remains primary; stereotypical attire enables optional costume discovery path, not a mandatory attribute. [Witch](https://danbooru.donmai.us/wiki_pages/witch), [jester](https://danbooru.donmai.us/wiki_pages/jester) |
| `nurse`, `nun`, `soldier`, `clown`, `nurse_cap` | Roles link to clothing as secondary; a literal cap is clothing primary. Each wiki is separately linked from [external_review.md](artifacts/external_review.md). |
| `golden_deer_(fire_emblem)` | Named student group used when all are present → PERSON_COUNT, not deer/gold/clothing. [Wiki](https://danbooru.donmai.us/wiki_pages/golden_deer_%28fire_emblem%29) |
| `burst_bomb_(splatoon)`, `baku_(creature)`, `freesia_(flower)` | Definition distinguishes a fictional weapon, mythological creature, and flower → weapon / creature / plant. Sources in catalog. |

## Additional-category stress cases

| Boundary | Sampled evidence and path rule |
| --- | --- |
| Color, pattern, shape | `polka_dot`, `pastel_colors`, `saturated`, `heart_print` → COLOR_APPEARANCE; geometry tags have symbol secondary. Fixed-color clothing/eye tags retain target identity and primary path |
| Gaze vs camera | Looking up/down/side, eye contact → GAZE. `profile` is only one side of face visible, so COMPOSITION, not gaze |
| Light vs sky | Backlight, dappled light, moonlight, night/dawn/weather, aurora → LIGHT. Sky, star, planet, constellation → PLACE_BACKGROUND |
| Composition vs screen layout | Close-up/full body/portrait/perspective/POV/panorama → COMPOSITION. Split-screen and magnified layers → STYLE, with composition as a secondary discovery route |
| Pose vs body part | Standing/sitting/lying orientations/jump/stretch → POSE_MOVEMENT |
| Living things vs food/place | Animals → CREATURE; rose/cactus/grass/freesia → PLANT. Fish definition distinguishes food use. Mushroom is fungus, so LIVING_NATURE root only |
| Text vs symbol vs eye feature | Direction arrow/sound effect/logo/watermark/thought bubble/star symbol → TEXT_SYMBOL. Symbol-shaped pupils → HAIR_FACE. Sky stars stay PLACE |
| Role vs attire | Role main path remains for witch/jester/nun; attire secondary. Maid wiki makes worn uniform central, so uniform primary. Police spans too many role types and stays unresolved |

All 97 external review rows have paraphrased observation, a separate classification inference, and a source trail in `external_evidence.json` / [review catalog](artifacts/external_review.md). Wiki evidence is not canonical authority, and no gold labels, independent acceptance, or error rate are claimed.

## Post context and unresolved policy

The post inspection reads tag metadata only: the first 12 available post IDs ordered ascending per tag. It did not download or inspect images. A missing co-tag is not negative evidence.

| Canonical | Direct page | official_alternate_costume in 12 | Treatment |
| --- | --- | ---: | --- |
| `minna_de_enjoy!_spojoy_park_(project_sekai)` | Event wiki | 7 | UNRESOLVED: whether a whole event receives clothing path |
| `saihate_e_to_tobu_kimi_e_(project_sekai)` | Event wiki | 8 | UNRESOLVED: same scope decision |
| `uma_stars_(umamusume)` | Show/project wiki | 11 | UNRESOLVED: show/theme vs outfit path |
| `funsai_seyo!_unvalentine_no_fukushuu_(project_sekai)` | Event wiki | 10 | UNRESOLVED under same policy |
| `nijigasaki_7th_live!_new_tokimeki_land` | No exact page | 9; Hawaiian shirt in all 12 | CLOTHING/COSTUME proposal from context alone; needs independent check |
| `blood_moon_(league)` | No exact page | 1 | COSTUME proposal supported by related official skin pages plus context, not an arbitrary co-tag threshold |

The first four are now factually identified; they remain unresolved because event/show identity does not decide its practical browse path. Police is also unresolved because its definition covers people, places, equipment, and scenes. No category was added just to make unresolved count zero.

## Concentration and stop point

- Same 17 top levels, 16 optional subgenres, depth ≤2; visible catch-all remains zero.
- Primary counts improved from V1 to V2: color 1→9, gaze 3→10, light 4→14, composition 5→15, pose 5→13, living/nature 6→16, text/symbol 10→16.
- Largest primary remains clothing, 47/248 = 18.95%; everyday 13, costume 16, uniform 9, accessory 9.
- Five unresolved are 1.98%, not folded into a visible “other.” Another 30,376 entries are NOT_SAMPLED, not unresolved.
- 156 original pilot rows are outside this targeted external check. Revised paths remain proposals and all reviewed flags are false.
- No production changes. DEV/AUDIT must decide event/theme routing, context-only attire paths, secondaries, and whether to request a different pilot. No full rollout/merge/#34/#42/Stage10 before acceptance.
