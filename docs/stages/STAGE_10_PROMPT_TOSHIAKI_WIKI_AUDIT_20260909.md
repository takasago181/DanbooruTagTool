# Stage10 PROMPT Toshiaki diffusion Wiki audit

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: community-source audit / prompt-side research candidate. **Not production specification.**

## 1. Purpose

`https://wikiwiki.jp/sd_toshiaki/` のうち、動画を除く Prompt・モデル・生成設定・Forge Neo・拡張機能・Tagger 関連ページを、DanbooruTagTool の現在目的――**高品質で、生成難度が高く、ニッチ・複合的な成人向け画像を狙い通りに成立させること**――から監査する。

本Wikiは、日本語圏の実運用知識として非常に価値が高い。一方でWiki自身が「AI進化に編集が追いつかない」「間違い・旧情報があり得る」と注意しており、2022–2023年のA1111/SD1.5知識と、2026年のAnima / Forge Neo知識が同居する。

したがって本プロジェクトでは、Wiki全体を正本として採用せず、**更新日・対象モデル・UI/parser・一次情報一致を必須メタデータにする `COMMUNITY_JA_CANDIDATE_CORPUS`** として扱う。

---

## 2. Overall verdict

### ADOPT AS CANDIDATE CORPUS

強み:
- 日本語圏の実運用知識が非常に広い。
- Danbooruタグ、A1111構文、Dynamic Prompts、X/Y/Z plot、Forge Neo、Forge Couple、Illustrious、Anima、WD Taggerまで横断している。
- 成功例だけでなく、失敗・相性・古い手法への注意が多い。
- Anima / Forge Neo 関連は2026年更新が多く、現行環境との距離が近い。
- 「モデルごとに推奨Promptや設定が違う」「タグが存在してもモデルが学習しているとは限らない」といった、本プロジェクトのStage10思想と整合する実践知識が多い。

弱み:
- Wikiなのでauthoritative specificationではない。
- 同じページに `OFFICIAL_MATCH` と `COMMUNITY_HYPOTHESIS` が混在する。
- モデル本体の文法と、A1111/ForgeのPrompt parser構文が混在する。
- Illustriousページは更新日が新しくても、本文の大部分が旧v0.1前提と明記されるなど、**ページ更新日だけでは情報鮮度を判定できない**。
- Animaページに公式情報と衝突する具体的記述が少なくとも2件ある。
- 2022–2023年の長文Negative/weightテンプレ等をmodern familyへ流用すると逆効果になり得る。

総合:
> **AIArtRecipeより技術的に深く、Prompt engine / Forge operation / experimental designへの価値が高い。反面、version/parser scopingをせずに丸呑みすると危険。**

---

## 3. High-value findings

### 3.1 Danbooru canonical identity vs rendered Prompt surface

Page: `Danbooru語`

有用な整理:
- Danbooru上のcanonical tagは `_` で複合語をつなぐ。
- AI向けDanbooru-style Promptでは複合語をspaceで記述する運用が一般的。
- `()` を含むcanonicalはA1111系のweighting syntaxと衝突するためescapeが必要になる場合がある。

PROMPT decision:
- **canonical identity と rendered prompt surface を分離**する現在設計を補強する。
- `canonical=upper_body` を保持していても、target family/parserでは `upper body` としてrenderする、という層を独立させる価値がある。
- canonical文字列の保存と、model/parserへ渡す文字列を同一視しない。

Evidence label: `COMMUNITY_VALIDATED / UI_PARSER_SCOPED`

### 3.2 UI parser grammar is not model grammar

Page: `特殊なPrompt指定`

Wikiは以下をA1111/Forge系の特殊構文として整理する。
- weighting `()`
- prompt editing `[A:B:when]`
- alternating `[A|B]`
- `AND`
- `BREAK`
- escape rules

A1111公式でもprompt editing構文は確認できる。

PROMPT decision:
- **A1111 syntaxが動くこと ≠ model自体がその記法を学習していること**。
- Forge NeoでAnimaを使う場合も、parserがどの記法をどうconditioningへ変換するかを別監査する。
- Stage10 traceabilityには最低限:
  - source template
  - resolved/actual Prompt
  - parser/UI environment
  - model/checkpoint
  を残す。

`BREAK`のAnima挙動についてのWiki記述はenvironment/parser依存の可能性が高く、universal Anima factにはしない。

Evidence label: `OFFICIAL_MATCH` for A1111 editing syntax / `ENV_SPECIFIC_HOLD` for cross-architecture behavior

### 3.3 Dynamic Prompts is high-value for Stage10, but randomness must be controlled

Page: `Dynamic Prompts`

Wikiと公式 extension docsの方向が一致:
- wildcard
- `{A|B}` variation
- nested wildcards
- combinatorial generation
- X/Y Plotとの併用

PROMPT decision:
- Stage10 variation / prompt matrix生成に非常に有用。
- causal auditではrandom generationをそのまま使わず、combinatorial/deterministic条件にする。
- 必ずresolved actual PromptをPNG metadata/evidenceへ残す。
- `templateだけ保存して実際の展開Promptを失う` を禁止。

Evidence label: `OFFICIAL_MATCH / ADOPT_CANDIDATE`

### 3.4 X/Y/Z plot concept fits one-experiment-one-question

Page: `X/Y/Z plot`

Prompt S/R等で同seed・単一差分を比較する考え方は、現在のStage10 `one experiment = one question` と整合。

PROMPT decision:
- 実験思想は採用候補。
- 実際の実行基盤は#30 Forge Neo automationが上位になり得るので、古いA1111 UI scriptへの依存はしない。
- Wiki掲載の古いdefault Prompt/Negativeをそのままfixtureにしない。

Evidence label: `COMMUNITY_VALIDATED / OPERATIONALLY_SUPERSEDED_CANDIDATE`

### 3.5 Illustrious: “tag exists” is not “model knows it”

Page: `Illustrious-XL`

重要な実践知識:
- Danbooru上にタグが存在していても、学習画像が少ない・cutoff後・caption exposureが弱い場合、モデルが十分に反応するとは限らない。
- related/support tagsで弱い概念を補う運用がある。

PROMPT decision:
- Special2788監査の重要原則として有用。
- `canonical valid` と `model trigger effective` を別フィールド/別Stageで扱う。
- related tag supportは `AUTO_FACT` にせず `SUPPORT_CANDIDATE`。

Evidence label: `COMMUNITY_VALIDATED_CONCEPT / MODEL_RESPONSE_REQUIRES_AB`

### 3.6 Illustrious advice must be version-scoped

同ページは2026年更新でも、本文の多くがv0.1/初期派生ベースである旨を自ら記載。

さらに、Illustrious系一般向けの長めQuality/Negative運用は、WAI Illustrious v17作者ガイドの
「quality/aestheticを盛りすぎない」「overly long negativeはquality低下/blurを招き得る」
という説明と衝突する。

PROMPT decision:
- `ILLUSTRIOUS_BASE/V0.1` と `WAI_V17` を絶対に統合しない。
- Wiki上の「IllustriousではこのNegativeを維持」系助言をWAI v17へ継承しない。
- WAI v17はcreator guidanceを優先。

Evidence label: `VERSION_SCOPED`; WAIへの一般化は `CONTRADICTED_FOR_WAI_V17`

### 3.7 Anima page is mostly strong/current

Page: `Anima`

公式と一致する主要点:
- Danbooru-style tags + natural language + mixed prompting
- tag modeでspace-based surfaceを使う
- quality/meta/year/safety tags
- artist tagの`@`
- natural languageは短すぎない方がよい
- tags + NLを混在可能
- multiple charactersではcharacter名だけでなくappearance descriptionが重要
- Aesthetic profileではquality/score過積載に注意

PROMPT decision:
- Animaについては本Wikiを有力な `COMMUNITY_JA` 補助資料として使える。
- ただし公式と食い違う箇所は公式を優先する。

Evidence label: mostly `OFFICIAL_MATCH / COMMUNITY_EXPANSION`

### 3.8 Anima hard/relation prompting candidate knowledge

Wikiは、複雑な関係では:
- actorを曖昧な代名詞だけで呼ばない
- appearance/roleを明示する
- tag位置の小細工だけでなく、relationを自然文で明示する
といった実践知識を示す。

これはAnima公式の「multiple charactersでは基本外見を記述することが特に重要」と方向が一致する。

PROMPT decision:
- hard-targetでは
  1. tag-only baseline
  2. + one short relation sentence
  3. + appearance anchor when multiple actors
  の段階試験候補にする。
- proseを無制限に増やすルールにはしない。

Evidence label: `COMMUNITY_JA_CANDIDATE / STAGE10_AB_REQUIRED`

### 3.9 Forge Neo + Forge Couple is important assisted-control knowledge

Pages: `Forge neo`, extension guides

Forge Couple公式も:
- Forge Neo support
- Anima support
- region-specific conditioning
- checkpointがそもそもcompositionを理解できない場合は魔法の解決策ではない
と説明。

PROMPT decision:
- Prompt-only ceilingを認める現在方針を強化。
- repeated `BINDING_LOST / ATTRIBUTE_LEAKAGE / IDENTITY_MIXING` では、Promptを無限に長くするより Forge Couple / region control を `ASSISTED_CONTROL_CANDIDATE` にする。
- assisted control成功をPrompt-only成功として数えない。

Evidence label: `OFFICIAL_MATCH / ADOPT_CANDIDATE`

### 3.10 WD1.4 Tagger: useful tool, not semantic ground truth

Page: `WD1.4 Tagger`

WikiはTagger/Interrogatorの用途理解には有用だが、モデルランキング等には時点依存記述がある。

PROMPT decision:
- Taggerはcandidate evidence / evaluator補助。
- Special2788のrare/composite/relationについてhuman/semantic truthを代替しない。
- Wikiの「このtaggerが一番」評価はdate-scoped。

Evidence label: `TOOL_ORIENTATION / DATED_RANKING`

### 3.11 みんなの呪文広場 is valuable raw support corpus

Page: `みんなの呪文広場`

有用性:
- camera / pose / depth / wind / composition / motion / Dynamic Prompt候補など、日本語ユーザーの生の工夫が多い。

限界:
- model/version不明が多い。
- controlled comparisonではない。
- 成功例だけではcausal effect不明。

PROMPT decision:
- `COMMUNITY_JA_RAW_CANDIDATE` としてsupport候補発見に使う。
- production auto-supportへ直接昇格させない。

### 3.12 万能便利呪文 / old Tips are historical only

`万能便利呪文` は2022年、Tipsの一部は2023年前後のNAI/SD1.5/A1111時代の長文Negative・大量weight運用。

PROMPT decision:
- `HISTORICAL_ONLY`。
- WAI/Illustrious/NoobAI/Animaの現行Promptへ自動継承しない。
- 現代モデルで有効かは別途A/Bが必要。

---

## 4. Concrete corrections / contradictions found

### 4.1 Anima count-tag spacing

Wiki claim candidate:
- `1 boy, 2 girls` のように numeral と noun の間にspaceを置くべきで、`1boy/2girls`は悪いという説明。

Official Anima evidence:
- official tag-order grammar itself is `[1girl/1boy/1other etc]`。
- official full tag example uses `1girl`。

PROMPT verdict:
- **tag modeで「1 boy」が必須という主張は公式と衝突。**
- NL sentence内で `one boy / two girls` 等を使う話と、Danbooru-style count tagを混同しない。
- `CONTRADICTED_BY_OFFICIAL / MODE_CONFUSION`。

### 4.2 Anima/Qwen “1k token limit” rationale

Wiki claim candidate:
- small Qwen encoderに1k token程度の制限があるため、自然文を300 words以下程度に抑えるという説明。

Implementation/config evidence:
- Qwen3 text encoder自体のmax-position capabilityは1k固定ではない。
- Anima tooling/adapter側には別のtoken-length/padding/training configurationが存在する。

PROMPT verdict:
- **「1k token limitだから」という説明は技術的根拠として採用しない。**
- 「Promptを不必要に長文化しない」という実践注意は独立して妥当候補。
- exact production word/token limitはStage10 evidenceなしに固定しない。
- `RATIONALE_INCORRECT / PRACTICAL_CAUTION_MAY_HOLD`。

### 4.3 Illustrious long Negative vs WAI v17

Wiki-side generic Illustrious practice:
- 長めのquality/negative setを維持する運用がある。

WAI v17 author guidance:
- too many quality/aesthetic tags and overly long negative prompts can reduce image quality and make results blurrier.

PROMPT verdict:
- Generic Illustrious practiceをWAI v17へ適用禁止。
- `CONTRADICTED_FOR_WAI_V17`。

### 4.4 BREAK on Anima

Wiki-side observation:
- Forge Neo / AnimaでBREAKが期待どおり働かない、またはmodel textとして解釈される可能性への注意。

PROMPT verdict:
- useful warningだが、これはmodel training factではなくparser/environment behaviorの可能性が高い。
- Forge Neo version・parser pathを固定して確認。
- `ENV_SPECIFIC_HOLD`。

---

## 5. What should be learned into PROMPT knowledge

### High priority
- canonical tag identity vs rendered model surface
- UI parser grammar vs model grammar separation
- Dynamic Prompts resolved-prompt traceability
- deterministic/combinatorial variation for audits
- one-variable X/Y style comparison
- version-scoped model prompting
- Anima hybrid relation/appearance-anchor candidates
- Forge Couple as binding/control escalation option
- raw Japanese support-candidate vocabulary
- old knowledge quarantine by date/model

### Medium priority / A/B required
- related tags strengthening weak Illustrious concepts
- exact tag ordering effects within derived checkpoints
- Anima pronoun/role wording details
- exact Prompt density limits
- exact BREAK semantics outside standard SDXL parser paths

### Do not promote directly
- universal long-negative templates
- 2022/2023 “万能呪文”
- page-level claims without model version
- “tagger confidence = semantic truth”
- “Danbooru tag exists = model understands it”
- any family-wide rule inferred from a single derivative checkpoint

---

## 6. Source hierarchy for this corpus

1. model author / official model card
2. official extension/UI repository/docs
3. version-pinned implementation source
4. Toshiaki Wiki current model-specific page with direct evidence
5. Toshiaki Wiki community experimentation
6. raw prompt-sharing page
7. historical/general tips

If lower-ranked evidence conflicts with higher-ranked evidence, lower-ranked evidence is not averaged upward; it becomes `CONTRADICTION/HOLD`.

---

## 7. Product implications

This Wiki materially strengthens several current product directions:

- **model-family profile must exist**; one global Prompt grammar is inappropriate.
- canonical Special identity and rendered Prompt token surface should be separable.
- Prompt parser/environment should be part of Stage10 traceability.
- hard relation failures need a Prompt-only ceiling and assisted-control route.
- Japanese community prompt knowledge is valuable for support discovery, but support should be evidence-ranked.
- old long-template culture should not silently infect modern family profiles.

---

## 8. Boundary

- No production `data/**` changed.
- No #32 verdict changed.
- No KNOWLEDGE #44 corpus changed.
- No Stage10 production image A/B started.
- No model-family candidate was promoted to production FACT solely from this Wiki.
- Videos were excluded by user instruction.
