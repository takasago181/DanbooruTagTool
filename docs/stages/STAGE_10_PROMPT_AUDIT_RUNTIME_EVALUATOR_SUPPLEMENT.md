# Stage10 Prompt Audit — Runtime & Evaluator Supplement

最終更新: 2026-09-09

## Purpose

`STAGE_10_PROMPT_AUDIT_KNOWLEDGE_RESERVOIR.md` の補遺。

本書は **Prompt以外の処理が画像結果・監査結果を変える要因** と、**自動評価器を過信しないための知識** を集約する。

production仕様ではない。Stage10での独立監査、failure切り分け、controlled A/B設計に使用する。

---

## 1. Base generation と post-processing を分離する

Promptの性能を監査する場合、最終PNGだけを見ると「Promptが成功した」のか「後段補正が成功した」のか分からない。

最低でも以下を別処理として扱う。

1. base txt2img generation
2. Hires.fix / second pass
3. ADetailer / local inpaint
4. ControlNet / pose/depth等のcontrol
5. regional conditioning / Forge Couple
6. manual img2img / inpaint
7. upscaler-only処理

### Audit rule

可能なら `BASE_OUTPUT` と `FINAL_OUTPUT` を両方保存する。

最終画像だけでPromptのsemantic fidelityを採点しない。

---

## 2. Hires.fix is a second generation pass — `OFFICIAL_FACT`

AUTOMATIC1111公式WikiはHires.fixを、低解像度で一度生成し、upscale後にimg2img相当のsecond passでdetailsを追加する処理として説明する。[R01]

つまりHires.fixは単なる画像拡大ではない。

### Audit implications

- Hires.fix ON/OFFは別生成条件。
- denoising strength、hires steps、upscalerを必ず保存する。
- baseで成立していた局所関係がsecond passで変化する可能性、逆にbase破綻がsecond passで修復される可能性を区別する。
- WAI v17作者mirror自身もHires upscaleがlimb correctionへ影響し得ると説明しているため、WAIの「Promptによる人体成立率」を測る時にHires結果だけで判定しない。[R02]

### Candidate labels

- `BASE_PASS`
- `HIRES_RETAINED`
- `HIRES_REPAIRED`
- `HIRES_DAMAGED`
- `HIRES_SEMANTIC_DRIFT`

---

## 3. ADetailer is detect + mask + inpaint — `OFFICIAL_FACT`

ADetailer公式repoは、自動detect / masking / inpaintingを行うextensionと明示している。[R03]

実装上も、ADetailerはimg2img inpaint処理を作り、独立した `ad_prompt` / `ad_negative_prompt`、denoising strength、steps、CFG、ControlNet等を持てる。[R04][R05]

### Critical audit implication

ADetailer後の顔・手・人物局所を見て、base Promptがその局所を正しく生成したと結論しない。

### Required metadata

- ADetailer enabled/disabled
- detector model
- detection threshold
- mask dilation/erosion
- inpaint only masked / padding
- denoising strength
- ADetailer prompt
- ADetailer negative prompt
- ADetailer sampler/steps/CFG override
- ADetailer ControlNet
- processing order when multiple detectors are enabled

### Special case

ADetailerのPromptがblankならmain promptを継承し、`[PROMPT]`等で元Promptを展開できる機構がある。[R05]

したがって、main promptだけ保存してもlocal inpaintの実Promptを一意に復元できない場合がある。

### Audit labels

- `BASE_FAILURE_AD_REPAIRED`
- `BASE_SUCCESS_AD_RETAINED`
- `AD_ATTRIBUTE_DRIFT`
- `AD_IDENTITY_DRIFT`
- `AD_NOT_APPLICABLE`

---

## 4. CFG=1 and Negative Prompt — model/runtime dependent trap

Hugging Face Diffusersのstandard classifier-free guidance実装では、`guidance_scale = 1` は「classifier-free guidanceを行わない」状態と定義され、CFGは `>1` で有効化される。[R06][R07]

Anima公式はTurboを CFG 1 / 8–12 stepsで使うよう案内する。[R08]

### Audit implication

`Anima Turbo + CFG 1` でNegative Promptの効果をSDXLのCFG 5–7と同じ前提で監査しない。

### Important limitation

Forge NeoのAnima実装やNegPiP等のextensionがstandard Diffusersと完全同一とは限らない。

したがって:

- `STANDARD_CFG_THEORY`: CFG=1なら通常CFG negative conditioningは働かない/大幅に意味が変わる
- `EXACT_FORGE_ANIMA`: controlled test required

として分離する。

### Test candidate

同一Anima Turbo checkpoint/seedで:

1. Negative empty
2. fixed Negative
3. CFG 1 vs supported higher CFG only where model/runtime permits
4. NegPiP等extension OFF/ONを別実験

一つのA/Bで複数条件を変えない。

---

## 5. LoRA is a model intervention, not a decorative Prompt token

LoRA使用時は、base checkpointだけのPrompt-following能力を測っているわけではない。

複数LoRAの研究でも、単純に複数adapterを組み合わせるとconcept間interferenceが生じ、visual qualityやindividual concept fidelityが低下し得ることが報告されている。[R09]

これはexact anime LoRAへの定量則ではなく `RESEARCH_BACKGROUND` だが、監査分離には十分重要。

### Required metadata

- LoRA file name
- file hash / version
- base model compatibility
- trigger words
- network weight
- text encoder weight / UNet weightが別なら両方
- multiple LoRA order
- multiple LoRA count
- any block-weight / LBW configuration

### Audit lanes

- `NO_LORA_BASELINE`
- `SINGLE_LORA`
- `MULTI_LORA`

を混ぜない。

### Failure classes

- `LORA_STYLE_DOMINANCE`
- `LORA_CONCEPT_INTERFERENCE`
- `LORA_TRIGGER_COLLISION`
- `LORA_IDENTITY_DRIFT`
- `LORA_BASE_SPECIAL_SUPPRESSION`

### HOLD

「weight 0.Xなら安全」等のglobal閾値は設定しない。LoRAごとに学習内容・rank・base・triggerが違う。

---

## 6. WD EVA02 v3 evaluator coverage has a hard vocabulary/data boundary

SmilingWolf `wd-eva02-large-tagger-v3` 公式model cardより。[R10]

- ratings / characters / general tagsを出力
- Danbooru dataset由来
- **600 images未満のtagはtraining vocabularyからfilter**
- validation operating point: P=R threshold 0.5296, F1 0.4772
- dataset/tag updateは2024-02-28まで

### Direct audit consequences

1. rare Special2788が600枚未満なら、そのexact canonicalをWD EVA02 v3が直接scoreできない可能性が構造的に高い。
2. canonicalがvocabularyに無い時、近接一般tagのconfidenceが高くても、target Special成立の証明にはならない。
3. taggerが個々のtagを認識しても、**actor-target binding / attribute ownership / relation** を独立tag confidenceだけから証明できるとは限らない。
4. model cardの0.5296は全体validation上のP=R operating pointであり、DanbooruTagToolのrare/composite target classに最適なwinner thresholdとは限らない。

### Required pre-routing check

各Specialについて先に:

- exact target vocabulary present?
- canonical spelling exact?
- Alias only?
- component tags only?
- target frequency/training eligibility known?
- evaluator questionとhuman semantic questionは同一か?

を確認する。

### Routing rule candidate

- exact vocabulary + direct visual target + calibrated class → auto-routing候補
- vocabulary absent → `REVIEW_UNSUPPORTED`
- component tags only → `REVIEW_SEMANTIC`
- relation/binding question →原則human/stronger evaluator lane

---

## 7. A tagger threshold is not a universal semantic winner threshold

WD EVA02 v3のglobal validation thresholdを、そのままA/B winner判定marginへ変換しない。[R10]

### Why

- tagごとのclass imbalanceが違う
- rare targetはmodel vocabularyから除外され得る
- confidence calibrationはtag/categoryで同一とは限らない
- Special testでは「tagが存在するか」以外にbinding/retention/visibilityを問う

### Stage10 calibration candidate

thresholdは最低でもtarget classごとに分ける。

- direct single-tag presence
- count
- simple attribute
- composite
- relation
- Alias-equivalence
- support-dependency
- multiple-Special retention

後半4種はmachine-decidableでない可能性を許容する。

---

## 8. Evaluator blind spot taxonomy

自動評価器に対して、画像failure taxonomyとは別に以下を記録する。

1. `VOCAB_ABSENT`
2. `VOCAB_ALIAS_ONLY`
3. `TARGET_TOO_RARE_FOR_EVALUATOR`
4. `COMPONENT_ONLY_DETECTION`
5. `RELATION_NOT_EXPRESSED`
6. `BINDING_NOT_EXPRESSED`
7. `COUNT_AMBIGUOUS`
8. `OCCLUDED_TARGET`
9. `CROPPED_TARGET`
10. `CONFIDENCE_NEAR_TIE`
11. `EVALUATOR_MODEL_DISAGREEMENT`
12. `HUMAN_EVALUATOR_DISAGREEMENT`

### Principle

`REVIEW` は失敗ではない。

評価器が答えられないsemantic questionを無理にwinnerへ変換することの方が監査上の失敗。

---

## 9. Resolution / aspect ratio is part of semantic test conditions

NoobAI、WAI、Illustrious、Animaはいずれも推奨resolution/運用が異なる。

### Audit rule

- same family A/Bではresolution/aspect ratio固定
- family cross-comparisonでは各family native/recommended条件を使う「実戦比較」と、同一条件を使う「controlled comparison」を分離
- full-body/upper-body等のvisibility評価ではaspect ratioが結果へ強く関与し得るため、Prompt tagだけの効果として扱わない

### Two valid experiment modes

1. `CONTROLLED_SAME_SETTINGS`
   - model以外を極力固定
   - pure model differenceを見やすい
2. `FAMILY_OPTIMAL_BASELINE`
   - 各familyの推奨sampler/CFG/resolutionを使用
   - user実戦能力を比較

両者の結論を混ぜない。

---

## 10. Seed robustness and audit confidence

1 seedの成功/失敗は、Prompt ruleの確定には弱い。

Stage10では少なくとも複数seedを使い、以下を区別する。

- `CONSISTENT_SUCCESS`
- `SEED_SENSITIVE_SUCCESS`
- `CONSISTENT_FAILURE`
- `MIXED_FAILURE_CLASS`

### Audit principle

同じA/Bで、seedごとに違うfailure classが出た場合は単純な勝率だけに圧縮しない。

例:

- seed A: target omission
- seed B: target present but wrong binding

は「2/2 failure」だけでは原因が消える。

failure distributionを保持する。

---

## 11. Audit order — external confound elimination ladder

Prompt自体を疑う前に、以下の順で確認する。

1. metadata completeness
2. exact checkpoint/version
3. resolved Prompt correctness
4. parser/template expansion
5. base generation vs post-processing
6. LoRA/control extension status
7. evaluator vocabulary/support
8. visibility/crop
9. concept recognition
10. binding/relation
11. Prompt density/support competition

これにより「ADetailerで直った顔」をPrompt成功と誤認したり、「WD14にtagが無い」ことをPrompt failureと誤認するのを防ぐ。

---

## 12. Additional HOLD backlog

controlled A/Bまたはcoverage調査が必要:

- exact Forge Neo Anima Turbo CFG=1でNegativeがどの程度無効/変質するか
- ADetailer ON/OFFでSpecial判定が変わるケース
- Hires.fixがrare/composite Special retentionへ与える影響
- multiple LoRA × multiple Specialのinterference
- WD EVA02 / Kagami / CL Tagger間のfinal Special2788 coverage比較
- tagger confidence calibrationのtarget-class別最適化
- final 2788 dictionary freeze後のevaluator vocabulary snapshot

---

## Sources

- **[R01] AUTOMATIC1111 Features — Hires.fix / prompt editing**  
  https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features

- **[R02] WAI Illustrious SDXL v17 author-text mirror**  
  https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

- **[R03] ADetailer official repository**  
  https://github.com/Bing-su/adetailer

- **[R04] ADetailer implementation — separate inpaint processing / prompts**  
  https://github.com/Bing-su/adetailer/blob/main/scripts/%21adetailer.py

- **[R05] ADetailer Advanced prompt behavior (`[PROMPT]`, `[SEP]`, blank prompt)**  
  https://github.com/Bing-su/adetailer/wiki/Advanced

- **[R06] Hugging Face Diffusers Stable Diffusion pipeline — CFG=1 means no classifier-free guidance**  
  https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion.py

- **[R07] Hugging Face Diffusers SDXL pipeline — same CFG semantics**  
  https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion_xl/pipeline_stable_diffusion_xl.py

- **[R08] Anima official model card — Turbo CFG1 / 8–12 steps**  
  https://huggingface.co/circlestone-labs/Anima

- **[R09] Training-Free Multi-Concept LoRA Composition with Prompt-Aware Weighting** — Tsoumplekas et al., 2026; research background for multi-LoRA interference  
  https://arxiv.org/abs/2606.03792

- **[R10] SmilingWolf WD EVA02-Large Tagger v3 official model card**  
  https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3

## Boundary

本書は自動scoring threshold、production Negative、LoRA weight、Hires/ADetailer defaultを決めない。

目的は「Promptの失敗」と「runtime/postprocess/evaluatorの失敗」を混同しないこと。