# Stage10 Prompt Audit Knowledge Reservoir

最終更新: 2026-09-09

## Status / purpose

この文書は、DanbooruTagTool の Stage10 以降で **Prompt生成結果を独立監査するための知識庫** である。

既存の `STAGE_10_KNOWLEDGE_HANDOFF.md` を置き換えない。既存handoffが主に「Promptをどう組むか」を扱うのに対し、本書は特に次を補う。

- Promptが正しく見えても画像上では失敗する典型パターン
- model family / text encoder / WebUI parser / extension による実行時差
- 複数主体・複数概念・relation・attribute binding の監査観点
- long-tail / rare concept を単純な成功率や post_count で誤判定しないための背景知識
- Prompt-only と regional / pose-control 等の assisted-control を混同しないための境界
- Negative Prompt、quality/meta、weight、chunking、template展開を「無害な補助」とみなさないための監査規則

本書は **候補知識 / 監査知識** であり、production Prompt grammar、winner/scoring規則、自動weight、自動support挿入を決定しない。

---

## 1. Evidence labels

監査では、知識の出所を以下で明示する。

| Label | 意味 | 扱い |
|---|---|---|
| `OFFICIAL_FACT` | exact model作者・公式repo/model card・実装source | 最優先。ただしversion一致を確認 |
| `AUTHOR_MIRROR` | 作者説明を転載したmirror/archive | 公式直URLが取得不能な場合の補助。mirrorであることを残す |
| `PROJECT_FACT` | DanbooruTagTool内の固定条件・controlled実測 | exact条件内では強い。family/globalへ一般化しない |
| `RESEARCH_BACKGROUND` | 査読/論文等の一般T2I知見 | failure taxonomyや監査設計に使用。exact anime checkpointの挙動証明にはしない |
| `COMMUNITY_JA` | 日本語圏の実画像比較・実運用 | 実践価値は高いが、再現条件とversionを確認。単独でFACT昇格しない |
| `COMMUNITY_OTHER` | その他community / issue / discussion | hypothesis生成・事故例の把握に使用 |
| `ADOPT_CANDIDATE` | 複数根拠からStage10試験に値する | controlled A/B後に昇格可 |
| `HOLD` | 根拠不足・source conflict・exact-family未検証 | 自動規則化禁止 |
| `CONFLICT` | 複数sourceが異なる運用を主張 | 片方を黙って採用せず、exact A/B対象にする |

### 監査上の原則

1. 公式の「推奨Prompt」は、そのmodel/versionにおける **baseline候補** であり、全用途に最適な固定正解ではない。
2. training caption順序は重要な根拠だが、「その順でPromptを書けば必ず最良」という証明ではない。
3. 日本語communityのcontrolled比較は、英語一次情報の代用品ではなく **独立した実践レーン** とする。
4. easy/common conceptで成立した規則を rare/composite/relational Special へそのまま一般化しない。
5. UNKNOWNを埋めるために post_count、Alias、implication、検索ヒット数を意味・生成能力の証明として代用しない。

---

## 2. Reproducibility contract — Prompt監査で必ず固定/保存するもの

Prompt監査は「表示された文字列」だけでは再現できない。最低限、以下を同一比較単位に保存する。

### 2.1 Model / inference

- model family
- exact checkpoint名
- checkpoint hash / file hash（取得可能な範囲）
- VAE
- text encoder / clip skip 等のfamily固有構成
- WebUI / runtime名とversion/commit
- sampler / scheduler
- Steps / CFG
- resolution
- Seed / RNG backend
- Hires.fix / img2img / refiner の有無と設定
- attention backend等、再現に影響し得るruntime差

### 2.2 Prompt execution trace

最低3層を区別する。

1. `SOURCE_TEMPLATE` — Dynamic Prompts / wildcard / macro等を含む入力元
2. `RESOLVED_PROMPT` — wildcard等を展開した実際のPositive/Negative
3. `EXECUTION_SYNTAX` — weight / BREAK / scheduling / region separator等、parserが解釈する構文

PNG infotextで resolved prompt が保存されても、templateが消える場合がある。逆にtemplate保存optionやextension不具合で metadata が期待どおり残らない例もあるため、監査artifactでは両方を別欄で保持する。[S06][S07]

### 2.3 Assisted controls

- LoRA名 / version / weight
- ControlNet / OpenPose 等のunit設定
- Forge Couple / Regional Prompting のmode
- region / mask / coordinates / weights
- Global Effect / Common Prompt
- separator
- extension version

これらを使った結果を `PROMPT_ONLY` 成功として数えない。

---

## 3. WebUI/parser layer — Prompt文字列とモデル入力は同義ではない

### 3.1 A1111 / SDXL系 attention syntax — `OFFICIAL_FACT`

AUTOMATIC1111 parserでは、典型的に次の構文が解釈される。[S05]

- `(text)` → attentionを約1.1倍
- `[text]` → attentionを約1/1.1倍
- `(text:1.5)` → 明示weight
- `BREAK` → parser上の特殊区切りとして扱われる

したがって、監査では **タグ集合が同じでもweight構文が違えば別Prompt** とみなす。

### 3.2 75-token/chunk系挙動 — SD/SDXL lane限定

A1111/CLIP系では長いPromptがchunk単位で処理され、`BREAK` がchunk境界へ影響する実装/運用がある。長Prompt比較では以下を記録する。

- tokenizer token数
- chunk数
- BREAK位置
- comma handling / chunk padding設定

ただしこれは **Anima等の非CLIP text encoderへ無条件移植しない**。

### 3.3 Anima × BREAK — `COMMUNITY_JA / HOLD-AS-GLOBAL`

AnimaはQwen系text encoderを使うため、A1111のSD/SDXL向けBREAKノウハウをそのまま使えないという日本語実践報告が複数ある。[S16][S17]

監査運用:

- Animaで `BREAK` を使ったPromptは、SDXLと同じ意味で処理されたと仮定しない。
- Anima Promptのgroupingは、短い自然文・明示subject/attribute記述・regional conditioningなど別方式として評価する。
- exact Forge Neo / ComfyUI実装での処理はversion依存なので、最終FACT化はcontrolled A/Bで行う。

---

## 4. Exact-family baseline knowledge

### 4.1 NoobAI XL 1.1 — `OFFICIAL_FACT`

公式model cardは以下を案内している。[S01]

- CFG 5–6
- Steps 25–30
- Euler a
- 約1024×1024面積
- 公式positive prefix: `masterpiece, best quality, newest, absurdres, highres, safe`
- caption schema: `count → character → series → artists → special tags → general tags → other tags`
- quality taxonomyは popularity/recency処理に基づく percentile区分

#### Audit implications

- 上記caption schemaはNoobAI 1.1に対する強いbaseline evidence。
- ただし `safe` や公式Negativeを **目的を問わず機械投入しない**。ratingや対象概念と因果的に競合する試験では、rating/Negative自体を変数として分離する。
- `8k`, `sharp focus`, `very aesthetic` 等を「NoobAI公式品質語」と誤認しない。
- READMEのtraining-date記述には v1.0への但し書きがあるため、v1.1 exact cutoffをそこから断定しない。

### 4.2 WAI Illustrious SDXL v17 — `AUTHOR_MIRROR`

取得可能な作者README mirrorでは以下が示される。[S02]

- Steps 15–30
- CFG 5–7
- Euler a
- 1024²より大きめのoriginal sizeを推奨
- positive例: `masterpiece, best quality, amazing quality`
- negative例: `bad quality, worst quality, worst detail, sketch, censor`
- quality/aesthetic関連tagを増やし過ぎたり、Negativeを長くし過ぎると quality低下/blurにつながる旨の警告

#### Audit implications

- quality boosterの数を増やすことを「無条件改善」とみなさない。
- WAIのPrompt auditでは、quality/meta増加に伴う **style drift / camera drift / subject fidelity変化** も確認する。
- NoobAI native caption orderをWAI公式grammarとして扱わない。

### 4.3 Illustrious XL official — `OFFICIAL_FACT`

公式model cardは、`close-up`, `upside-down`, `cowboy shot` 等のcritical composition tagの過剰併用がconflictを起こし得ると警告し、用途に応じて `upper body / cowboy shot / portrait / full body` 等を選ぶよう案内する。[S03]

推奨例:

- Euler a
- Steps 20–28
- CFG 5–7.5
- quality語: worst / bad / average / good / best / masterpiece

#### Audit implications

- composition supportは「多いほど強い」ではない。
- `full body + close-up + cowboy shot` のような同role競合は、Special failureと切り分ける。
- training/caption orderingが分かっても、Prompt順序効果は別A/Bで検証する。

### 4.4 Anima — `OFFICIAL_FACT`

公式model cardより。[S04]

- Danbooru-style tags、自然文、両者のmixで学習
- tagはlowercase、score tag以外はspaces推奨
- positive prefix例: `masterpiece, best quality, score_7, safe`
- tag order: quality/meta/year/safety → count → character → series → artist → general
- artist tagは `@` prefixが必要
- pure natural languageは少なくとも2文程度の具体記述を推奨
- tagsとnatural languageは混在可
- 複数characterでは名前だけでなく外見も記述することを作者が特に推奨
- Anima-Base / Aesthetic / Turboを分離
- Turbo: CFG 1 / 8–12 steps
- Aesthetic: quality tagsをcaptionから除いてfinetuneしており、positive quality tagなしbaselineが成立。score_*が過剰になる場合がある

#### Audit implications

- SDXLの「tagだけ・BREAK・低weight」慣習をそのまま適用しない。
- 複数人物では `character presence` と `attribute ownership` を別判定する。
- AestheticとBase/Turboでquality/metaの監査baselineを共通化しない。

---

## 5. Source conflict worth preserving — Anima count/tag surface

### Official
Anima公式はtag order例に `1girl/1boy/1other` を記載し、full exampleでも `1girl` を使用する。[S04]

### Japanese practical source
としあきdiffusion Wikiは、Qwen系encoderへの入力として `1 boy / 2 girls / 2 dogs` のように数字と名詞をspaceで分ける運用を推奨している。[S16]

### Decision

`CONFLICT / CONTROLLED_AB_REQUIRED`

- どちらかをglobal truthとして消さない。
- exact Anima version + same seed/settingsで `1girl` vs `1 girl` のような表記A/Bを組む価値がある。
- official tag identityとLLM text-encoderに対する自然言語tokenization上の実践最適化は、同じ論点ではない可能性がある。

---

## 6. Failure taxonomy — 「Promptに書いてある」だけではPASSにしない

T2I研究では、複数概念Promptで **subject neglect** と **attribute binding failure** が繰り返し報告されている。Attend-and-Exciteは、subject自体が消える catastrophic neglect と、色等が別subjectへ付くbinding failureを分離している。[S09]

T2I-CompBenchも compositional evaluation を、color/shape/texture binding、spatial relationship、non-spatial relationship、complex compositionへ分ける。[S10]

これらはmodern anime checkpoint固有の証明ではないが、DanbooruTagTool監査のfailure分類として有用な `RESEARCH_BACKGROUND` である。

### 必須failure class

1. `ENTITY_OMISSION`
   - 指定主体・object・主要概念の一つが画像から消える
2. `COUNT_FAILURE`
   - 人数/個数がずれる、重複する
3. `IDENTITY_MIXING`
   - 複数主体が混ざり、誰が誰か不明になる
4. `ATTRIBUTE_LEAKAGE`
   - 色、衣装、髪、装飾等が別主体へ移る
5. `ACTOR_TARGET_BINDING_FAILURE`
   - 行為主体/対象が逆転・不明瞭になる
6. `RELATION_FAILURE`
   - 各主体は存在するが相互関係が成立しない
7. `SPATIAL_FAILURE`
   - left/right, front/behind, above/below等が崩れる
8. `BODY_SITE_BINDING_FAILURE`
   - 対象となる身体部位や局所が別部位/別人物へ付く
9. `VISIBILITY_FAILURE`
   - 概念は成立している可能性があるがcrop/occlusion/frame外で判定不能
10. `SUPPORT_CONFLICT`
   - camera/pose/visibility support同士が競合して本体概念を壊す
11. `QUALITY_STYLE_DRIFT`
   - quality/aesthetic tag追加で、画質以外の構図・顔・色・styleが変わり比較を汚染する
12. `NEGATIVE_SUPPRESSION`
   - Negativeが意図概念の一部を抑制する
13. `LONG_TAIL_RECOGNITION_FAILURE`
   - rare concept自体をモデルが十分学習していない可能性
14. `ASSISTED_CONTROL_CONFOUND`
   - regional/pose control等で成功したのにPrompt-only成功として扱う

### 監査判定

1枚の画像に対して単一 `PASS/FAIL` だけを残さず、該当failure classを複数記録できるようにする。

---

## 7. Multiple-subject audit — 最低6問に分ける

複数主体Promptのhuman auditは、最低でも次を独立判定する。

1. **Presence** — 必要な全主体が存在するか
2. **Count** — 人数/個数が正しいか
3. **Identity** — 各主体を区別できるか
4. **Attribute ownership** — 特徴が正しい主体へ付いているか
5. **Relation** — actor-target / interactionが正しいか
6. **Visibility** — 判定に必要な箇所が見えているか

余裕があれば以下を追加する。

7. Spatial placement
8. Unwanted duplication
9. Cross-subject leakage
10. Base concept retention after adding the second Special

### なぜ必要か

「2人とも出た」だけでは、attribute leakageやrelation failureを見逃す。逆にrelationだけ失敗した画像を「タグ自体をモデルが知らない」と誤分類すると、不要なsupport追加やweight増加につながる。

### Japanese practical evidence

Animaの日本語実画像検証では、複数人物の髪/目/耳等の主要特徴は保たれても、装飾要素が別人物へ共有される例が報告され、`left character ... / right character ...` のような人物単位の自然文記述がタグ羅列より保持に有利だったというcontrolled practical resultがある。[S15]

これは `COMMUNITY_JA` であり、全Anima versionへFACT化しない。ただし attribute ownership auditを必須化する根拠として有用。

---

## 8. Relation / spatial audit — atomic questionを使う

複合Promptを「全体的に目的に近いか」だけで採点すると原因が分からない。

### 推奨atomic questions

- AとBは両方存在するか
- Aの属性XはAだけに付いているか
- Bの属性YはBだけに付いているか
- AはBに対して指定された位置関係か
- 指定interactionのactorはAか
- targetはBか
- relationを確認するのに必要な箇所がframe内か
- support追加でbase conceptを失っていないか

T2I-CompBench等がattribute binding / relation / complex compositionを分離するのと同じ理由で、DanbooruTagToolの監査も **概念単位のatomic subjudgment** を優先する。[S10]

---

## 9. Long-tail / rare concepts — post_countを生成確率へ直結させない

大規模multimodal model研究では、pretraining concept frequencyとdownstream performanceに強い関係があり、long-tail conceptで性能低下が観測されている。[S11]

ただしDanbooruTagToolでは、現在のDanbooru `post_count` は exact checkpointのtraining exposureそのものではない。

### Audit rule

- post_count = `STATISTICAL_CONTEXT`
- exact model training exposure = `UNKNOWN` unless version-pinned evidence exists
- rare Special failure時に、まず以下を分離する:
  1. concept recognition
  2. Prompt syntax mismatch
  3. composition/binding
  4. visibility
  5. competing support

### 禁止

- post_countが多い → modelは必ず知っている
- post_countが少ない → Promptが悪い
- 1 seed失敗 → concept未学習

いずれも断定しない。

---

## 10. Negative Prompt is a causal variable

Negative Promptは「画質だけを掃除する無害なfilter」とみなさない。

Classifier-Free Guidance系では、negative conditioningは生成方向そのものに関与する。general researchでもnegative promptingはsemantic alignmentを変化させ得る。[S12]

### Audit rule

- Special意味と意味的に近いNegativeは必ず記録する。
- anatomy-sensitive / count-sensitive / relation-sensitive Negativeは、関連するSpecial試験で常設しない。
- `Negative OFF → broad cleanup only → targeted negative` の段階A/Bを候補にする。
- Positive変更とNegative変更を同一A/Bで同時に行わない。

### HOLD

特定のanatomy-related Negativeがexact WAI/NoobAI/Animaで特定Specialを何%抑制するか、というfamily別定量則は未確定。既存handoffどおりStage10画像A/B対象。

---

## 11. Quality/meta tags — 見た目全体を動かす可能性を監査する

既存knowledge handoffに加え、日本語実践比較でもWAI系quality tagのON/OFFで顔、髪、衣装、画面への寄り方等が変わり、「ON=単純な高品質化」と言い切れない例が報告されている。[S18]

### Audit rule

quality/metaを変更したA/Bでは、Special成立率だけでなく以下を確認する。

- framing drift
- viewpoint drift
- subject identity drift
- palette/style drift
- detail増加によるocclusion
- anatomy error率

### Default

family公式最小セットから始める。大量の `8k / ultra detailed / sharp focus / very aesthetic` 等を共通常設しない。

---

## 12. Prompt density / ordering / attention — 「長さ」だけでは足りない

Prompt failureを総token数だけで説明しない。最低でも以下を記録する。

- tokenizer token数
- concept数
- Special数
- support block数
- same-role composition tag数
- weighted phrase数
- relation sentence数
- Negative token数
- chunk数（CLIP系）
- regional conditioningの有無

### Experiment ladder

`core only → +required meaning support → +visibility → +relation → +aesthetic`

各段階で1種類ずつ追加し、破綻点を特定する。

### Avoid

ABが失敗した時に、一度にcamera / visibility / weighting / broad parent / Negativeを全部変えること。原因追跡不能になる。

---

## 13. Forge Couple / Regional conditioning — separate assisted-control lane

Forge Couple公式READMEは、異なるconditioningを画像内regionへ割り当て、feature/color mixingを減らす目的を明示している。またcheckpoint自体がcompositionを理解していない場合はextensionでも直せないと注意している。[S08]

### Audit metadata

Forge Couple利用時は最低限保存:

- exact extension version/commit
- mode: Basic / Advanced / Mask / Tile
- region coordinates / masks / weights
- direction
- Global Effect
- Common Prompt
- separator
- compatibility setting
- subject replacement等

### Critical confound

Forge Couple READMEは Dynamic Prompts等がseparator/Common Promptを事前処理し、壊す可能性も警告している。[S08]

したがって:

- `PROMPT_ONLY`
- `PROMPT_PLUS_REGIONAL`
- `PROMPT_PLUS_POSE_CONTROL`

を同一スコアへ混ぜない。

---

## 14. Dynamic Prompts / wildcard audit

Dynamic Promptsの利用時、PNGに保存されるのがresolved promptだけで、元templateを後から再構成できないケースがある。[S06]

### Required

- template text
- resolved final positive
- resolved final negative
- wildcard source/version/hash（可能なら）
- random seed / combinatorial selection setting

### Why

同一「Promptテンプレート」であっても、wildcard展開結果が違えばSpecial supportやcameraが変わる。監査対象は template nameではなく **実際に生成へ渡されたresolved prompt**。

---

## 15. Prompt-only ceiling

次の条件が揃ったら、無限にtag/weightを足すのではなく `PROMPT_ONLY_CEILING` 候補として記録する。

- target concept単体は複数seedで成立する
- 複合時のみbinding/relationが崩れる
- minimal visibility supportでも観測可能
- supportを増やすほど別failureが増える
- relation sentence / order変更でも安定しない

その後、Forge Couple / ControlNet / OpenPose等を **別lane** で試す。

assisted-controlで成功したことは重要な実用知識だが、Prompt composer自体の能力と混同しない。

---

## 16. Human audit rubric candidate

各A/B比較について、総合winnerより先に以下を0/1/2またはPASS/UNCLEAR/FAILで記録する候補。

| Axis | Question |
|---|---|
| Target presence | 目的概念/主体が存在するか |
| Identity | canonicalが意図するvisual identityを保つか |
| Binding | 属性・部位・actor/targetが正しく結び付くか |
| Relation | 指定関係が成立しているか |
| Count | 人/物/概念数が正しいか |
| Visibility | 判定に必要な箇所が見えるか |
| Base retention | 追加Special/supportによって元概念を失っていないか |
| Unwanted leakage | 他主体/他部位へ属性が漏れていないか |
| Composition conflict | camera/pose supportが自己矛盾していないか |
| Style confound | quality/aesthetic差が意味判定を汚染していないか |

### Winner rule candidate

- semantic axesで明確な優位がある → A/B winner候補
- semantic成功は同等、見栄えだけ違う → `TIE_SEMANTIC` + aesthetic note
- visibility不足 → `UNCLEAR_VISIBILITY`
- identity/bindingの質問自体を評価器が扱えない → `REVIEW_SEMANTIC`
- metadata不足 → `INVALID_METADATA`

自動評価器のconfidenceが高くても、人間が見るべきsemantic questionと一致していなければ自動winnerにしない。

---

## 17. Audit matrix for future Stage10 expansion

最小代表ケースだけでなく、監査知識を育てるため以下の軸を段階的に持つ。

### A. Single concept

- common canonical
- rare canonical
- Alias vs canonical
- broad vs specific

### B. Composition

- same concept + frame ON/OFF
- viewpoint ON/OFF
- same-role composition conflict
- crop/occlusion stress

### C. Multiple concepts

- A_ONLY / B_ONLY / AB
- AB order reversal
- AB + minimal visibility
- AB + relation sentence

### D. Multiple subjects

- two identities
- attribute ownership
- asymmetric roles
- spatial relation
- object ownership

### E. Execution layer

- unweighted vs weighted
- SDXL BREAK/no BREAK where applicable
- short vs longer prompt density
- template vs resolved prompt verification

### F. Assisted controls

- Prompt-only baseline
- Forge Couple
- pose control

各実験は `one experiment = one question` を維持する。

---

## 18. Known traps / REJECT as audit shortcuts

- `画像が綺麗` → Specialが正しく成立した、と判定する
- `全主体が出た` → bindingも正しい、と判定する
- `タグがPrompt内にある` → modelがそのtagを理解した、と判定する
- `post_countが高い` → exact checkpointのtraining exposureが十分、と断定する
- `quality tagsを追加` → 比較条件を改善しただけなのでconfoundではない、と扱う
- `Negativeはcleanupだけ` と扱う
- `BREAK` / weight構文をmodel familyを跨いで同じ意味だと仮定する
- Regional Prompting成功をPrompt-only成功へ加算する
- Dynamic Prompt templateだけ保存してresolved promptを捨てる
- 1 seedの成功/失敗でルール化する
- easy WD14-classifiable conceptのthresholdをrare/relational Specialへ一般化する

---

## 19. New research decisions from this reservoir

### ADOPT_CANDIDATE

1. 監査failure taxonomyへ `ENTITY_OMISSION / ATTRIBUTE_LEAKAGE / ACTOR_TARGET_BINDING / RELATION / VISIBILITY / SUPPORT_CONFLICT` を明示追加する。
2. 複数人物監査ではPresenceとBindingを別採点する。
3. exact Prompt traceabilityを `template / resolved / execution syntax` の3層へ分ける。
4. Prompt-only / regional / pose-controlを別laneにする。
5. Negativeとquality/metaをcausal variableとして扱う。
6. rare conceptではpost_countを補助統計に限定し、recognition failureとcomposition failureを分離する。
7. AnimaではSDXL由来parserノウハウを自動継承しない。

### HOLD / controlled A/B needed

1. Anima `1girl` vs `1 girl` 等count表記の実効差
2. Anima exact versionでのBREAK処理差
3. Anima/SDXL各familyにおけるweight最適値
4. exact-family別 long Prompt破綻点
5. anatomy-sensitive Negativeのspecific concept retentionへの定量影響
6. broad+specific併用のfamily別効果
7. quality/meta追加によるSpecial成功率とstyle driftのtradeoff
8. Forge Coupleで改善するfailure classとPrompt-only ceilingの境界

---

## 20. Source inventory

### Primary / official / author

- **[S01] NoobAI XL 1.1 official model card** — Laxhar Lab, Hugging Face  
  https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

- **[S02] WAI Illustrious SDXL v17 author-text mirror** — LyliaEngine Hugging Face mirror; source credits WAI0731/Civitai  
  https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

- **[S03] Illustrious XL official early release model card** — OnomaAIResearch  
  https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0

- **[S04] Anima official model card** — circlestone-labs  
  https://huggingface.co/circlestone-labs/Anima

- **[S05] AUTOMATIC1111 prompt parser implementation**  
  https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/modules/prompt_parser.py  
  Related feature documentation: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features

- **[S06] Dynamic Prompts discussion — resolved prompt vs template metadata**  
  https://github.com/adieyal/sd-dynamic-prompts/discussions/149

- **[S07] Dynamic Prompts metadata issue examples**  
  https://github.com/adieyal/sd-dynamic-prompts/issues/703

- **[S08] SD Forge Attention Couple official repository / README** — Haoming02  
  https://github.com/Haoming02/sd-forge-couple

### Research background

- **[S09] Attend-and-Excite: Attention-Based Semantic Guidance for Text-to-Image Diffusion Models** — Chefer et al., SIGGRAPH 2023  
  https://arxiv.org/abs/2301.13826

- **[S10] T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-image Generation** — Huang et al., 2023  
  https://arxiv.org/abs/2307.06350

- **[S11] No “Zero-Shot” Without Exponential Data: Pretraining Concept Frequency Determines Multimodal Model Performance** — Udandarao et al., 2024  
  https://arxiv.org/abs/2404.04125

- **[S12] Stay on topic with Classifier-Free Guidance** — CFG/negative-prompting background; use as mechanism/background, not exact checkpoint rule  
  https://arxiv.org/abs/2306.17806

### Japanese practical lane

- **[S15] Anima複数character自然言語検証** — HKMC_AILab, 2026-06  
  https://note.com/hkmclab/n/n7611426be16a

- **[S16] Anima — としあきdiffusion Wiki** — tag表記、自然言語、複数主体、BREAK等のcommunity practical guidance  
  https://wikiwiki.jp/sd_toshiaki/Anima

- **[S17] 特殊なPrompt指定 — としあきdiffusion Wiki** — A1111/Forge向け構文のmodel/runtime依存注意  
  https://wikiwiki.jp/sd_toshiaki/%E7%89%B9%E6%AE%8A%E3%81%AAPrompt%E6%8C%87%E5%AE%9A

- **[S18] Draw Things 日本語ガイド — model/quality tag比較** — 2026-09  
  https://note.com/drawthingsguide/n/n49f84ee6804f

- **[S19] WAI系version固定Prompt/Seed比較例** — Novapen  
  https://note.com/novapen_create/n/nf4a63d6e94e6

- **[S20] Camera orientation実画像比較例** — iPentec  
  https://www.ipentec.com/document/ai-image/image-generation-prompt-model-orientation-prompt

### Project-local upstream evidence

本書は以下を前提として補強する。

- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
- Issue #4 RESULT comments: `5575548139`, `5575574404`, `5575634362`, `5575856893`, `5575917518`, `5575924699`, `5575974230`
- `docs/stages/STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md`
- Issue #5 PROMPT checkpoints
- Issue #37 representativeness review

---

## Final boundary

この知識庫から直接、次をproductionへ昇格しない。

- global Prompt grammar
- global Prompt order
- automatic weight
- automatic Negative expansion
- automatic quality booster expansion
- rare tagの自動削除/一般化
- Alias/Semanticのsilent replacement
- regional/pose-controlの自動有効化
- auto-winner threshold

監査で有用な知識は **失敗原因を正しく分類し、次のcontrolled A/Bを選ぶために使う**。production rule化は、exact family / exact runtime / traceable Prompt /複数seedでのStage10 evidenceを経たものに限る。