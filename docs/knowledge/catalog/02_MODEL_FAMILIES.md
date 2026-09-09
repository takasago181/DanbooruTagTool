# 02 — Model Families

## WAI Illustrious v17 — 現在の最優先

### exact author facts
- 推奨UI: Forge Neo
- Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- VAE内蔵
- 元解像度は1024x1024より大きいarea推奨。例1024x1344
- Positive品質baseline: `masterpiece, best quality, amazing quality`
- Negative baseline: `bad quality, worst quality, worst detail, sketch, censor`
- quality/aestheticタグ過多・長いNegativeは品質低下/blurの可能性
- Hiresが四肢を修正する場合があるため、baseとHiresを分離評価

### あなたの暫定local baseline
- Forge Neo
- Euler a
- 25 steps
- CFG 5
- portraitは1024x1344を第一候補
- fixed paired seed
- Hires OFF
- ADetailer OFF
- LoRA OFF
- regional/Control OFF

### WAI17でまだHOLD
- canonical vs Alias activation
- rare Special exposure
- broad+specific
- actor-target/body-site relation ceiling
- restraint topology
- machine/device functional relation
- tentacle ownership
- simultaneous Special/count ceiling
- visibility support効果
- unusual anatomy/count Negative ON/OFF
- LoRA x Special/support

原本: `research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`

---

## Illustrious XL family baseline

- Booru-oriented tag知識が強い。
- relation-rich sceneを単純なbag-of-tagsとして扱うのは危険。
- critical composition tagの競合に注意。
- derivativeごとの挙動は再検証が必要。

原本:
- `GENERATION_KNOWLEDGE_CORPUS.md`
- `research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`

---

## NoobAI XL 1.1 EPS

### exact knowledge
- Danbooru + e621 native tag captions
- CFG 5–6
- Steps 25–30
- Euler a
- 約1MP
- caption structure: count -> character -> series -> artists -> special tags -> general tags -> other

### 意味
- Special-before-Generalはexact-model根拠が強い。
- e621 exposureは非人間/特殊解剖/fetish vocabularyのalternate-trigger仮説に有用。
- ただし現在のrare tagやSemanticがexact tokenとして学習済みとは限らない。

### HOLD
- canonical/Alias/e621 alternate trigger
- actor/body-site relation
- hard count
- camera/visibility placement
- anatomy Negative effect

---

## NoobAI V-Pred 1.0

- EPSとはprediction regimeが別。
- CFG 4–5 / Steps 28–35 / Euler系という別条件。
- EPSの画像結果をV-Predの証拠へ流用しない。

---

## Anima

### exact family knowledge
- tags + natural language + mixed caption
- lowercase / spaces中心
- Gelbooru form優先ケースあり
- random tag dropout
- Base / Aesthetic / Turboを分離
- multi-characterではidentity/basic appearanceの明示が有用

### 実践上の現在結論
- relation-heavy caseは `tag anchor + concise factual relation clause` をA/B候補にする価値が高い。
- 自然文だからbindingが解決するとは限らない。
- pronoun依存よりstable actor identifierを優先。

### HOLD
- tag-only vs concise hybridの実効差
- hard relation ceiling
- multi-actor ceiling
- unusual anatomy x Negative
- alternate trigger drift

---

## モデル間で安全に共有できる一般則

- relation != presence
- rare concept != one-seed failure
- Negativeはactive intervention
- concept数増加でcompositional burden増加
- LoRA/postprocess/controlはconfound
- evaluator coverageを先に確認

## 共有禁止

- exact Prompt order
- exact quality prefix
- exact Negative list
- camera placement
- weight
- Alias preference
- broad+specific benefit
- natural language superiority
- simultaneous Special ceiling