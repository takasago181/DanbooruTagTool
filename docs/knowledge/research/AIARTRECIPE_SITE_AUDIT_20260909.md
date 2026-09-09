# AIアートのレシピ（aiartrecipe.com）横断監査

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `SITE_AUDIT_V1 / TEXT_AND_IMAGE_ONLY`

## 0. Scope

対象サイト: https://aiartrecipe.com/

ユーザー指示により **動画系コンテンツは完全除外**。YouTube・動画生成・動画補間・動画LoRA等の記事は、サイトのナビゲーションに存在しても本監査の evidence に使用しない。

対象:
- Prompt / play / situation / body-part / character-attribute 記事
- model comparison
- image/T2I/image-edit/control articles
- ComfyUI / tagger / ControlNet 等の text-based tool articles
- LoRAやモデルの実用記事のうち、静止画生成知識に関係するもの

目的はサイトの文章を canonical 辞書として採用することではなく、**実生成の観察・失敗例・alternate trigger・support候補・model behavior仮説を抽出し、妥当性を独立検証すること**。

---

## 1. Site-level verdict

### Overall decision

**ADOPT AS PRACTICAL OBSERVATION CORPUS / REJECT AS CANONICAL AUTHORITY**

このサイトは DanbooruTagTool にとって有用である。特に価値が高いのは以下。

1. 成人向け・ニッチな Prompt を実際に生成している。
2. 成功画像だけでなく、wrong body-site / wrong source / wrong count / malformed implement / crop / model confusion 等の失敗を文章で残す記事が多い。
3. WAI / Illustrious / Anima 等、プロジェクト対象に近いモデルを扱う。
4. free-English relation phrase、broad+specific、Negative hack、ControlNet/LoRA assisted control 等、Stage10でA/B候補になる実践パターンが多い。
5. 日本語圏の実用知識源として、英語公式資料とは異なる「実際にどこで困るか」を提供する。

一方、以下の理由から semantic/canonical truth としては使えない。

- canonical tag / Alias / free phrase / author-made phrase が同じ一覧に混在する。
- exact model version が欠ける記事がある。
- fixed seed / sample count / all-output retention が無い比較が多い。
- visually good example を中心にした記事があり、母数や成功率が不明。
- typo や日本語意味説明の誤りが実際に存在する。
- LoRAやControlNetを使った成功が base checkpoint capability と混ざり得る。
- subjective model ranking と客観的能力評価が混在する。
- ライセンス/商用可否はモデル本体の一次ライセンス確認なしでは信用しない。

したがって default evidence class は `PRACTICAL`。

`CONTROLLED_PRACTICAL` へ昇格できるのは、少なくとも exact model/version、実設定、事前固定seed、比較変数、sample数、全結果/失敗の記録が揃う記事・実験だけ。

---

## 2. Site structure observed

サイトは Prompt 集だけではなく、少なくとも以下のレーンを持つ。

- プロンプト
  - プレイ
  - シチュ
  - キャラ属性
  - 部位パーツ
- 画像系
- モデル
- ツール
- コラム
- 動画系（**本監査では除外**）

2026-09-09時点で閲覧したページでは Promptカテゴリが多数を占め、成人向け特殊概念、モデル比較、自然言語、tagger、ControlNet、image-editまで広い。

これは一つの「Prompt百科」ではなく、**日本語圏の practical generation notebook 集**として読むべきである。

---

## 3. Evidence ingestion contract

AIアートのレシピ由来の claim を #44 へ取り込む場合、最低限次のフィールドを付ける。

- `article_url`
- `article_date / update_date`
- `model_family`
- `exact_checkpoint_version` or `UNKNOWN`
- `sampler / scheduler / steps / CFG / resolution` when available
- `seed_control`: fixed / visible / unknown
- `sample_count`: known / unknown
- `prompt_surface`
- `negative_surface`
- `lora/control/postprocess`
- `claimed_effect`
- `observed_failure`
- `canonical_status`: `CANONICAL / ALIAS / SEMANTIC / FREE_PHRASE / TYPO / UNKNOWN`
- `transfer_scope`: `SAME_VERSION / FAMILY_HYPOTHESIS / HISTORICAL / TEST_REQUIRED`
- `decision`: `ADOPT_PRACTICAL / VERIFY_FIRST / HOLD / REJECT`

### Hard prohibition

Site wording aloneで以下を決めない。

- canonical identity
- Alias equivalence
- implication / related
- intrinsic semantic support
- production Prompt grammar
- model-independent success rule
- evaluator ground truth

---

## 4. High-value articles and verdicts

### 4.1 Anima vs Illustrious natural-language comparison
Article: https://aiartrecipe.com/archives/4339
Date: 2026-06-03

Observed:
- tag + English natural-language mixで Anima と Illustrious/WAIを比較。
- right-side body-part/hand ownership、urine source-target、smartphone screen vs real scene、multi-character clothing/expression assignment等の relation-rich tasks を試している。
- right-side constraintは記事自身が約50%程度と記述。
- Animaでは自然文で source/target や screen/real の分離が改善した例を提示。

Audit:
- Anima側は `score_7, anime` 等を含め、Illustrious側では一部を除去しNegativeも別。厳密な同一Prompt比較ではない。
- fixed-seed / predetermined multi-seed protocolは明確でない。

Decision: `ADOPT_PRACTICAL`

Use:
- Anima relation/binding test case候補。
- `tag anchor + concise factual clause` 仮説を補強。

Do not infer:
- Animaが常にIllustriousよりrelationに強い。
- 50%を一般成功率とする。

Official cross-check:
Anima author card は tag + natural language + mixed prompting、multi-character descriptionを公式サポートしているため、方向性は整合。

### 4.2 Anima Turbo adult still-image examples
Article: https://aiartrecipe.com/archives/4555
Date: 2026-08

Observed:
- 12 steps / CFG 1 / Euler を使い複数の静止画sexual poseを生成。
- crop / face / compositionの不安定さも記述。

Decision:
- exact inference settings は official Anima Turbo card と一致するため、設定自体は `CORROBORATED`。
- 「最強」「Illustriousより高性能」等の総合rankingは `PRACTICAL_SUBJECTIVE`。

### 4.3 Stable Diffusion adult Prompt encyclopedia
Article: https://aiartrecipe.com/archives/1756
Updated: 2026-03-30

Strength:
- 性行為、体位、BDSM、機械、触手、体液、body-part等の候補表現が大量。
- Special2788外の free relation phrase を発見する source として強い。

Critical weakness:
- canonical Danbooru tag / Alias / Semantic-like phrase / ordinary English / typo が同列。

Examples needing verification:
- `beastiality` -> standard spelling/canonical candidate is `bestiality`
- `collorbone` -> `collarbone`
- `machine sex` 等は free/alternate phraseとして扱い、canonical扱いしない。

Decision: `ADOPT_AS_CANDIDATE_GENERATOR_ONLY`

### 4.4 WAI `nsfw / explicit` experiment
Article: https://aiartrecipe.com/archives/2546

Observed:
- WAI系で `nsfw` / `explicit` のpositive effectを比較。
- already-explicit sceneでは追加効果が小さいという観察。
- `SFW`での逆方向テストも実施。

Official cross-check:
WAI v17 author card は rating vocabulary を `general / sensitive / nsfw / explicit` と明記。

Important correction:
`SFW` は v17 author cardの official rating token ではなく、`general` と同一視できない。

Decision: `PRACTICAL_MODEL_SCOPED`

Reject generalization:
- `nsfw = R15`, `explicit = R18` のような日本のレーティング対応は非公式。
- 他familyへ自動移植しない。

### 4.5 Image-to-prompt/tagger comparison
Article: https://aiartrecipe.com/archives/1814

Observed:
- DeepDanbooru / WD14 / BLIP / JoyCaption系などを成人向け一画像で比較。
- absent object、誤ったfluid/location、過剰な自然文detail等の hallucination が記事中に見える。

Decision: `HIGH_VALUE_PRACTICAL_FAILURE_CASE`

Project lesson:
- image caption/tagger output は semantic truthではない。
- 一枚比較からWD14を総合推奨していても、Special2788 evaluator policyには転用しない。
- rare/relation/compositeはcoverage gateが必要。

### 4.6 BDSM / restraint prompts
Article: https://aiartrecipe.com/archives/3100

Observed:
- `shibari,bound` 系。
- whip geometryが崩れやすいことを明記。
- `wax play` の抽象語だけでは弱く、component phraseへ分解した例。

Decision: `ADOPT_PRACTICAL`

Project lesson:
- theme tag presence != implement topology。
- abstract play phraseが弱ければ visible components へ分解する価値がある。
- component phraseを intrinsic meaning へ自動昇格しない。

### 4.7 Sex machine
Article: https://aiartrecipe.com/archives/3125

Observed:
- `sex machine`を中心に machine/device sceneを生成。
- `machine sex`も効くとする実践記述。

Decision:
- `sex machine`: project canonical inventoryと照合可能な direct candidate。
- `machine sex`: `FREE_PHRASE / ALT_TRIGGER_CANDIDATE`。

Audit lesson:
device存在だけで成功判定せず、機能的接触、target body-site、actor/device relationを判定する。

### 4.8 Tentacle prompts
Article: https://aiartrecipe.com/archives/888

Observed:
- `tentacles` 単体でもsexual/restraint priorが出ると報告。
- `tentacle around arm/legs`, `tentacle in mouth`, `tentacle in pussy` 等の locational/free relation phrase。

Decision: `PRACTICAL / HISTORICAL_OR_VERSION_UNKNOWN`

Use:
- strong concept prior / ownership ambiguity / body-site phraseのtest候補。

Do not infer:
- site free phrase = Danbooru canonical。
- old/unknown WAI behavior = WAI v17 fact。

### 4.9 Object insertion
Article: https://aiartrecipe.com/archives/2529

Observed:
- broad `object insertion`だけだと implementが曖昧。
- actual object名やposeを足すと改善する例。
- specific toy/tagによっては broad generic phrase無しでも出る。

Decision: `ADOPT_PRACTICAL`

Strong alignment with #44:
- broad+specificは universal add ruleではなく controlled test。
- implement identityとbody-site/actionを分離。

### 4.10 Enema
Article: https://aiartrecipe.com/archives/4448
Date: 2026-06-20

Observed:
- plain Illustriousで `enema` がIV-like/wrong-siteへ崩れる例。
- body-site supportとNegative suppressionを試す。
- LoRAの方が安定したと報告。

Decision: `HIGH_VALUE_PRACTICAL_FAILURE`

Cautions:
- `no pussy` 等の suppression は anatomy collateral risk があり `TEST_REQUIRED`。
- LoRA successは base-model successではなく `LORA_ASSISTED_ONLY`。

### 4.11 Double penetration / group count
Article: https://aiartrecipe.com/archives/3573

Observed:
- `double penetration`に actor/count/group contextを加える。
- count/composition burdenが大きい。

Decision: `ADOPT_PRACTICAL`

Use:
- count support / actor-target decomposition test cases。

### 4.12 Clothing aside / pull
Article: https://aiartrecipe.com/archives/3905
Date: 2026-02-28

Observed:
- broad `clothing aside` と item-specific aside、pull系の違い。
- static displacement と active pulling が同じではない。

Decision: `ADOPT_AS_SEARCH/TRIGGER_CANDIDATES`

Canonical/semantic provenanceは別確認必須。

### 4.13 Full Nelson
Article: https://aiartrecipe.com/archives/440

Important exact scope:
- article explicitly uses `WAI-NSFW-illustrious-SDXLV12`。

Observed:
- `full nelson`、visibility support (`feet`)等。
- `anal full nelson` 等の free composition phrase。

Decision: `PRACTICAL_EXACT_OLD_VERSION / HISTORICAL`

Do not transfer directly to current WAI v17.

### 4.14 Piledriver / folded / upside-down
Article: https://aiartrecipe.com/archives/4472
Date: 2026-07-01

Observed:
- `folded`, `piledriver`, `upside-down`, legs-over-head等を比較。
- `piledriver` はsexual pose priorを強く持つ。
- `from above` が framingを大きく変える。
- `solo` を入れて unwanted partnerを抑える例。

Decision: `HIGH_VALUE_PRACTICAL`

Project lesson:
- trigger carries prior beyond dictionary gloss。
- viewpoint support is not neutral。
- broad suppression (`solo`) may alter target semantics and must be scenario-scoped。

### 4.15 Group sex / count failure
Article: https://aiartrecipe.com/archives/2314

Observed:
- `orgy/gangbang` は exact person count controllerではない。
- requested 3girls+3boysが2x2/4x4などへ崩れると記録。
- AnyTest等 assisted controlを提案。
- Negative `eyes` でface artifactを隠す hackも使用。

Decision:
- count failure observation: `ADOPT_PRACTICAL`
- AnyTest: `ASSISTED_CONTROL_CANDIDATE`
- `eyes` negative hack: `REJECT_AS_GENERAL_GUIDANCE`。エラーを解決せず視認性を隠す可能性がある。

### 4.16 Bukkake / fluid location article
Article: https://aiartrecipe.com/archives/1262

Critical experimental error:
- `ejucalation` / `ejecalation` の綴りを使い「効かない」趣旨の結論がある。
- 正しい語は `ejaculation`。

Later internal correction signal:
- https://aiartrecipe.com/archives/3132 では正しい `ejaculation` を試し、生成挙動が変化している。

Decision:
- location phrase observations: `PRACTICAL`
- misspelled-token non-effect conclusion: `REJECT_EXPERIMENT_INVALID`

This is a durable warning: **siteの「効かなかった」を採る前に spelling/canonical/alias/versionを検証する。**

### 4.17 Urination / source-target
Article: https://aiartrecipe.com/archives/1136

Observed:
- `peeing` は強いが、visible penisがあるとwrong sourceへ引っ張られる例。
- `peeing from pussy` 等の free relation phraseでsourceを固定しようとする。

Decision: `HIGH_VALUE_PRACTICAL_FAILURE`

Project lesson:
- fluid/material presence != source-target relation success。
- natural-language/free phraseは relation-support candidate、canonicalではない。

### 4.18 Cross-section / internal anatomy
Article: https://aiartrecipe.com/archives/3263

Observed:
- cross-section / internal / x-ray / cervix / uterus 等を比較。
- specific LoRAがweight 1では強すぎ、0.5–0.8等を記事で推奨。

Semantic error:
- `impregnation` を「着床」相当として説明する箇所があるが、implantationとimpregnationは同義ではない。

Decision:
- visual behavior: `PRACTICAL`
- Japanese semantic gloss: `REJECT_AS_CANONICAL_AUTHORITY`
- LoRA weight: `ADAPTER_SPECIFIC_ONLY`

---

## 5. Site-level error taxonomy

### E1 — spelling / token validity
Examples:
- `ejucalation / ejecalation`
- `beastiality`
- `collorbone`

Policy:
`failed token`をmodel ignoranceに分類する前に spelling/canonical/alias を検証する。

### E2 — semantic gloss error
Example:
- `impregnation` と implantation の混同。

Policy:
Japanese説明は検索候補には使えるが canonical meaning authorityにはしない。

### E3 — model-version leakage
Old WAI V12/unknown SeaArt snapshotの挙動をWAI v17へ移植する危険。

Policy:
exact version absent -> `HISTORICAL_OR_UNKNOWN / TEST_REQUIRED`。

### E4 — success screenshot without denominator
母数、seed、failed outputsが無い。

Policy:
E0/E1 practical hypothesisまで。success rateにしない。

### E5 — LoRA/control confound
AdapterやAnyTest等の成功をbase model abilityへ帰属する危険。

Policy:
`PROMPT_ONLY / ASSISTED_CONTROL / LORA_ASSISTED / POSTPROCESS_RESCUE`を分離。

### E6 — subjective ranking
「最強」「これでOK」等。

Policy:
model choice preferenceとしてのみ保存。事実化しない。

### E7 — Negative masking
`eyes`などで問題箇所を消す、broad anatomy suppressionでターゲットごと消す等。

Policy:
error suppressionとtarget successを別指標にする。

### E8 — free phrase mistaken for canonical
ordinary English phraseが効くこととDanbooru tag identityは別。

Policy:
`FREE_PHRASE_ALT_TRIGGER`として保存し、canonicalを変更しない。

---

## 6. Where the site is unusually valuable

### 6.1 Failure corpus
このサイトで最も価値が高いのは successful prompt list より failure descriptions。

Examples:
- urine source reversal
- enema wrong-site / IV-like rendering
- whip shape collapse
- wrong person count
- object insertion implement ambiguity
- natural-language side/ownership not always obeyed
- machine/tentacle prior causing unrelated scene structure

These map directly to current #44 failure taxonomy:
- `WRONG_BODY_SITE`
- `WRONG_ACTOR_TARGET`
- `WRONG_COUNT`
- `OBJECT_ONLY_RELATION_FAIL`
- `GEOMETRY_FAIL`
- `CONCEPT_PRIOR_LEAK`
- `VISIBILITY_UNCLEAR`

### 6.2 Japanese practical vocabulary
Japanese user intentと英語surface phraseの間を埋める候補が多い。

However:
- search/display candidateとして有用
- canonical Prompt outputへ直結させない
- UI-JA semantic authorityではない

### 6.3 Model transition snapshots
Old WAI, current Anima, Illustrious derivatives等を時系列で見られる。

Useful for:
- “昔効いた” ruleの発見
- version driftの疑い
- current exact-family image test候補

---

## 7. Cross-check against official model sources

### WAI v17
Official: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Exact author facts that override site generalization:
- Steps 15–30
- CFG 5–7
- Euler a
- >1024² original area guidance / example 1024×1344
- `general / sensitive / nsfw / explicit`
- avoid excessive quality/aesthetic tags and overly long Negative
- Hires can repair limbs

Thus:
- old WAI article settings are historical unless exact v17
- giant Prompt/Negative recipes are not author-default truth
- post-Hires anatomy success is separate from base Prompt success

### NoobAI XL 1.1 EPS
Official: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

Exact author facts:
- Danbooru + e621 native tag training context
- CFG 5–6, 25–30 steps, Euler a, ~1MP
- order: count -> character -> series -> artist -> special -> general -> other

Site phrases may be practical candidates but cannot override this exact caption/order evidence.

### Anima
Official: https://huggingface.co/circlestone-labs/Anima

Exact author facts:
- tags + natural language + hybrid
- Base/Aesthetic/Turbo differences
- tag dropout
- Gelbooru-form preference where applicable
- multi-character description guidance
- Turbo CFG 1 / 8–12 steps

Thus aiartrecipe's Anima relation examples are useful practical corroboration, but success rate and superiority claims remain practical only.

---

## 8. Knowledge decisions

### ADOPT
- Site as Japanese `PRACTICAL` knowledge lane.
- Failure observations as hypothesis / audit-red-flag evidence.
- free relation phrases as alternate-trigger/support A/B candidates.
- exact-old-version articles as historical model evidence.
- model-specific observed priors as TEST_REQUIRED candidates.

### HOLD / VERIFY FIRST
- all canonical/alias status
- all model-version-unspecified response claims
- all broad+specific “must add” advice
- all Negative hacks
- success-rate claims without denominator
- LoRA necessity claims
- “model X better than Y” rankings

### REJECT
- typo-based non-effect conclusions
- Japanese gloss as canonical authority
- assisted-control success as Prompt-only proof
- LoRA trigger bundle as intrinsic semantic support
- one-image Tagger recommendation as Special2788 evaluator truth
- site commercial/license claims without exact upstream license confirmation

---

## 9. Future use rule

When a Special audit or Stage10 case resembles an aiartrecipe article:

1. find exact article/date/model/version;
2. verify token spelling and project canonical identity;
3. extract the **failure mode**, not only the successful Prompt;
4. identify free phrase vs canonical/alias;
5. remove LoRA/control/postprocess confounds for Prompt-only baseline;
6. turn useful observation into one-question paired A/B;
7. run predetermined seeds under current exact project model;
8. only then promote from `PRACTICAL` toward local empirical guidance.

---

## 10. Final site verdict

`AIアートのレシピ` is **worth keeping as a high-value Japanese practical source**, especially for adult/niche generation failure cases and alternate prompt surfaces.

Its strongest value is **not “which prompt is correct” but “what went wrong in a real generation attempt, and what intervention appeared to change it.”**

It must always pass canonical/version/control/confound verification before becoming reusable project knowledge.
