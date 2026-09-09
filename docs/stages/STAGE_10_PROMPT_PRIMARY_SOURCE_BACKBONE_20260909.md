# Stage10 PROMPT primary-source backbone

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: evidence-routing contract candidate. **Not production specification.**

## Purpose

高品質・高難度・ニッチ/複合成人向け画像を狙うDanbooruTagToolについて、PROMPT班が今後どの主張をどの種類の一次情報で検証するかを固定する。

PROMPT知識は以下の5層に分離する。

1. `SEMANTIC_AUTHORITY`
   - Danbooru Wiki / alias / implication / tag group
   - canonicalの意味幅、近接概念、body-site、relation、poseの語義確認
2. `MODEL_AUTHORITY`
   - Hugging Face公式model card、作者公式Civitai/公式サイト
   - caption structure、推奨settings、quality/meta/safety、natural-language対応、version差
3. `RUNTIME_AUTHORITY`
   - Forge/A1111/拡張の公式GitHub
   - parser、regional conditioning、ControlNet、ADetailer、Dynamic Prompts等の実装仕様
4. `FAILURE_RESEARCH`
   - arXiv / peer-reviewed or primary research
   - semantic neglect、attribute binding、relation/composition failure、spatial control、evaluator限界
5. `COMMUNITY_EVIDENCE`
   - としあきWiki、AIArtRecipe、Note、Reddit等
   - 実践例・失敗例・日本語運用。一次情報と照合して候補化

## Source precedence

同じ主張が衝突した場合:

`exact model/version official > exact extension official > Danbooru/e621 semantic authority > research background > controlled community evidence > anecdotal community evidence`

ただし、意味論はDanbooru/e621がmodel cardより優先し、runtime behaviorはextension repoがmodel cardより優先する。分野を跨いで単純順位付けしない。

## Key rules

- `tag exists` != `model recognizes tag`
- `model recognizes tag` != `correct actor/site binding`
- `Prompt contains token` != `image realizes intent`
- `community success example` != `production rule`
- `training caption order` != `universally optimal inference order`
- `assisted-control success` != `PROMPT_ONLY success`
- `Danbooru alias/implication` != `model-response equivalence`
- exact checkpoint/versionを保存しない知識はmodel-specific FACTへ昇格させない

## Current priority sources

### Model official
- Anima: https://huggingface.co/circlestone-labs/Anima
- NoobAI XL 1.1: https://huggingface.co/Laxhar/noobai-XL-1.1
- Illustrious XL v1.1: https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1
- Illustrious official platform: https://www.illustrious-xl.ai/
- WAI v17: author-linked Civitai / trusted mirror; exact author page再照合を優先

### Semantic
- Danbooru/Safebooru wiki pages and tag groups
- e621 wiki only as supplemental non-human/creature taxonomy, never as Danbooru canonical replacement

### Runtime/control
- Forge Couple: https://github.com/Haoming02/sd-forge-couple
- Dynamic Prompts: https://github.com/adieyal/sd-dynamic-prompts
- ADetailer: https://github.com/Bing-su/adetailer
- Regional Prompter: https://github.com/hako-mikan/sd-webui-regional-prompter
- ControlNet WebUI: https://github.com/Mikubill/sd-webui-controlnet

### Research
- Attend-and-Excite: https://arxiv.org/abs/2301.13826
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- Object-Attribute Binding in T2I: https://arxiv.org/abs/2404.13766
- MultiDiffusion: https://arxiv.org/abs/2302.08113
- Concept Conductor: https://arxiv.org/abs/2408.03632

## Product interpretation

最終目的は「辞書として正しいPrompt」ではなく、

**semantic safety + model realization rate + binding correctness + visual quality + low user repair burden**

である。

従ってPROMPT班は、community knowledgeを捨てずに一次情報で補正し、Stage10で実画像へ接続する。

## Boundary

- #32 verdictを変更しない
- KNOWLEDGE #44 corpusを変更しない
- production ruleへ未検証知識を昇格しない
- Stage10 production A/Bを開始しない
