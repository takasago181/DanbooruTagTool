# としあきdiffusion Wiki — Coverage Map

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `SITE_COVERAGE_V1 / VIDEO_EXCLUDED`

Target: https://wikiwiki.jp/sd_toshiaki/

## 0. Coverage statement

本調査は以下を実施した。

- FrontPage / Menu / page category structure の横断確認
- RecentChanges を用いた2026-era更新箇所の確認
- project-relevant model/tool/prompt/training/troubleshooting pages の本文深掘り
- high-impact claims の official/current source 照合
- legacy pages の識別
- 動画生成・動画補間・動画モデル/LoRAはユーザー指示により除外

これは「Wiki内の動画以外の全ページ全行を逐語精読した」という意味ではない。DanbooruTagToolの現在目的に影響する領域を優先し、カテゴリ横断 + 高関連ページ深掘りで coverage を確保した。

---

## 1. Coverage legend

- `DEEP` — 本文の重要節まで確認し、project rulesへ具体的に反映
- `CROSSCHECKED` — 本文 + official/primary source照合
- `SURVEYED` — page/category/functionを確認、重要点を抽出
- `LEGACY_SURVEY` — 古い情報として位置づけを確認
- `EXCLUDED_VIDEO` — 動画系につき除外
- `LOW_RELEVANCE` — project current goalへの寄与が低く優先度を下げた

---

## 2. Site / navigation / freshness

| Area | Coverage | Relevance | Notes |
|---|---|---:|---|
| FrontPage | DEEP | HIGH | Wiki自体が古い/誤情報残存リスクを明記 |
| Menu / category structure | SURVEYED | HIGH | 全体横断の基準 |
| RecentChanges | DEEP | HIGH | 2026 refreshとlegacy coexistence確認 |
| edit/history-oriented site metadata | SURVEYED | MEDIUM | page modified dateをfreshness hintとして使用 |

---

## 3. UI / runtime / package ecosystem

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| Forge Neo | CROSSCHECKED | VERY HIGH | current practical source; exact capabilityはofficial GitHub優先 |
| A1111/WebUI general | SURVEYED + LEGACY | MEDIUM | parser/syntax/historyに有用、現行Neoへ自動移植禁止 |
| ComfyUI | DEEP | HIGH | workflow/metadata/reproducibilityに有用 |
| extension compatibility | DEEP | HIGH | exact build/version identity必須 |
| install/update basics | SURVEYED | LOW-MEDIUM | project already established; only current compatibility rules retained |
| general hardware setup | SURVEYED | LOW | current KNOWLEDGE goalでは低優先 |

---

## 4. Image model families

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| Anima | CROSSCHECKED | VERY HIGH | official cardでNL/tag/order/negative等を再検証 |
| Illustrious XL | CROSSCHECKED | VERY HIGH | generic/old guidanceとexact derivativeを分離 |
| WAI Illustrious | CROSSCHECKED | VERY HIGH | v17 author card優先; long-negative conflict発見 |
| legacy SDXL checkpoints | SURVEYED | MEDIUM | family history/hypothesis用 |
| SD1.x models | LEGACY_SURVEY | LOW | current production guidanceに不採用 |
| unrelated modern model families | SURVEYED | LOW-MEDIUM | project target化までHOLD |
| video models | EXCLUDED_VIDEO | NONE | user instruction |

---

## 5. Prompt / semantic surface

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| Prompt main guide | DEEP | VERY HIGH | practical mindset/failure diagnosis useful |
| Prompt syntax / emphasis | DEEP | HIGH | tool/parser layerとして保持 |
| BREAK / AND | DEEP | HIGH | model semanticsと分離 |
| Danbooru語 | DEEP | VERY HIGH | underscore canonical vs space surface分離に有用 |
| Negative Prompt | CROSSCHECKED | VERY HIGH | current-vs-legacy conflict多数 |
| old universal Prompt/Negative recipes | LEGACY_SURVEY | HIGH risk | current exact-model baselineにはREJECT |
| seed | DEEP | HIGH | fixed-seed basic valid; Batch Cで拡張 |
| generic “best prompt” lists | SURVEYED | MEDIUM-LOW | hypothesis only |

---

## 6. Composition / control / assisted generation

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| ControlNet | DEEP + LEGACY_SPLIT | HIGH | assisted lane; old SD1.5 params segregated |
| OpenPose / pose control | SURVEYED | HIGH | geometry control, not semantic proof |
| regional prompting / Forge Couple context | CROSSCHECKED | VERY HIGH | actor/resource separation assisted lane |
| Dynamic Prompts | CROSSCHECKED | VERY HIGH | controlled variant enumeration candidate |
| inpaint/img2img | DEEP | HIGH | repair/postprocess evidence separated |
| ADetailer-related workflow references | SURVEYED | HIGH | postprocess confound principle already established |

---

## 7. Upscale / Hires / image quality

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| Hires.fix | CROSSCHECKED | VERY HIGH | second-stage intervention; base vs rescue separate |
| denoise strength | DEEP | HIGH | higher intervention changes image more; exact values versioned |
| upscaler choice | SURVEYED | MEDIUM | aesthetic/quality, lower than semantics |
| high-resolution troubleshooting | DEEP | HIGH | crop/anatomy/composition confound useful |

---

## 8. Tagger / interrogator / metadata

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| WD1.4 Tagger | CROSSCHECKED | VERY HIGH | operational info useful; old ranking LEGACY |
| metadata / PNG info | DEEP | VERY HIGH | experiment traceability strongly adopted |
| image-to-prompt/tag extraction | SURVEYED | MEDIUM | observation helper, not truth |
| older tagger comparisons | LEGACY_SURVEY | MEDIUM | historical only |

---

## 9. LoRA / training

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| beginner LoRA guide | DEEP | HIGH | workflow heuristics; precise percentages not FACT |
| Anima LoRA guide | DEEP | HIGH | exact 2026 workflow but versioned |
| multi-concept LoRA | DEEP | VERY HIGH | entanglement/tag partition practical evidence |
| caption/tag effects | CROSSCHECKED | VERY HIGH | training annotation tradeoff; inference transfer bounded |
| training tips / loss | DEEP | MEDIUM-HIGH | seed/control useful; magic loss thresholds rejected |
| Difference LoRA | DEEP | MEDIUM | community hypothesis, not universal superiority |
| old LoRA method taxonomy | LEGACY_SURVEY | MEDIUM | history/versioned |
| video LoRA | EXCLUDED_VIDEO | NONE | user instruction |

---

## 10. Troubleshooting / FAQ

| Area | Coverage | Relevance | Decision |
|---|---|---:|---|
| reproducibility/hash/settings | DEEP | VERY HIGH | adopted |
| Prompt not working | DEEP | VERY HIGH | diagnostic tree corroboration |
| hand/anatomy errors | DEEP | VERY HIGH | negative-hidden-body-part risk useful |
| blur/overweight/overprompt | DEEP | HIGH | practical anti-support evidence |
| resolution/composition problems | DEEP | HIGH | visibility/geometry confound |
| extension/tool errors | SURVEYED | MEDIUM | only exact current tool issue if later needed |
| generic install FAQ | SURVEYED | LOW | not knowledge priority |

---

## 11. Adult / niche / Special relevance

The Wiki is not treated as a dedicated Special2788 semantic database, but several cross-cutting areas directly strengthen hard/niche knowledge:

- old anatomy Negative stacks can suppress/hide required unusual anatomy
- Hires can repair body structure after base failure
- actor separation and regional conditioning are assisted lanes
- visible body-part requirement can change whether concept is judgeable
- model/version mismatch can look like tag failure
- Prompt syntax tricks do not solve relation ownership
- LoRA can inject context/pose/style priors

Coverage: `DEEP_CROSS_CUTTING`, not `per-Special canonical`.

---

## 12. Legacy buckets identified

### `LEGACY_SD1X`
- 2022-era universal negative/prompts
- early A1111 tricks
- old ControlNet recipes
- SD1.x-specific quality/artifact vocabulary stacks

### `LEGACY_EARLY_SDXL`
- early generic SDXL/Illustrious recipes that conflict with current derivative cards

### `LEGACY_TAGGER_RANKING`
- pre-Kagami/CL era “best WD model” ranking

### `LEGACY_TOOL_CAPABILITY`
- old statements about what Forge/Control/regional extensions cannot support before later updates

These remain useful historical evidence but are blocked from automatic production-rule promotion.

---

## 13. High-value pages/areas for future revisit

If #44 later needs more depth, revisit exact sections rather than re-reading the whole Wiki:

1. Anima — exact relation/multi-character examples
2. Illustrious/WAI — version-specific Prompt/Negative changes
3. Prompt syntax — parser behavior changes by current UI build
4. FAQ — action/visibility/anatomy failure cases
5. Hires/upscale — postprocess rescue conditions
6. LoRA caption/multi-concept — entanglement diagnostics
7. Dynamic Prompts — controlled experiment enumeration
8. WD Tagger — only for operation; evaluator ranking should use current primary sources

---

## 14. Site-wide final coverage verdict

The site was covered broadly enough to establish a durable project policy:

**Use aggressively for Japanese practical operations/failure-mode hypotheses; verify exact model/tool claims independently; quarantine legacy advice; never use as canonical semantic authority.**

The strongest project contribution is not a single Prompt recipe. It is the collection of operational failure modes, historical context, tool-layer distinctions, and Japanese workflow observations that complement exact author sources.
