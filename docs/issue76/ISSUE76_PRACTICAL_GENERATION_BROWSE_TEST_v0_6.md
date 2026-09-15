# Issue #76 Practical-generation browse stress test v0.6

Status: **PRACTICAL STRUCTURE PASS / v0.5 ROW MAPPING NOT FREEZE-READY / v0.6 CANDIDATE PATCH PRODUCED**

Date: 2026-09-15 JST

## 1. What this pass tests

This pass does **not** ask whether the taxonomy is ontologically tidy.

It asks:

> When actually constructing and diagnosing image-generation prompts, can a user reach the Special concept from the dimensions that matter in generation?

Evidence used:

1. current Issue #76 v0.5 full 2,788 candidate;
2. current Stage10 structural diagnosis dimensions: object/presence, action/relation, body-site, count/ownership, visibility, scene, theme/topology;
3. historical **actual generation** evidence from Issue #30 Wave 1: 64 generated images / 32 A-B pairs / 16 representative experiments;
4. current NoobAI XL 1.1 author guidance: tag-native captioning and the `special tags -> general tags` prompt structure.

Important limitation:

- the historical 64-image Wave 1 generation was the WAI17 calibration lane, not NoobAI XL 1.1 EPS;
- no new NoobAI image was generated in this Issue #76 pass;
- therefore the old images are used to identify **practical structural predicates**, not to claim model-wide NoobAI success rates.

## 2. Main verdict

The **three-axis browse model itself passes the practical test**:

- `種類から探す`
- `部位から探す`
- `テーマから探す`

The old 38 permanent visible subgenres do **not** need to return.

However, v0.5 was still too mechanically inherited from v1 and was **not freeze-ready**.

Actual-generation task structure exposed missing intrinsic body-site routes and several forced semantic homes.

The fix is not more visible shelves. The fix is better sidecar facets.

## 3. Actual-generation Wave 1 cross-check

The 16 Wave 1 experiment classes were cross-checked against the browse predicates needed to understand the generated image.

v0.5:
- aligned: **13 / 16**
- missing structural browse predicate: **3 / 16**

The three misses were:
- `handjob`
- `double footjob`
- `cooperative footjob`

All three are generation tasks whose correctness depends on genital-target contact, but v0.5 had no male-genital body-site facet because the old v1 mapping had no explicit secondary body-site path.

v0.6 adds the intrinsic target-site route.

v0.6:
- aligned: **16 / 16**

This is not a claim that all 16 generate successfully. In the actual Wave 1 images, for example, `bound penis` failed both A/B pairs and `caught` was visually unclear. Those failures are useful here: they show that restraint topology and scene/context are real generation dimensions and should remain discoverable without turning them into deep subgenre trees.

## 4. Practical correction rule

### Body-site facet rule

Add a body-site facet when the site is an **intrinsic/discriminative structural predicate** of the concept.

Examples:
- `handjob` -> 男性器
- `fellatio` -> 口・口内 + 男性器
- `cunnilingus` -> 口・口内 + 女性器
- `anilingus` -> 口・口内 + 尻・肛門
- `paizuri` -> 乳房・乳首 + 男性器
- `anal beads` -> 尻・肛門
- `urethral beads` -> 尿道

Do **not** attach every possibly involved body part to generic `sex`, generic pose tags, or broad context tags.

That would recreate facet spam.

### Kind/home rule

`kind` is optional.

Use a kind only when it helps browsing by what the concept fundamentally is.

Theme-native umbrella concepts do not need a fake kind home:
- `bdsm` -> テーマ:拘束・BDSM
- `guro` -> テーマ:損傷・R18G
- `ryona` -> テーマ:損傷・R18G
- `breeding kink` -> テーマ:生殖・妊娠・授乳

Dynamic processes/actions should not be hidden in static body state:
- `giving birth` -> 行為・接触 + reproduction theme
- `breastfeeding` -> 行為・接触 + breast + reproduction
- `dissection` / `impalement` / `strangling` -> 行為・接触 + R18G

Concrete BDSM instruments should be objects:
- `nipple clamps`
- `torture instruments`
- `judas cradle`
- `wartenberg wheel`
etc.

## 5. v0.6 patch size

The practical-generation pass changes:

- unique Special rows touched: **100**
- dimensional edits: **111**
- body-site additions: **69**
- kind/home corrections: **42**

No canonical ID, English identity, Alias relation, product-fit verdict, General taxonomy, search ranking, or production WPF data is changed.

## 6. Distribution after v0.6

Kinds:

| 種類 | v0.5 | v0.6 |
|---|---:|---:|
| 行為・接触 | 911 | 907 |
| 衣服・露出 | 503 | 503 |
| 身体・状態 | 322 | 298 |
| 道具・物 | 284 | 299 |
| 体液・排泄 | 275 | 275 |
| ポーズ・構図・場面 | 156 | 156 |
| 人物・関係 | 123 | 123 |
| 異形・変形 | 119 | 119 |
| 表現・メタ | 66 | 66 |
| kindなし（AUTO_CANDIDATE / theme-native） | 0 | 13 |

Body-site facets:

| 部位 | v0.5 | v0.6 |
|---|---:|---:|
| 男性器 | 253 | 307 |
| 乳房・乳首 | 257 | 266 |
| 女性器 | 177 | 183 |
| 口・口内 | 175 | 175 |
| 尻・肛門 | 113 | 113 |
| 尿道 | 20 | 20 |

Theme totals are unchanged:
- 拘束・BDSM: 366
- 損傷・R18G: 66
- 生殖・妊娠・授乳: 25

Every `AUTO_CANDIDATE` still has at least one usable browse route.

## 7. Stress test of the 907-row action shelf

The raw `行為・接触` shelf is still large: **907 rows**.

That alone is **not** evidence for restoring the old 10+ sexual subgenres.

After v0.6:
- 534 action rows have at least one body/theme facet;
- 373 have neither body nor theme facet.

The practical answer should be:
- keep the left browse tree shallow;
- allow result-pane filter chips to intersect the independent axes;
- retain ordinary text search and usage/post-count sorting inside the selected result set.

Example intersections:

| User intent | v2 filter | candidate rows |
|---|---|---:|
| アナル系の道具だけ | 部位:尻・肛門 × 種類:道具・物 | 14件 |
| アナル系の行為だけ | 部位:尻・肛門 × 種類:行為・接触 | 43件 |
| 尿道用の道具 | 部位:尿道 × 種類:道具・物 | 5件 |
| BDSMの道具 | テーマ:拘束・BDSM × 種類:道具・物 | 139件 |
| 口枷系 | テーマ:拘束・BDSM × 部位:口・口内 × 種類:道具・物 | 43件 |
| 妊娠・授乳系全体 | テーマ:生殖・妊娠・授乳 | 25件 |
| R18Gの行為 | テーマ:損傷・R18G × 種類:行為・接触 | 19件 |
| R18Gの身体状態 | テーマ:損傷・R18G × 種類:身体・状態 | 30件 |
| 口×男性器 | 部位:口・口内 AND 男性器 | 22件 |
| 口×女性器 | 部位:口・口内 AND 女性器 | 4件 |
| 乳房×男性器 | 部位:乳房・乳首 AND 男性器 | 10件 |

These intersections produce useful working sets without a new nested hierarchy.

Especially important:
- same-axis body facets should be AND-combinable in the result pane when useful (`口・口内` + `女性器`, `乳房・乳首` + `男性器`);
- this is a **filter operation**, not a new taxonomy level.

## 8. Representative before/after generation-oriented examples

| Special | generation predicate | v1 primary route | v2 v0.6 route |
|---|---|---|---|
| 263 `vibrator` | object presence | 道具・性具・機械 | 種類:道具・物 |
| 669 `breasts out` | body visibility | 裸体・衣服・露出 > 部分露出 | 種類:衣服・露出 / 部位:乳房・乳首 |
| 2055 `skirt lift` | clothing/exposure | 裸体・衣服・露出 > 脱衣・着崩し | 種類:衣服・露出 |
| 131 `standing missionary` | pose/composition | ポーズ・体位・構図 | 種類:ポーズ・構図・場面 |
| 269 `dildo` | object presence | 道具・性具・機械 | 種類:道具・物 |
| 38 `handjob` | action + male-genital target | 性行為・性的刺激 > 手・足・身体刺激 | 種類:行為・接触 / 部位:男性器 |
| 265 `vibrator on nipple` | tool + nipple body-site | 道具・性具・機械 | 種類:道具・物 / 部位:乳房・乳首 |
| 20 `double footjob` | action + count + male-genital target | 性行為・性的刺激 > 手・足・身体刺激 | 種類:行為・接触 / 部位:男性器 |
| 16 `cooperative footjob` | action + multi-person binding + male-genital target | 性行為・性的刺激 > 手・足・身体刺激 | 種類:行為・接触 / 部位:男性器 |
| 2024 `breast expansion` | body transformation + breast site | 異形・非人間・触手・変形 | 種類:異形・変形 / 部位:乳房・乳首 |
| 632 `bound penis` | restraint topology + male-genital site | 拘束・BDSM・支配 > 拘束状態 | 種類:行為・接触 / 部位:男性器 / テーマ:拘束・BDSM |
| 337 `cum` | fluid/result state | 体液・排泄・汚損 | 種類:体液・排泄 |
| 325 `tentacle sex` | nonhuman form + sexual relation | 異形・非人間・触手・変形 | 種類:異形・変形 |
| 2190 `pregnant` | pregnancy body state | 生殖・妊娠・授乳 | 種類:身体・状態 / テーマ:生殖・妊娠・授乳 |
| 2149 `caught` | scene/context | 状況・場面 | 種類:ポーズ・構図・場面 |
| 574 `vibrator cord` | object construction support | 道具・性具・機械 | 種類:道具・物 |
| 266 `anal beads` | tool + anal site | 道具・性具・機械 | 種類:道具・物 / 部位:尻・肛門 |
| 268 `butt plug` | tool + anal site | 道具・性具・機械 | 種類:道具・物 / 部位:尻・肛門 |
| 149 `anal object insertion` | insertion + anal site | 接触・挿入・部位行為 > 肛門・直腸 | 種類:行為・接触 / 部位:尻・肛門 |
| 101 `anilingus` | oral relation + anal site | 性行為・性的刺激 > 口淫 | 種類:行為・接触 / 部位:口・口内 \| 尻・肛門 |
| 104 `fellatio` | oral relation + male-genital target | 性行為・性的刺激 > 口淫 | 種類:行為・接触 / 部位:口・口内 \| 男性器 |
| 681 `cunnilingus` | oral relation + female-genital target | 性行為・性的刺激 > 口淫 | 種類:行為・接触 / 部位:口・口内 \| 女性器 |
| 696 `licking testicle` | mouth + testicle target | 性行為・性的刺激 > 口淫 | 種類:行為・接触 / 部位:口・口内 \| 男性器 |
| 698 `testicle sucking` | mouth + testicle target | 性行為・性的刺激 > 口淫 | 種類:行為・接触 / 部位:口・口内 \| 男性器 |
| 524 `paizuri` | breast contact + male-genital target | 性行為・性的刺激 > 手・足・身体刺激 | 種類:行為・接触 / 部位:乳房・乳首 \| 男性器 |
| 536 `tribadism` | female-genital contact | 性行為・性的刺激 > 擦り・挟み・こすり | 種類:行為・接触 / 部位:女性器 |
| 541 `vaginal` | vaginal/female-genital site | 性行為・性的刺激 > 性交・性行為 | 種類:行為・接触 / 部位:女性器 |
| 209 `urethral beads` | tool + urethral site | 道具・性具・機械 | 種類:道具・物 / 部位:尿道 |
| 219 `urethral sounding` | action + urethral site | 接触・挿入・部位行為 > 尿道 | 種類:行為・接触 / 部位:尿道 |
| 1814 `ball gag` | tool + mouth + BDSM | 拘束・BDSM・支配 > 口枷 | 種類:道具・物 / 部位:口・口内 / テーマ:拘束・BDSM |
| 1828 `handcuffs` | tool + BDSM | 拘束・BDSM・支配 > 拘束具 | 種類:道具・物 / テーマ:拘束・BDSM |
| 1723 `nipple clamps` | tool + breast site + BDSM | 拘束・BDSM・支配 > 苦痛・拷問 | 種類:道具・物 / 部位:乳房・乳首 / テーマ:拘束・BDSM |
| 633 `chastity cage` | tool + male-genital + BDSM | 拘束・BDSM・支配 > 貞操管理 | 種類:道具・物 / 部位:男性器 / テーマ:拘束・BDSM |
| 416 `bdsm` | theme umbrella | 拘束・BDSM・支配 | テーマ:拘束・BDSM |
| 2191 `breast pump` | tool + breast + reproduction | 道具・性具・機械 | 種類:道具・物 / 部位:乳房・乳首 / テーマ:生殖・妊娠・授乳 |
| 2193 `breastfeeding` | action + breast + reproduction | 生殖・妊娠・授乳 | 種類:行為・接触 / 部位:乳房・乳首 / テーマ:生殖・妊娠・授乳 |
| 2184 `giving birth` | process/action + reproduction | 生殖・妊娠・授乳 | 種類:行為・接触 / テーマ:生殖・妊娠・授乳 |
| 470 `guro` | theme umbrella | 損傷・R18G | テーマ:損傷・R18G |
| 473 `dissection` | action/process + R18G | 損傷・R18G | 種類:行為・接触 / テーマ:損傷・R18G |
| 476 `impalement` | action/process + R18G | 損傷・R18G | 種類:行為・接触 / テーマ:損傷・R18G |
| 1772 `corpse` | body/state + R18G | 損傷・R18G | 種類:身体・状態 / テーマ:損傷・R18G |
| 2164 `blood` | fluid + R18G | 体液・排泄・汚損 | 種類:体液・排泄 / テーマ:損傷・R18G |
| 1958 `ryona` | theme umbrella | 損傷・R18G | テーマ:損傷・R18G |
| 1961 `strangling` | action + R18G | 損傷・R18G | 種類:行為・接触 / テーマ:損傷・R18G |

## 9. Practical UX decision

### PASS
- three independent browse axes;
- no permanent visible old 38-subgenre tree;
- `尻・肛門` remains one visible facet;
- optional kind/home;
- multi-route discovery for objects/actions/body states;
- intersection chips in result pane.

### DO NOT DO
- do not restore `口淫`, `手・足・身体刺激`, `局所刺激`, `直前・事後`, etc. as permanent child shelves merely because `行為` is large;
- do not create a third/deeper taxonomy;
- do not encode generation topology as dozens of visible tree nodes;
- do not treat v1 secondary-path absence as proof that a body-site facet is irrelevant.

## 10. Next gate

Before WPF production replacement:

1. treat v0.6 as the candidate data for a **browse-only WPF prototype**;
2. prototype result-pane axis chips + search/sort without changing production;
3. test the same practical tasks by hand in WQHD;
4. only if the 907-row action shelf is still genuinely awkward after those controls, add the smallest proven refinement.

Current recommendation:

> **Do not split `行為・接触` yet.**
>
> First test the shallow tree + cross-axis chips + search/sort. Practical generation evidence says body-site/relation/theme are more useful discriminators than the old sexual-act ontology.
