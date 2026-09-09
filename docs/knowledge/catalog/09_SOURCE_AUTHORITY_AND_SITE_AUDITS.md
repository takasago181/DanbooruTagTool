# 09 — Source Authority / Site Audits

## 基本ルール

**サイト単位で信用しない。主張の種類ごとに権限を分ける。**

### canonical meaning
最優先:
1. Danbooru current Wiki
2. active Alias / Implication records
3. project canonical data

### exact model behavior
最優先:
1. exact model author card
2. author reply/discussion
3. controlled exact-model practical evidence

### tool behavior
最優先:
1. official README/docs
2. official issues/version reports

### general mechanism
最優先:
1. primary paper / arXiv / CVF / OpenReview
2. controlled reproducible studies

### practical failure discovery
- AIArtRecipe
- としあきdiffusion Wiki
- Civitai/Tensor.Art creator reports
- HF community discussions
- Reddit等

これらはhypothesis generatorであり、canonical truthではない。

---

## AIArtRecipe

正式評価:
**ADOPT AS PRACTICAL OBSERVATION CORPUS / REJECT AS CANONICAL AUTHORITY**

強み:
- niche/adult generationの成功・失敗例
- wrong-site / wrong-source / wrong-count等を文章で残す
- WAI/Illustrious/Anima等の実践

弱み:
- canonical / alias / free phrase / typoが混在
- exact model versionやseed/sample数不足の記事あり
- typoに起因する誤結論も確認済み

使い方:
- failure mechanism
- alternate phrase候補
- A/B hypothesis

原本:
- `research/AIARTRECIPE_SITE_AUDIT_20260909.md`
- `research/AIARTRECIPE_PRACTICAL_FINDINGS_20260909.md`

---

## としあきdiffusion Wiki

正式評価:
**ADOPT AS JAPANESE COMMUNITY PRACTICAL / OPERATIONS CORPUS**

強み:
- Forge Neo / ComfyUI / Prompt / Negative / Hires / Control / LoRA / troubleshootingが広い
- 日本語実運用のfailure知識が豊富

弱み:
- 2022–2023 legacyと2026現行情報が同居
- community heuristicとauthor factが混ざる
- old universal Negative等を現行WAIへ流用すると危険

分類:
- PRACTICAL_CURRENT
- PRACTICAL_VERSIONED
- COMMUNITY_HEURISTIC
- LEGACY
- REJECT_FOR_EXACT_MODEL

原本:
- `research/TOSHIAKI_WIKI_SITE_AUDIT_20260909.md`
- `research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `research/TOSHIAKI_WIKI_COVERAGE_MAP_20260909.md`

---

## Hugging Face

Model card / author statement > community discussion。

- WAI17: author cardがexact settings/Negative/Hiresの最高権限
- NoobAI: training corpus/caption order/inferenceの最高権限
- Anima: formatting/tag dropout/NL/Gelbooru/multi-character guidanceの最高権限

community discussionsはbinding failure等の発見に有用だが、成功率のFACTにはしない。

原本: `research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`

---

## Danbooru / e621

Danbooru = canonical semantic authority。
e621 = NoobAI向けsecondary vocabulary/training-surface source。

e621はDanbooru canonicalを上書きしない。

原本:
- `research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`

---

## 恒久権限表

詳細: `research/SOURCE_AUTHORITY_MATRIX_20260909.md`

言語はevidence rankではない。日本語/英語/中国語/韓国語等を同じ基準で評価する。