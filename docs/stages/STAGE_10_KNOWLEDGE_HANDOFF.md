# Stage10 KNOWLEDGE Handoff

最終更新: 2026-09-08

## Status

Issue #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge` のStage10開始前外部調査を完了し、PROMPT班が参照できる整理済み知識セットとして固定する。

この文書は **Stage10実験用候補知識のhandoff** であり、production仕様・winner/scoring規則・全model共通Prompt grammarを決定するものではない。

## Evidence policy

証拠は次の順で扱う。

1. exact checkpoint / versionの公式作者情報
2. versionを特定できる資料・データ
3. controlledな実画像比較
4. community / practical evidence
5. 未検証仮説

不明点は推測で埋めず `UNKNOWN` / `HOLD` とする。

日本語資料は英語一次情報の代替ではなく **必須の独立レーン** とする。日本語実践資料は model / version / seed / 比較条件固定の有無を見て重み付けする。

## FACT / confirmed working knowledge

### Model family separation

- NoobAI XL 1.1 EPS と XL V-Pred 1.0 を混同しない。
- WAI Illustrious v17をIllustrious本体やNoobAIと同一grammar扱いしない。
- AnimaはBase / Aesthetic / Turboを分離する。
- model固有知識を全family共通truthへ昇格しない。

### Prompt structure / quality baseline

- NoobAI XL 1.1: native caption order `count → character → series → artist → special → general → other` を基準候補とする。camera tag最適配置は未固定。
- WAI v17: tag-first baseline。作者推奨qualityを最小構成で使い、quality/aesthetic tagやNegativeの過剰投入を避ける。
- Illustrious: booru tag中心。critical composition tagの競合を避ける。
- Anima: tag + short natural-language混在を候補として保持。長い自然文やbooru概念との矛盾は避ける。

Quality / Metaはfamily公式最小セットから始める。

- WAI v17: `masterpiece, best quality, amazing quality` を初期候補
- Illustrious: `masterpiece, best quality` を最小候補
- NoobAI 1.1: 公式prefixを基準。ただし成人Stress Testへ `safe` / negative `nsfw` を機械的に流用しない
- Anima: profile別。Aestheticではqualityなしbaselineも保持

`8k / ultra detailed / sharp focus / very aesthetic` 等を全family共通常設supportにしない。

### Support taxonomy

Stage10ではsupportを少なくとも次に分ける。

1. Meaning support — Special意味成立に必要
2. Geometry / Kinematic support — 身体を物理的に成立可能な向き・位置へ置く
3. Visibility support — 成否判定に必要なframing / angle / visibility
4. Resource parking / disambiguation support — 使わない手・腕・object等の行先を固定し混線を減らす
5. Aesthetic support — lighting / expression / background等。Stress Testでのみ必要に応じて追加
6. Redundant decoration — 成立にも観測にも不要

### Camera / pose / visibility

同roleを大量に積まず、原則として必要最小限を選ぶ。

- Frame: `upper body / cowboy shot / full body` 等から目的に応じて1系統
- Viewpoint: `from side / from behind / three-quarter` 等から1系統
- Orientation: `torso twisted / lean` 等、必要時のみ
- Visibility / Relation: 対象観測またはactor-target分離に必要な時だけ追加

`full body` は全Special共通tagではなくVisibility supportとして扱う。

### Multiple Special experiment design

まず単独成立と複合成立を分離する。

- `A_ONLY`
- `B_ONLY`
- `AB minimal`
- `BA`（順序差を見る場合）
- `AB + Frame`
- `AB + Frame + Viewpoint`
- `AB + targeted orientation / visibility / relation`

supportは一度に盛らず、1段ずつ追加して効果を追跡する。

Hard / rare Specialの失敗は少なくとも以下へ分離する。

1. exposure / recognition failure
2. single-concept failure
3. compositional / binding failure
4. visibility / crop / occlusion failure

## ADOPT candidates for Stage10 Prompt work

- Quality / Metaはfamily最小公式セットから開始する。
- Camera / pose supportはroleごとに原則1系統。
- Special意味supportとVisibility supportを混同しない。
- Geometry / Kinematic supportやresource parkingを、同義タグの大量追加より優先候補にする。
- 複数SpecialはA_ONLY/B_ONLYを先に確認し、AB失敗を「modelがtagを知らない」と即断しない。
- Stress TestではAesthetic supportを使用可能だが、Meaning / Visibility等と分離して記録する。
- Promptだけでprecise poseやactor-target分離が安定しない場合、support/weightを無限追加せずPrompt-only ceilingとして記録し、ControlNet/OpenPose/Forge Couple等は別assisted-control laneへ分離する。
- 実験分離モードとユーザー実戦Stress Testモードを分ける。

## HOLD — Stage10実画像A/Bで決着させる

### Anatomy-sensitive Negative

特殊解剖・意図的な多肢等と以下のNegativeの相互作用は、modern exact-familyの十分な公開controlled比較が不足している。

- `bad anatomy`
- `extra limbs`
- `extra arms`
- `malformed anatomy`

常設せず個別ON/OFFで比較し、

- intended Special retention
- unwanted error suppression

を別々に評価する。

### NoobAI XL 1.1 exact camera tuning

`full body / cowboy shot / from side` 等の使用自体ではなく、exact 1.1での最適配置・優先順は公式根拠不足。Stage10で実測する。

### canonical / Alias / Semantic response

辞書上の同一性・関連性とモデル反応の同一性は別。exact training pipelineでの正規化根拠不足のため、実Promptと画像を保存して比較する。

### Prompt density / Special count / support threshold

「長いPrompt」そのものではなく、次を記録して破綻点を実測する。

- tag数
- tokenizer token数
- Special数
- support block数
- relation sentence有無
- competing instruction数

### Additional HOLD

- `fully visible / clearly visible / unobstructed / in frame / body part focus` のfamily別定量効果
- rare/current post_countからtraining exposureを直接断定すること
- LoRA interferenceの再現可能な一般則（Stage10開始前Gateではなくfollow-up backlog）

## REJECT for pre-Stage10 defaults

- NoobAI / WAI / Illustrious / Animaへ同一Prompt grammarを公式扱いで流用する
- `8k / ultra detailed / sharp focus` 等を全familyへ「品質向上おまじない」として常設する
- camera / pose / supportを多く積めば複数Special成立率が単調に上がると仮定する
- `full body` を全Special共通の観測tagに固定する
- unusual anatomyへ `bad anatomy / extra limbs / extra arms` を機械的に常設する
- current Danbooru post_countだけからモデル学習済み確率を断定する
- communityの使用数閾値を固定productionルールへ昇格する

## Stage10 experiment candidates

優先して実画像でFACTへ昇格させる項目:

1. unusual anatomy × anatomy-negative ON/OFF
2. canonical / Alias / Semantic response差
3. NoobAI XL 1.1 exact camera / framing
4. broad + specific: `specific alone → + broad parent`
5. Aesthetic support: baseline vs aesthetic-added
6. Prompt density / competing instruction量
7. Special同時数 1 → 2 → 3… の破綻点
8. support escalation: minimal → Frame → Viewpoint → Geometry/Visibility
9. tag-only vs short relation sentence（family別）

## Required metadata for interpretation

各画像/結果について最低限、以下を追跡可能にする候補。

- model / exact checkpoint version
- positive Prompt実出力
- Negative Prompt実出力
- Seed
- resolution
- sampler / scheduler
- Steps
- CFG
- Special ID / canonical tag / layer
- comparison condition ID
- support blocks
- LoRA名 / weight（使用時）
- result判定とfailure class

## Japanese-source lane

Stage10でも日本語資料の実践検証を継続参照する。これまで主に次の種類を使用した。

- Illustrious: framing / angle / quality tagの同条件または実画像比較
- WAI / Illustrious: style / color / quality変化の比較
- NoobAI: artist tag / full-body等の実践比較
- Anima: natural language vs booru tag、composition、torso twist、複数人物・矛盾poseの実画像比較
- 複数LoRA: 同一Seed比較（follow-up backlog）

代表的な詳細source一覧とFACT/ADOPT/HOLDの根拠はIssue #4のRESULT commentsを参照:

- `5575548139` — Quality / Meta / camera / visibility / family別Stress構造
- `5575574404` — targeted support / anatomy-negative follow-up
- `5575634362` — Illustrious系Hard / rare Special・geometry support
- `5575856893` — latest-priority follow-up / Japanese-source lane reconfirmed
- `5575917518` — NoobAI exact camera / anatomy-negative補足
- `5575924699` — MEDIUM priorities → Stage10 experiment candidates
- `5575974230` — pre-Stage10 research cleanup / HOLD分離

## Production boundary

このhandoffから自動的に次を行わない。

- Stage9 Runtime Composerへの自動実装
- automatic Special deletion / generalization
- unvalidated support auto-insertion
- automatic weighting
- Prompt rewrite
- ambiguous alias silent resolve
- model-family behaviorのglobal truth化
- Stage10 winner/scoring logicのproduction固定

## KNOWLEDGE completion verdict

**Issue #4 pre-Stage10 research: COMPLETE.**

Stage10開始前に外部調査がblockerとなるHIGH/MEDIUM項目はなし。
残る不確定項目は明示的にHOLDとしてStage10実画像A/Bへ移管する。
PROMPT班は本書とIssue #4の証拠commentsを参照して正式handoffへ反映できる。
