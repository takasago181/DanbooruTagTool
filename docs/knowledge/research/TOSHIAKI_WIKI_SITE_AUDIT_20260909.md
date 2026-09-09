# としあきdiffusion Wiki 横断監査

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `SITE_AUDIT_V1 / VIDEO_EXCLUDED`

Target: https://wikiwiki.jp/sd_toshiaki/

## 0. Scope

この監査は、としあきdiffusion Wikiを DanbooruTagTool の永続KNOWLEDGE sourceとしてどう扱うべきかを判定する。

ユーザー指示により、動画生成・動画補間・動画LoRA等の動画系ページは evidence 対象外とする。

対象は主に以下。
- Forge Neo / WebUI / ComfyUI
- image model / WAI / Illustrious / Anima
- Prompt / Prompt syntax / Danbooru語
- Negative Prompt
- Hires / upscale / img2img
- ControlNet / regional prompting / Dynamic Prompts / WD Tagger
- LoRA / caption / training / multi-concept training
- FAQ / troubleshooting / error / metadata / reproducibility
- legacy SD1.x/early-SDXL guidance の識別

全ページ索引、メニュー構造、RecentChangesを横断した上で、DanbooruTagToolへ影響の大きいページを本文まで深掘りした。動画を除く全ページの全行を逐語的に精読したという主張はしない。coverageは companion file に明示する。

---

## 1. Site-level verdict

### Decision

**ADOPT AS JAPANESE COMMUNITY PRACTICAL / OPERATIONS CORPUS**

**REJECT AS CANONICAL SEMANTIC AUTHORITY OR UNVERIFIED EXACT-MODEL AUTHORITY**

### Why it is valuable

1. 日本語圏のStable Diffusion運用知識が非常に広い。
2. Forge Neo / ComfyUI / Anima 等、2026年時点の現行系も更新されている。
3. FAQ・トラブルシュートに、成功例だけでなく「なぜ壊れるか」の実践記録が多い。
4. Prompt、Hires、LoRA、ControlNet、Taggerなど、DanbooruTagToolがStage10で遭遇する confound が一箇所に集約されている。
5. ページ自身が「古い/不正確な情報が残る可能性」を認め、古い情報の整理も継続している。
6. 論文や公式Model cardへのリンクを持つページもあり、一次照合の入口として優秀。

### Why it cannot be canonical authority

1. 2022–2023年のSD1.x常識と2026年のAnima/Forge Neo情報が同居する。
2. 同じページの中で、現行情報と旧情報が混在する場合がある。
3. community synthesis、作者推測、体感、exact author factの境界が常に明示されるわけではない。
4. model family / derivative / version間の差を一般化した記述がある。
5. 「公式推奨」と書かれていても、現在の公式Model cardが更新されている場合がある。
6. Prompt/Negativeの強いレシピが、特定時代・モデル向けなのに一般則に見える場合がある。

Project rule:
**Wikiは practical hypothesis / operation evidence として採る。canonical meaning、exact-model rule、production ruleへの昇格には独立照合が必要。**

---

## 2. Evidence classification rule for this site

### `PRACTICAL_CURRENT`
- 2026年更新
- exact tool/model versionが比較的明瞭
- 現在の公式情報と矛盾しない

### `PRACTICAL_VERSIONED`
- usefulだが特定version/architecture/toolに限定

### `COMMUNITY_HEURISTIC`
- 再現条件、seed、母数、一次根拠が不足
- experiment candidateには使える

### `LEGACY`
- SD1.x / early A1111 / old WD ranking / old universal Negative 等
- 現行モデルへ自動転用しない

### `REJECT_FOR_EXACT_MODEL`
- 現在のexact model作者情報と衝突

### `HOLD`
- 現行version確認不足、または競合する情報あり

---

## 3. Material conflict audit

## 3.1 Illustrious generic Negative vs WAI Illustrious v17

WikiのIllustrious一般ページには、長いNegative/full negativeを維持し削らない方がよいという強い助言がある。

しかし exact WAI Illustrious v17 model card は:
- positive: `masterpiece, best quality, amazing quality`
- negative: `bad quality, worst quality, worst detail, sketch, censor`
- quality/aesthetic tagsを入れすぎると品質が落ちる可能性
- Negativeを長くしすぎると品質低下/blurの可能性

を明示する。

Decision:
- Wikiの長いNegative助言: `LEGACY_OR_FAMILY_GENERAL`
- WAI v17へ適用: **`REJECT_FOR_EXACT_MODEL`**

Project consequence:
特殊解剖、multiple appendage、hard-fetish stress testで old universal anatomy Negative を基準にしない。

Sources:
- Wiki Illustrious: https://wikiwiki.jp/sd_toshiaki/Illustrious-XL
- WAI v17 author: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

## 3.2 Anima Negative recipe drift

Wiki Animaページは、`6 fingers`, `6 toes`, `bad hands`, `bad fingers` 等を含む長いリストを「公式推奨」相当として紹介する箇所がある。

Current Anima model card currently shows a different concise negative baseline:
`worst quality, low quality, score_1, score_2, score_3, artist name, blurry, jpeg artifacts, chromatic aberration`

Current exact official also states:
- tags + natural language + mixed prompting
- lowercase / spaces
- Gelbooru spelling preference when forms differ
- pure NLはdescriptiveに、at least ~2 sentences
- multi-characterではidentification/basic appearanceを記述
- tag dropout

Decision:
- Wiki Anima practical relation/actor examples: `PRACTICAL_CURRENT`
- Wikiの古い/misattributed Negative list: `REJECT_FOR_CURRENT_EXACT_ANIMA`
- Wiki独自architecture interpretation: `COMMUNITY_HEURISTIC` unless author-confirmed.

Source:
- Wiki Anima: https://wikiwiki.jp/sd_toshiaki/Anima
- Official Anima: https://huggingface.co/circlestone-labs/Anima

## 3.3 WD Tagger ranking staleness

Wiki WD1.4 Tagger pageには、2024-era comparisonに基づき EVA02 を最良候補のように扱う記述がある。

2026 project contextでは:
- WD EVA02 v3は有用だが `<600 images` tags filter がある。
- Kagami-24k、CL Tagger v2等、より広い語彙/較正情報を持つ候補が存在する。

Decision:
- Wiki ranking: `LEGACY_RANKING`
- WDの一般的操作説明: `PRACTICAL_VERSIONED`
- current evaluator selection: Wiki単独では決めない。

Sources:
- Wiki WD: https://wikiwiki.jp/sd_toshiaki/WD1.4%20Tagger
- WD EVA02 v3: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3

## 3.4 Old universal Negative lists

`万能便利呪文` 等の古いページには、`bad anatomy`、extra limb系等を大量に含む classic Negative stacks がある。

Decision:
- preserve as `LEGACY`
- current WAI/NoobAI/Anima hard-Special baseline: `REJECT`
- anatomy/count-changing Specialでは collision hypothesis としてのみ使い、OFF/ON test対象。

---

## 4. High-confidence useful knowledge from the Wiki

## 4.1 Exact model/tool author guidance overrides community default

Wiki FAQ自体にもモデル作者設定を優先する方向性がある。

Project adoption:
- generic sampler/steps/CFG defaults are fallback only.
- exact checkpoint/version author card is higher authority.

Class: `PRACTICAL_CURRENT -> aligns with project evidence policy`.

## 4.2 Reproducibility needs actual environment identity

FAQでは、同じPromptでも model/settings/library/version が違えば出力が変わり得ること、hash/metadata確認が重要とされる。

Project adoption:
evidence identityに最低限:
- checkpoint/hash
- model family/version/profile
- sampler/scheduler
- steps/CFG/resolution
- seed
- actual positive/negative
- LoRA/control/postprocess
- tool/build where material
を保持する。

Class: `PRACTICAL_CURRENT`.

## 4.3 “Prompt failed” does not immediately mean “model does not know concept”

FAQには、training tag conventionやvisibility、構図、タグの使われ方によって期待actionが出ない例がある。

Project adoption:
`semantic identity -> unary activation -> relation/binding -> visibility/geometry -> conflict` を確認してから `tag unknown` を疑う。

Class: `PRACTICAL_CURRENT`, strongly aligns with Batch A.

## 4.4 Prompt syntax belongs to tool/parser layer

Wiki syntax pagesの `BREAK`, `AND`, comment handling等は A1111/WebUI parser behaviorを含む。

Project adoption:
- syntax featureをモデル学習意味と混同しない。
- `BREAK`等をAnima/NoobAIのlearned grammarと見なさない。
- tool parser versionを evidence identity に含める場合がある。

Class: `PRACTICAL_VERSIONED`.

## 4.5 Canonical underscore identity vs model prompt surface

Danbooru語ページは、Danbooru tagのunderscore形式とAI Prompt surfaceのspace形式を区別している。

Project adoption:
- canonical identity remains `canonical_tag`.
- model prompt surface/trigger spelling is separate field.
- spaces preference does not rename canonical.

Class: `PRACTICAL_CURRENT`, aligns with current canonical/trigger separation.

## 4.6 Anima relation/actor binding practicals

Wiki Anima page recommends explicit actors/positions/relations for multi-character cases and discourages inherited `BREAK`-style character separation.

Official Anima also supports detailed NL and asks for character identity/basic appearance in multi-character prompts.

Project adoption:
- `tag-only` vs `tag anchor + concise explicit relation clause` is a valid controlled A/B lane for Anima.
- explicit actor IDs are better test surfaces than ambiguous pronouns.
- do not claim guaranteed success.

Class: `PRACTICAL_CURRENT + EXACT_AUTHOR_CORROBORATION`.

## 4.7 Hires is a separate generation intervention

Wiki upscale/Hires pages describe Hires.fix as a multi-stage process and denoise as controlling how much the second pass changes the image.

Project adoption:
- base output and final Hires output are distinct evidence.
- final repair != base Prompt success.
- WAI v17 author explicitly says Hires can repair limbs, strengthening this confound.

Class: `PRACTICAL_CURRENT + FACT_EXACT_MODEL for WAI v17`.

## 4.8 ControlNet/regional prompting is an assisted-control lane

Wiki correctly presents ControlNet/regional tools as extra conditioning/control mechanisms.

Project adoption:
- assisted-control success can be valuable product capability.
- it must not certify Prompt-only capability.
- old SD1.5 ControlNet parameters are `LEGACY` unless current version verified.

## 4.9 Dynamic Prompts has strong experimental utility

Wiki and extension behavior support:
- wildcard/template expansion
- combinatorial enumeration
- repeated seed-controlled generation patterns

Project implication:
Dynamic Prompts is a strong candidate for enumerating controlled support variants and reducing manual test preparation.

Boundary:
tool capability only; no semantic authority.

## 4.10 LoRA knowledge is useful if scoped as heuristic

Wiki LoRA pages contain useful operational lessons:
- model-family compatibility matters
- dataset/caption decisions affect what LoRA learns
- multi-concept training increases entanglement risk
- fixed conditions help compare training changes

But claims like:
- source quality explains a precise 80–90%
- fixed image count is universally ideal
- one loss threshold proves success
- Difference LoRA is generally superior
are not accepted as universal FACT.

Class: `PRACTICAL / COMMUNITY_HEURISTIC` depending page.

---

## 5. Important low-confidence / rejected patterns

1. **one universal Negative for all modern anime models** — REJECT.
2. **old SD1.x syntax behavior as model semantic rule** — REJECT.
3. **one Tagger ranking from 2024 as current 2026 best** — REJECT.
4. **20 steps is universal optimum** — REJECT; fallback heuristic only.
5. **one fixed seed proves reliability** — REJECT; useful for controlled visual comparison only.
6. **exact loss threshold proves LoRA quality** — REJECT.
7. **short/simple NL is necessarily best for Anima** — REJECT; current official encourages descriptive pure NL.
8. **Illustrious family guidance automatically transfers to WAI/NoobAI/Anima** — REJECT.
9. **Hires repaired anatomy = base model understood relation/anatomy** — REJECT.
10. **BREAK is character binding mechanism** — REJECT.

---

## 6. Version/freshness discipline

Every future Wiki-derived claim should record when material:
- page title
- page last-modified date
- target model/tool generation
- exact model/checkpoint/version if present
- whether official/current source corroborates it

Age labels:
- `CURRENT_2026`
- `RECENT_BUT_VERSIONED`
- `LEGACY_SDXL`
- `LEGACY_SD1X`
- `UNKNOWN_AGE`

A page being edited in 2026 does **not** prove every paragraph was rewritten in 2026.

---

## 7. Final site assessment

| Dimension | Verdict |
|---|---|
| Japanese practical breadth | VERY HIGH |
| Current Forge/Anima operations | HIGH |
| Failure/troubleshooting value | HIGH |
| Prompt hypothesis generation | HIGH |
| LoRA/training practical ideas | MEDIUM-HIGH |
| Exact-model authority | MEDIUM-LOW unless independently verified |
| Canonical semantic authority | LOW / REJECT |
| Risk of stale legacy carryover | HIGH |
| Value for DanbooruTagTool KNOWLEDGE | HIGH with version/evidence gating |

Final policy:
**Use this Wiki aggressively as a Japanese practical observation and troubleshooting source, but never ingest it raw into canonical dictionary or exact-model rules. Version-gate, source-rank, and cross-check high-impact claims.**
