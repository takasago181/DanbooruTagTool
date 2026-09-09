# Stage10 PROMPT hard-target family source ledger

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: evidence ledger. **Not production specification.**

## 1. Purpose

`STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md` の根拠を追跡する。
公式・作者・日本語実践・仮説を混ぜない。

---

## 2. Official / author sources

### S1 — WAI Illustrious SDXL v17 mirror carrying author instructions
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Evidence: `AUTHOR_GUIDE`
- Key points:
  - Steps 15–30
  - CFG 5–7
  - Euler a
  - 1024x1024 より大きい原寸推奨
  - positive quality example: `masterpiece, best quality, amazing quality`
  - negative example: `bad quality, worst quality, worst detail, sketch, censor`
  - quality/aesthetic tag を盛りすぎない
  - overly long negative は quality低下 / blur の原因になり得ると明記
  - v17 で background color relevance / Hires.fix limb correction 改善を説明
- Caution:
  - Hugging Face mirror であり、source link は WAI0731 の Civitai 系を示す。production FACT 化時は可能なら作者一次ページ再照合。

### S2 — NoobAI XL 1.1 official README
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Evidence: `OFFICIAL_FACT`
- Key points:
  - native tags caption
  - caption order = `<1girl/1boy/1other/...>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`
  - quality prefix / negative example
  - CFG / Steps / Euler a / resolution recommendation
- PROMPT relevance:
  - Special placement を明示的な training-caption lane として監査できる

### S3 — Illustrious XL v1.1 official model card
- URL: https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1
- Evidence: `OFFICIAL_FACT`
- Key points:
  - v1.1 を v1.0 より natural-language focused refined model と説明
  - high-resolution generation / official generation guideへの導線
- PROMPT relevance:
  - Illustrious lineageを booru-only と固定しない
  - version差を保持する

### S4 — Illustrious XL v2.0 official model card
- URL: https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0
- Evidence: `OFFICIAL_FACT`
- Key points:
  - official platformで high-res / natural-language promptingを提供
  - STABLE checkpointはgeneration安定性改善を意図
- Caution:
  - DanbooruTagToolの現行対象family/versionと完全一致するとは限らない。WAI派生へ直接一般化しない。

### S5 — Anima official model card
- URL: https://huggingface.co/circlestone-labs/Anima
- Evidence: `OFFICIAL_FACT`
- Key points:
  - Danbooru-style tags / natural-language captions / mixで学習
  - tag order = `[quality/meta/year/safety] [count] [character] [series] [artist] [general tags]`
  - tags within section arbitrary order
  - natural languageはdescriptiveに。pure NLなら2文以上程度を推奨
  - tags + NLを混在可能
  - multiple charactersではcharacter nameだけでなくbasic appearance記述を強く推奨
  - random tag dropout
  - Aesthetic versionではquality tag不要でもよく、score tag過積載でslop方向へ押し得る
  - weightingは動作するがtypical SDXLより高いweight例を提示

---

## 3. Japanese community evidence

### J1 — Anima multiple-character experiment
- URL: https://note.com/ulyssesx00/n/n8f6a2c961e7c
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - natural-language centered promptで3人を扱う検証
  - appearance / relationを文章で分離
  - character consistencyが比較的維持されたという実践報告
- Use:
  - appearance-anchor / relation support仮説の補強
- Limitation:
  - Turbo LoRA使用、single-author test。base Anima universal factではない。

### J2 — Anima multi-character natural-language test
- URL: https://note.com/hkmclab/n/n7611426be16a
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - natural language + tagsで複数人物を描き分ける検証
  - quality tagをcharacter promptから分離する運用例
- Use:
  - character blockとshared composition blockを分ける設計候補

### J3 — Anima location / multi-character prompt experiment
- URL: https://note.com/stray_dog0012/n/n6576baad72c1
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - prompt-onlyで左右位置・属性分離がある程度可能という報告
- Use:
  - Prompt-only ceilingを最初から低く固定しない根拠
- Limitation:
  - model/workflow固有。再現性はStage10で要確認。

### J4 — WAI-Illustrious -> WAI-ANIMA migration note
- URL: https://note.com/nonb0716/n/nc7644494c360
- Evidence: `COMMUNITY_JA`
- Observed claims:
  - IllustriousとAnimaでprompt作法・negative感度・embedding互換性が違うという実践報告
  - Animaでは従来SDXL用embeddingをそのまま流用できないケース
- Important conflict:
  - 同記事では複数キャラ分離にForge Couple必須という強い主張あり。
  - J1/J2/J3のprompt-only successful reportsと衝突。
- Decision:
  - `CONFLICT / CONTROLLED_AB_REQUIRED`
  - 「Animaはprompt-onlyで十分」「Forge Couple必須」のどちらもproduction factにしない。

### J5 — Anima role-block prompt design
- URL: https://note.com/dn0288/n/n76c3eae57d68
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - Character Anchor / Outfit Lock / Pose Contract / Variation Slotの役割分離が扱いやすいという実践報告
- Use:
  - DanbooruTagToolのinternal block architectureとの親和性が高い
- Limitation:
  - hard-target専用検証ではない。

### J6 — Illustrious derived checkpoint overview
- URL: https://note.com/kei_aono/n/n08d5451cdab5
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - Illustrious派生間でprompt adherence / color / style / expressionに差が大きい
- Use:
  - Illustrious familyを単一挙動に潰さない補強
- Limitation:
  - 2025年時点の記事であり、現行WAI v17 direct evidenceではない。

### J7 — Illustrious tag/prompt practical guide
- URL: https://note.com/kazumu/n/n6390a899bdce
- Evidence: `COMMUNITY_JA`
- Observed claim:
  - Danbooru tag構文・順序の実践整理
- Use:
  - community operation reference only
- Limitation:
  - official specificationではない。モデル/version差を超えて一般化しない。

---

## 4. Evidence conflicts worth preserving

### C1 — Anima multi-character separation
Evidence A:
- official model card: appearance description is important for multiple characters
- J1/J2/J3: natural-language or hybrid Promptで一定のmulti-character separation成功

Evidence B:
- J4: Forge Coupleの領域指定が必須という実践主張

PROMPT verdict:
- `HOLD / CONTROLLED_AB_REQUIRED`
- model version / Forge Neo implementation / resolution / number of actors / relation complexity / LoRA有無を固定して比較

### C2 — Quality tags in Anima
Official:
- base supports quality / score tags
- Aesthetic can omit quality tags; score-heavy can push toward slop

Community:
- score_9/8/7を積極利用する運用も存在

PROMPT verdict:
- `PROFILE_SPECIFIC`
- Base / Aesthetic / Turbo / derivativeを分離

### C3 — WAI long negative
Author guide:
- overly long negative can reduce quality / increase blur

Existing generic community practice:
- long negative templates are widely reused in SDXL workflows

PROMPT verdict:
- WAI v17ではgeneric long-negative inheritanceを禁止仮定にする
- Stage10で minimum vs expanded を比較

---

## 5. Source-quality lessons

1. Official model cardがある場合、communityより上位。
2. 同じfamily名でもderived checkpointを混ぜない。
3. prompt例だけでなく model version / LoRA / CFG / steps / sampler / resolutionを保存する。
4. hard-targetでは成功例だけでなく失敗例を保存する。
5. community consensusが割れる場合、平均化せずCONFLICTとして残す。
6. 日本語圏知見は独立laneとして保持し、英語圏の翻訳版扱いにしない。

---

## 6. Current evidence gaps

- WAI v17 hard-target-specific controlled examples
- Illustrious base/v1.1 hard relational scene official guidance
- NoobAI 1.1 canonical-vs-alias controlled evidence
- Anima Base/Aesthetic/Turbo hard relation comparison
- family別 minimum negative
- family別 Prompt-only ceiling
- hard-targetに対するHires.fix前後semantic retention
- multi-Special + body-site binding + object integrityの同時成立

These stay `HOLD` until Stage10 or stronger evidence.

---

## 7. Boundary

- This ledger is evidence storage, not a production rule.
- No explicit hard-target completion Prompt is stored here.
- No #32 / #44 authority is overridden.
- No Stage10 production image A/B is started.
