# Issue #41 frozen input review — batch 01

Status: FROZEN / QUARANTINE ONLY
Issue: #41 `[UI-JA][PILOT] R3 fresh100 semantic evidence + real #32 bridge + blind30 quality gate`
Branch: `ui-ja/issue41-pilot`
Base audited R3 commit: `53f02d9b3419db8fd9099b38204c29eed289ee8e`
Pilot selection blob: `a6e3970ecdde31b67ca78dfc2dea744211864680`
R3 spec blob: `74642e6436de277cf8721bb3572c6c539872fec5`

## Boundary

This batch is semantic/wording input preparation only. It does not run Codex, does not promote an overlay, and does not modify production `data/**`, #32-owned verdicts/candidates, #35 UI, search ranking, `CURRENT_DEV_TASK.md`, main, or Stage10 production A/B.

Japanese wording is never semantic authority. Semantic-scope approval in this batch is limited to rows that remain safely transparent under the R3 rule allowing LOW/MEDIUM canonical-token composition. Rows needing exact-canonical Tier-B scope are deliberately deferred.

## Selection-risk audit note

`pilot_selection.json` reports the requested/achieved selection strata as 25/20/20/20/15, but also reports `shortage_by_stratum.HIGH_POSE_ACTION = 18`. The selection therefore uses one-way fallback/backfill. `selection_stratum` is not treated as proof that the row's actual semantic risk has that class.

The audited engine classifier is also narrower than the written highest-applicable-risk contract for several canonicals. For this batch, any row with pose/action, anatomy/adult, actor/target/body-site binding, idiomatic/ambiguous scope, or other non-transparent semantics is withheld from composition-based approval even when `pilot_selection.json` labels it LOW/MEDIUM.

## Frozen safe rows

Each row below has exactly one primary Japanese display candidate and one minimal Japanese search candidate. No broad search alias is introduced.

| ordinal | canonical | scope basis | display candidate | search candidate | search class | decision |
|---:|---|---|---|---|---|---|
| 1 | `eyelashes` | transparent concrete noun/entity | まつげ | まつげ | EXACT_SYNONYM | include |
| 2 | `gauntlets` | transparent concrete noun/entity | ガントレット | ガントレット | EXACT_SYNONYM | include |
| 4 | `goggles` | transparent concrete noun/entity | ゴーグル | ゴーグル | EXACT_SYNONYM | include |
| 7 | `toenails` | transparent concrete anatomical noun; no actor/target/action relation added | 足の爪 | 足の爪 | EXACT_SYNONYM | include |
| 8 | `dragon_horns` | transparent entity/type modifier + noun | ドラゴンの角 | ドラゴンの角 | EXACT_SYNONYM | include |
| 16 | `mary_janes` | conventional footwear entity name | メリージェーンシューズ | メリージェーン | COMMON_EXACT_PARAPHRASE | include |
| 20 | `plant` | transparent concrete noun/entity | 植物 | 植物 | EXACT_SYNONYM | include |
| 22 | `underwear` | transparent broad clothing-category noun | 下着 | 下着 | EXACT_SYNONYM | include |
| 26 | `black_leotard` | transparent required color + garment composition | 黒いレオタード | 黒いレオタード | COMMON_EXACT_PARAPHRASE | include |
| 27 | `black_ribbon` | transparent required color + object composition | 黒いリボン | 黒いリボン | COMMON_EXACT_PARAPHRASE | include |
| 28 | `black_bikini` | transparent required color + garment composition | 黒いビキニ | 黒いビキニ | COMMON_EXACT_PARAPHRASE | include |
| 29 | `white_panties` | transparent required color + garment composition | 白いパンティー | 白いパンティー | COMMON_EXACT_PARAPHRASE | include |
| 30 | `white_pupils` | transparent required color + body-feature composition | 白い瞳孔 | 白い瞳孔 | COMMON_EXACT_PARAPHRASE | include |
| 31 | `brown_jacket` | transparent required color + garment composition | 茶色のジャケット | 茶色のジャケット | COMMON_EXACT_PARAPHRASE | include |
| 32 | `blue_shirt` | transparent required color + garment composition | 青いシャツ | 青いシャツ | COMMON_EXACT_PARAPHRASE | include |
| 33 | `yellow_eyes` | transparent required color + body-feature composition | 黄色い目 | 黄色い目 | COMMON_EXACT_PARAPHRASE | include |
| 34 | `white_shorts` | transparent required color + garment composition | 白いショートパンツ | 白いショートパンツ | COMMON_EXACT_PARAPHRASE | include |
| 35 | `black_dress` | transparent required color + garment composition | 黒いドレス | 黒いドレス | COMMON_EXACT_PARAPHRASE | include |
| 36 | `black_coat` | transparent required color + garment composition | 黒いコート | 黒いコート | COMMON_EXACT_PARAPHRASE | include |
| 37 | `blue_necktie` | transparent required color + garment composition | 青いネクタイ | 青いネクタイ | COMMON_EXACT_PARAPHRASE | include |
| 38 | `green_hair` | transparent required color + body-feature composition | 緑の髪 | 緑の髪 | COMMON_EXACT_PARAPHRASE | include |
| 39 | `white_flower` | transparent required color + object composition | 白い花 | 白い花 | COMMON_EXACT_PARAPHRASE | include |
| 40 | `yellow_background` | transparent required color + background composition | 黄色い背景 | 黄色い背景 | COMMON_EXACT_PARAPHRASE | include |
| 41 | `white_pants` | transparent required color + trousers composition; avoid ambiguous `白パンツ` | 白いズボン | 白いズボン | COMMON_EXACT_PARAPHRASE | include |
| 42 | `black_necktie` | transparent required color + garment composition | 黒いネクタイ | 黒いネクタイ | COMMON_EXACT_PARAPHRASE | include |
| 43 | `white_bikini` | transparent required color + garment composition | 白いビキニ | 白いビキニ | COMMON_EXACT_PARAPHRASE | include |
| 44 | `black_pants` | transparent required color + trousers composition; avoid ambiguous `黒パンツ` | 黒いズボン | 黒いズボン | COMMON_EXACT_PARAPHRASE | include |
| 45 | `green_dress` | transparent required color + garment composition | 緑のドレス | 緑のドレス | COMMON_EXACT_PARAPHRASE | include |

## Explicitly deferred from batch 01

The following fresh100 rows are not allowed to gain `SEMANTIC_SCOPE` from token composition in this batch. They require exact-canonical Tier-B semantic evidence or a separate conservative review before any READY path:

- body-site / relation / scope binding: `neck_bell`, `thigh_gap`, `facial_mark`, `rabbit_girl`
- pose/action/state/composition: `all_fours`, `shirt_lift`, `facing_viewer`, `spoken_ellipsis`
- idiomatic/ambiguous/entity-width: `fake_animal_ears`, `bara`, `:<`, `hand_fan`, `profile`, `fishnets`, `loli`
- adult action: `fellatio`
- count/visual-width needing exact scope check: `two-tone_background`
- every fresh100 HIGH/CRITICAL row not listed in the safe table above

`loli`, `fellatio`, and `all_fours` are particularly important because the fixed selection currently labels them `LOW`; that label is not used here as permission for automatic semantic approval.

## Search collision safeguards applied

- `white_panties` does **not** receive `白パンツ`, because that term can collide with `white_pants`.
- `white_pants` / `black_pants` use `白いズボン` / `黒いズボン`, preserving the trousers sense instead of the ambiguous Japanese `パンツ`.
- No child/subtype, parent/category, implication-only, fandom/meme, actor-added, target-added, context-added, or broad colloquial terms are included.
- One search candidate per canonical is kept in this batch.

## Next input work

1. Convert these 28 reviewed rows into R3 `SEMANTIC_SCOPE` + `WORDING_CANDIDATE` JSONL records with this frozen review blob as wording-review provenance.
2. Obtain/freeze exact-canonical Tier-B semantic scope for deferred LOW rows and all HIGH/CRITICAL rows.
3. Only after the full fresh100 semantic/wording input is frozen, connect the real read-only #32 snapshot/requirements and run the R3 engine.
