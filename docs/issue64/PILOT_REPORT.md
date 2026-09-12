# Issue #64 General taxonomy pilot — revision 2

2026-09-12 / FROM: DEV implementation (Codex) / TO: DEV・AUDIT

**RESULT: targeted revision complete; 253-row pilot returned for review. Semantic acceptance and full rollout remain pending.**

Branch: `codex/issue64-general-taxonomy-pilot` (same branch). Base live main: `293181686260a91398334a0fe2d794a5998388cc`. Previous commit: `144adfd8f70718ab2eae4c76774b0bd6e86a16d9`. The new commit SHA is recorded in the Issue #64 re-handoff comment.

This revision responds to [DEV/AUDIT review](https://github.com/takasago181/DanbooruTagTool/issues/64#issuecomment-5644982292): HOLD_PILOT_ACCEPTANCE / TARGETED REVISION REQUIRED. Resume preflight confirmed live main, current-state/task mirrors, Issue body/latest comment, permanent rules, and product goal. Main was unchanged on the final pre-documentation fetch.

## Requested revisions

| Review request | Result |
| --- | --- |
| Recheck all 12 unresolved via definitions | All checked against Danbooru wiki; four also received limited post-tag context. Nine now have proposed paths; three remain unresolved |
| Re-evaluate five flagged paths | All five changed: `bootes_(constellation)`, `small_chastity_cage`, `maid`, `witch`, `jester` |
| Add 64–96 targeted rows | Exactly 80 new rows; all 173 original rows retained without selection drift; total 253 |
| Add source provenance | 97 row-level records with observed fact, distinct inference, URL, retrieval date, wiki ID/update/hash where available; no runtime fetch |
| Preserve 17 levels/categories, catch-all and unresolved | Same 17 top levels, same subgenres, max depth 2, visible catch-all 0, five explicit unresolved |
| Regression/protected recheck | 74 tests passed; 86 protected files unchanged |

## Exact target population remains unchanged

- Production Japanese overlay: 30,629 unique canonical entries; exact match to #55 post-promotion SHA `999b42fa76e036ad79f68ef7cd3ff958c94bd42c08ab00dd0394898d0205de76` (4,114,120 bytes).
- Audited V5 source SHA `a307a354f6e7c9fb2387464713765795d9949802b345b00eb3cb64659df7fdce`; canonical order and every display_ja/search_ja match production.
- Usage source is the 2026-09-02 local snapshot, SHA `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`. Exact target join: 30,629, missing 0, duplicate 0, all original category 0 (General).
- `artifacts/population.txt` remains the same sorted UTF-8/LF canonical membership list, SHA `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b`. No population/evidence diff from V1.
- High usage ≥100,000: 581; ordinary 1,000–99,999: 9,160; rare <1,000: 20,888. Median usage 339, min 50, max 8,363,808. Three or more underscore pieces: 8,017; qualified parenthesized names: 3,557.
- New rare-name sample is eight tags selected to test boundaries; it is not a population-prevalence sample. Snapshot counts remain the sampling source even if live counts have since changed.

## Supplement method

`selection.json` preserves the V1 `issue64-pilot-v1:` seed, initial draws, and 51 boundary challenges. Its new `revision_challenges` groups add exactly 80 distinct in-population names; the builder rejects repeats, overlaps, out-of-target names, additions outside 64–96, or a total pilot above 256.

| Challenge group | Added |
| --- | ---: |
| 色・柄・形 | 8 |
| 視線・向き | 8 |
| 光・時間・天候 | 8 |
| 構図・画角 | 8 |
| ポーズ・動き | 8 |
| 生き物・植物 | 8 |
| 文字・記号 | 6 |
| 役柄と衣装 | 6 |
| 空・星・天体 | 6 |
| 画面表現と構図 | 6 |
| rare qualified General names | 8 |
| **Total** | **80** |

The rare-name rows are `cancer_(constellation)`, `constellation_(love_live!)`, `burst_bomb_(splatoon)`, `funsai_seyo!_unvalentine_no_fukushuu_(project_sekai)`, `golden_deer_(fire_emblem)`, `baku_(creature)`, `freesia_(flower)`, and `blood_moon_(league)`.

## Definitions and strength of evidence

All 80 additions, the 12 previous unresolved rows, and the five flagged examples were checked. `external_evidence.json` contains 97 reviewed-row records: 95 matching direct wiki definitions, two wiki lookups with no exact page, four related wiki pages for one case, and six text-only context samples of 12 post IDs each. Thus the source-kind totals are 99 wiki pages, two no-match lookups, and six post-context samples.

The evidence catalog links each row's source, separates observed definition from taxonomy inference, and labels unresolved lookups. Summaries are paraphrased. No images were downloaded or inspected. Post samples are the first 12 available IDs in ascending order, not random or representative samples. Co-occurrence is never treated as a definition; missing co-tags are not negative evidence. External pages can change; retrieved time, updated_at, wiki ID, and body hash identify the captured version. Reproduction uses committed summaries and is offline.

All 253 rows still have `reviewed=false`, with reviewer and reviewed_at null. External lookups do not constitute independent semantic acceptance. The other **156 original rows were not rechecked in this targeted revision** and are enumerated in `artifacts/revision_audit.json`.

## Revised classifications

Fourteen original rows changed: nine former unresolved rows now have candidate paths, and five existing paths changed.

| Tag | V2 proposed path | Evidence-led reason |
| --- | --- | --- |
| `aa-12` | OBJECT_PROP / WEAPON | Wiki identifies the named item as a combat shotgun |
| `hand_in_bra` | ACTION_CONTACT / INTERACTION | Definition describes a hand in own or another's bra; does not establish sexual purpose or clothing removal, so INTIMATE was not forced |
| `koe_naki_sakana` | CLOTHING / COSTUME | Wiki says the song is recognizable by a character's distinctive outfit; the song's canonical identity is retained |
| `light_in_heart` | LIGHT_TIME_WEATHER | Wiki defines a chest glow |
| `naked_dress` | CLOTHING_STATE_EXPOSURE | Wiki defines a visibly bare state beneath a worn dress |
| `ribbon_bar` | CLOTHING / ACCESSORY | Wiki describes service ribbons worn on uniforms |
| `screen_zoom` | STYLE_QUALITY_META + PLACE_BACKGROUND | Wiki describes performance imagery projected onto a physical background screen |
| `viewer_on_leash` | ACTION_CONTACT / INTERACTION + COMPOSITION_CAMERA | Wiki definition entails both a leash relation and POV |
| `bootes_(constellation)` | PLACE_BACKGROUND | Celestial object/pattern; remove erroneous weather primary and duplicate secondary |
| `small_chastity_cage` | OBJECT_PROP, no subgenre | Known device; DAILY was an unsuitable subtype |
| `maid` | CLOTHING / UNIFORM + PERSON_COUNT | Wiki makes wearing a maid uniform the central tag condition |
| `witch`, `jester` | PERSON_COUNT + CLOTHING / COSTUME | Role stays primary; described attire adds a discovery path, not a requirement |
| `nijigasaki_7th_live!_new_tokimeki_land` | CLOTHING / COSTUME | Direct wiki absent; first 12 context posts include hawaiian_shirt on 12 and official_alternate_costume on 9; weaker, context-only proposal |

Changed statuses/paths, original/new tags, remaining unresolved, and evidence digests are reproducible in `artifacts/revision_audit.json` against `pilot_v1_baseline.json` (anchored to commit `144adfd`).

## Revised pilot distribution

The taxonomy remains 17 top-level genres with the existing optional subgenres and maximum depth two.

| Top-level Japanese entry | V1 primary | V2 primary |
| --- | ---: | ---: |
| 人物・人数・役柄 | 7 | 11 |
| 身体・部位・状態 | 12 | 12 |
| 髪・顔 | 10 | 11 |
| 表情・感情 | 6 | 6 |
| ポーズ・動き | 5 | 13 |
| 構図・画角 | 5 | 15 |
| 視線・向き | 3 | 10 |
| 衣装 | 40 | 47 |
| 着脱・露出 | 6 | 7 |
| 行為・接触 | 14 | 16 |
| 道具・小物 | 15 | 17 |
| 場所・背景 | 8 | 16 |
| 光・時間・天候 | 4 | 14 |
| 色・柄・形 | 1 | 9 |
| 画風・加工・画面表現 | 9 | 12 |
| 生き物・植物 | 6 | 16 |
| 文字・記号・マーク | 10 | 16 |

- 253 total = 248 proposed reachable + 5 unresolved. Pilot usage strata: high 85 / ordinary 99 / rare 69.
- 27 multi-path rows; primary + secondary paths = 275.
- Largest primary group is clothing: 47/248 = 18.95%, split everyday 13 / costume 16 / uniform 9 / accessory 9.
- Visible catch-all 0; explicit unresolved pressure 5/253 = 1.98% (ordinary 1, rare 4). This purposive sample is not a full-population estimate.
- Not sampled: 30,376. Full population classification and runtime application: 0.

The added cases distinguish geometry from camera framing, gaze from viewing position, celestial objects from weather/light, symbols from text, and picture-in-picture effects from camera composition. `small_chastity_cage`, `mushroom`, and `watermark` use a top-level path without a narrower subtype where the evidence does not fit available subgenres; these are known cases, not a general catch-all.

## Five remaining unresolved rows

`minna_de_enjoy!_spojoy_park_(project_sekai)`, `saihate_e_to_tobu_kimi_e_(project_sekai)`, `uma_stars_(umamusume)`, `funsai_seyo!_unvalentine_no_fukushuu_(project_sekai)`, `police`.

The first four have definitions and some costume-related context. The remaining decision is whether an event/show as a whole gets a clothing route. Co-occurrence alone cannot establish that product boundary. `police` is defined broadly across people, places, equipment, and scenes, so a single role/clothing path would be misleading. They remain explicit, with null paths; no new category was created merely to force assignment.

Full case notes and links are in [BOUNDARY_AUDIT.md](BOUNDARY_AUDIT.md); row-level definitions and inferences are in [external_review.md](artifacts/external_review.md).

## Validation and protected data

- Final focused + relevant regression: **74 passed in 14.59s**, covering pilot, existing Japanese overlay, Issue55 promotion, and product-fit.
- `python -X utf8 tools/issue64_taxonomy_pilot.py --check`: **seven artifacts byte-identical**.
- Population artifacts have no V1 diff; `git diff --check` reports no whitespace issues.
- Initial focused run caught a stale expectation of 274 paths; inspection counted 27 secondary paths and corrected the total to 275. The final combined suite then passed.
- Full suite was not run. Known historical main failures are not counted as passes. No UI changes; Windows UI acceptance is downstream.
- Protected inputs were hashed before and after revision. Both match the V1 baseline: **86 files / 7,119,591,754 bytes; changed 0 / added 0 / removed 0**. The scope is recorded in `protected_verification.json` and covers source, derived, runtime, index, Special, generation, semantic data and the audited V5 source.
- No runtime overlay, canonical identity, Special data, Issue #34 ranking, Issue #42 UI, or Stage10 work changed. No runtime LLM or network dependency.

Reproduce from the repository root:

```powershell
python -X utf8 tools/issue64_taxonomy_pilot.py --check
python -X utf8 -m pytest tests/test_issue64_taxonomy_pilot.py tests/test_stage6_5_japanese_overlay.py tests/test_issue55_promote_japanese_overlay.py tests/test_product_fit.py -q --basetemp=.pytest_cache/issue64-review-new
```

Use a new basetemp name. Full artifact building needs the ignored protected inputs; focused tests and review of committed evidence do not need those inputs or network.

**VERDICT: READY_FOR_DEV_AUDIT_RE_REVIEW / NOT ACCEPTED.** No full rollout, merge, #34/#42 work, or Stage10. DEV/AUDIT reviews the revised evidence and five remaining boundary decisions before any later expansion.
