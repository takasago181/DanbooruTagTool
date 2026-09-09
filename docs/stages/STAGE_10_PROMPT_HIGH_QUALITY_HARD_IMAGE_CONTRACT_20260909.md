# Stage10 PROMPT high-quality hard-image contract

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT-side current-purpose contract candidate. **Not production specification.**

## 1. Purpose clarification

現在のDanbooruTagToolは、単なるタグ検索・翻訳・整形ツールではない。

PROMPT班では、現在目的を次として扱う。

> **日本語の制作意図から、Specialを核に必要な補助・構造を選び、対象model familyで「高品質かつ生成難度の高い成人向け・ニッチ・複合画像」を狙い通りに成立させやすい完成Promptへ変換し、ユーザーの手直しを可能な限り減らすローカル非LLM制作支援。**

ここでいう「hard」は内容の強度だけを指さない。少なくとも以下を含む。

- rare / niche concept
- multiple-Special simultaneous retention
- multi-actor / actor-target relation
- body-site / ownership / attribute binding
- unusual pose / geometry / visibility
- crop / occlusion / composition difficulty
- long-tail model recognition uncertainty
- multiple competing instructions
- quality / aesthetic / Negative / support interaction

したがって、easy/common tagが出ることだけを最終品質の代表にしない。

## 2. Core optimization target

最終Promptの目的関数は、単一の「canonical correctness」ではない。

優先するのは次の複合品質。

1. **Intent fidelity**
   - ユーザーが指定した意味・関係・強度・対象を保つ。
   - broad化、soft化、別概念化で成功率を見かけ上上げない。

2. **Target realization**
   - Special / relation / required body-site等が画像上に実際に成立する。
   - Prompt中にtokenが存在するだけではPASSにしない。

3. **Binding correctness**
   - actor/target、body-site、ownership、attribute、relationが正しい主体へ結びつく。
   - multiple actor / multiple Specialで混線・移動・役割反転しない。

4. **Visual quality**
   - anatomy/coherence、構図、視認性、detail、style consistency、不要artifact抑制を含め、完成画像として見栄えが成立する。
   - 「Specialだけ出たが画として壊れている」を高品質成功としない。

5. **Composition quality**
   - 画角・pose・orientation・visibilityがtargetの成立と観測に寄与する。
   - 同roleのsupport競合で画面を壊さない。

6. **Model-family fitness**
   - WAI / Illustrious / NoobAI / Anima等のfamily差を維持する。
   - 別familyの成功則を未検証で流用しない。

7. **Minimum-sufficient complexity**
   - 最短Promptを目標にしない。
   - 必要なsupportは使うが、成立に寄与しない語・競合要素・惰性quality語は減らす。
   - 目標は **minimum length** ではなく **minimum sufficient structure**。

8. **Low user effort**
   - userへSpecial探索、support再設計、Prompt再構築を戻しすぎない。
   - ambiguityがなければPROMPT側で第一推奨を組む。

9. **Reproducibility / traceability**
   - source intent、Special identity、support、resolved Prompt、Negative、model/settingsを追跡できる。

## 3. Two Prompt modes — stronger distinction

### 3.1 Experimental Isolation Prompt

目的:
- one experiment = one question
- 原因分離
- family/support/Negative等のA/B検証

特徴:
- 比較対象以外を固定
- aesthetic要素は観測に不要なら削る
- 高品質な最終作品Promptを目指すモードではない

重要:
**このPromptが簡素であることを、そのままproduction-quality Promptの設計原則へ昇格しない。**

### 3.2 Production-quality Hard-image Prompt / Stress Prompt

目的:
- ユーザーが実際に使う完成Promptへ近づける
- rare/niche/multiple/relation等の難しい構成を高品質に成立させる

許可される要素:
- family-appropriate quality/meta
- required Meaning support
- Geometry/Kinematic support
- Visibility support
- relation/binding support
- composition/camera
- aesthetic support
- target-safe Negative candidate
- 必要ならmodel-specific short natural-language relation support

ただし各要素は「入れたから正しい」ではなく、Stage10 evidenceで副作用を含め評価する。

## 4. High-quality image is not equal to quality-tag count

以下を禁止仮定とする。

- quality語を増やせば単調に画質が上がる
- `8k` 等を入れるほど上質になる
- Negativeを長くすれば破綻が減る
- supportを多く入れるほどSpecial成立率が上がる
- weightを強くすればtarget fidelityが上がる

Prompt auditではquality/metaを独立したsemantic/style/composition interventionとして扱う。

高品質判定は、少なくとも次を分離する。

- target fidelity
- anatomy/coherence
- composition/readability
- identity consistency
- visual cleanliness
- style/aesthetic quality
- artifact rate
- Special retention
- binding correctness

## 5. Hard-image failure classes

難しい画像では、単純な「出た/出ない」判定を禁止する。

最低限、以下を分ける。

- `TARGET_MISSING`
- `PARTIAL_TARGET`
- `MULTI_SPECIAL_DROP`
- `ACTOR_TARGET_SWAP`
- `BODY_SITE_BINDING_ERROR`
- `ATTRIBUTE_LEAKAGE`
- `IDENTITY_MIXING`
- `COUNT_FAILURE`
- `RELATION_FAILURE`
- `GEOMETRY_FAILURE`
- `VISIBILITY_FAILURE`
- `CROP_OCCLUSION_FAILURE`
- `COMPOSITION_CONFLICT`
- `NEGATIVE_COLLISION`
- `QUALITY_STYLE_DRIFT`
- `OVERPROMPTED_CONFLICT`
- `MODEL_TRIGGER_MISMATCH`
- `PROMPT_ONLY_LIMIT`
- `EVALUATOR_UNSUPPORTED`

これにより、rare Specialが失敗した時に「モデルがそのタグを知らない」と即断しない。

## 6. Prompt construction priority for difficult production cases

既存の組み方を再設計しない。現在の確定方向を、高品質目的に対して次の順で評価する。

1. Special Core / intended concept
2. actor/count/identity/relation required for ownership
3. Frame
4. Viewpoint
5. Orientation / Geometry
6. Visibility
7. targeted Relation / Binding support
8. family-appropriate Quality/Meta
9. target-safe Negative
10. Aesthetic support
11. optional variation / decoration

原則:
- 同role supportを無制限に積まない。
- 難しいからといって意味を弱めない。
- supportでtargetを覆い隠さない。
- aestheticを先に盛って成立問題を隠さない。
- 実戦Promptでは必要なsupportを削りすぎない。

## 7. Minimum-sufficient Prompt — revised meaning

従来の「Prompt肥大化を避ける」は維持するが、誤解を避ける。

### Wrong interpretation
- とにかくtag数を少なくする
- supportを削るほど良い
- background/lighting/expressionは不要
- test promptとproduction promptを同じ密度にする

### Current interpretation
**Targetを高品質に成立させるために必要な構造は入れ、効果のない・競合する・重複する要素だけを削る。**

したがって、Hard-image Promptではeasy imageよりsupport block数が増えてよい。
重要なのは量ではなく、各blockに役割と根拠があること。

## 8. Quality vs fidelity trade-off must be explicit

高品質化の操作がtarget fidelityを下げる場合、単純に「綺麗になったので勝ち」としない。

Stage10では少なくとも2軸で評価する。

- `TARGET_SCORE`: target intent / Special / binding / relation成立
- `IMAGE_QUALITY_SCORE`: anatomy / composition / aesthetic / artifact / coherence

理想は両方高いこと。

典型例:
- quality語追加で顔やstyleは改善したがtarget relationが弱くなった
- visibility supportでtargetは見えたが構図が不自然になった
- Negativeでartifactは減ったがtarget Specialも弱まった

この場合は単一winnerで情報を潰さない。

## 9. User-facing default should aim at best finished result

最終ツールでは、ユーザーが毎回「どのsupportを足すべきか」を判断する前提を弱める方向が現在目的に合う。

PROMPT側の将来候補:

- `Recommended` — 現在知識で最も高品質・成立率が高いと期待する完成Prompt
- `Faithful/Raw` — user explicit入力を最大限そのまま保持したtraceable版
- `Alternatives` — ambiguity / model variation / experimental variants

ただし、このUI/production動作の決定権はPROMPT班にはない。Stage10/future #42への提案候補とする。

## 10. Reprioritized Stage10 questions for the current goal

辞書freeze・KNOWLEDGE返却・Stage10 Gate後、PROMPT観点では次を高優先にする。

### Tier 1 — difficult target realization
1. multi-Special retention + binding
2. actor-target / body-site relation
3. visibility / geometry support side effects
4. CORE support auto-selectionの実生成効果
5. canonical/Alias/model-trigger response difference

### Tier 2 — finished-image quality
6. family-specific quality/meta minimum sufficient set
7. target-safe Negative profile
8. Prompt density: under-supported -> sufficient -> over-supported
9. aesthetic supportがtarget fidelityへ与える影響
10. model-specific block order / Special placement

### Tier 3 — user effort and ceiling
11. recommended default vs manual selection burden
12. replacement-slot burden
13. Prompt-only ceiling
14. assisted-control escalation boundary

## 11. Acceptance concept for a production-quality Prompt candidate

PROMPT側で将来 `PASS_HIGH_QUALITY_HARD_TARGET` と呼べる候補は、少なくとも以下を満たす必要がある。

- intentを弱めていない
- target Special/relationsが画像で成立する見込みがある
- multiple targetでbindingが明確
- 必要な箇所がframe内で観測可能
- same-role conflictを不用意に増やしていない
- model familyに適合
- quality/aesthetic supportがtargetを埋没させない
- Negativeがtarget semanticsと未検証衝突していない
- userが大幅なPrompt再構築をしなくてよい
- actual resolved Promptが追跡可能

Stage10実画像前は `CANDIDATE` であり、画像根拠なしにproduction-validと断定しない。

## 12. Anti-goals

この目的では以下を最適化しない。

- 2788件を全部同じPrompt grammarで処理すること
- Promptを最短にすること
- quality tag数を最大化すること
- userに大量選択肢を出すこと
- automatic evaluatorのcoverageを100%にすること
- easy/common tagの成功率だけを高く見せること
- Special canonical文字列そのものを守るために、画像上の意図成立を犠牲にすること
- Prompt-onlyに固執して無限supportを追加すること

## 13. Boundary

この文書はPROMPT班の目的・監査contract候補。

- production `data/**`を変更しない。
- Stage9 Composer仕様を上書きしない。
- #32 dictionary verdictを変更しない。
- KNOWLEDGE #44の調査を代行しない。
- Stage10本番A/Bを開始しない。
- model-specific未検証知識をFACT化しない。
- production UI/automation/scoringをPROMPT班だけで決定しない。

現在の役割は、**高品質で難度の高い成人向け画像を狙うという製品目的に対して、Prompt設計とStage10評価軸がズレないようにすること**。
