# Stage10 PROMPT hard-target family matrix

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: PROMPT-side research/audit matrix. **Not production specification.**

## 1. Purpose

DanbooruTagTool の現行目的は、単なるタグ整形ではなく、Special を核に、難度の高い成人向け・ニッチ・複合シーンを高品質かつ低手直しで成立させること。

この文書は、hard-target を family 別に同一 grammar で処理しないための監査行列を定義する。

対象 family:
- WAI Illustrious v17
- Illustrious XL
- NoobAI XL 1.1
- Anima

本書では具体的な露骨な完成 Prompt を生成せず、render-critical 部分は以下の slot で表す。

- `[ACT]` — 狙う行為・特殊概念
- `[SITE]` — body-site / target site
- `[OBJECT]` — 器具・拘束具・付属肢・機械等
- `[ACTOR_A]` / `[ACTOR_B]` — 主体
- `[RELATION]` — 誰が誰に何をしているか
- `[POSE]` — pose / geometry
- `[VISIBILITY]` — target を観測可能にする構図
- `[QUALITY]` — family-appropriate quality/meta
- `[NEGATIVE]` — family-appropriate minimum negative

---

## 2. Evidence hierarchy

### OFFICIAL_FACT
モデル作者 / 公式 model card / 公式 docs。

### AUTHOR_GUIDE
作者または配布者の一次運用説明。

### COMMUNITY_JA / COMMUNITY_EN
実画像付き比較・固定 seed 比較等。FACT へ自動昇格しない。

### PROJECT_HYPOTHESIS
上記から PROMPT班が導いた Stage10 検証候補。

### HOLD / CONFLICT
一次根拠不足、family内差、実画像未確認。

---

## 3. WAI Illustrious v17

### 3.1 Confirmed author-side facts

`AUTHOR_GUIDE`
- 推奨 Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- 原寸は 1024x1024 より大きいサイズを推奨する作者説明あり
- positive の quality 例: `masterpiece, best quality, amazing quality`
- negative 例: `bad quality, worst quality, worst detail, sketch, censor`
- quality / aesthetic 関連語を入れすぎないこと
- overly long negative prompt は image quality を落とし blur を増やし得ると作者側が明示
- v17 では背景との色調整合や Hires.fix の limb correction 改善を作者側が説明

### 3.2 PROMPT interpretation for hard targets

`PROJECT_HYPOTHESIS`

WAI v17 では **tag-first + lean quality** を初期基準とする価値が高い。

推奨構造候補:

`[ACTOR/COUNT] -> [ACT] -> [SITE/OBJECT] -> [POSE] -> [VISIBILITY] -> minimum relation support -> [QUALITY]`

重要:
- quality/meta を hard-target の前面へ過積載しない
- long negative で target semantic まで薄めない
- 同 role の camera / visibility / pose support を複数積みすぎない
- hard-target が出ない時、まず quality 語を増やすのではなく、ACT/SITE/BINDING/OBJECT のどこが欠落したかを見る

### 3.3 WAI-specific failure suspicion

Stage10 で個別に監査する。

- `WAI_Q_OVERLOAD`: quality/aesthetic 過積載で target fidelity が低下
- `WAI_NEG_OVERLOAD`: negative 肥大化で blur / semantic suppression
- `WAI_SUPPORT_COLLISION`: frame/pose/visibility を盛りすぎて画面が競合
- `WAI_HIRES_MASKING`: Hires.fix 後だけ anatomy が改善し、base Prompt の成功と誤認

### 3.4 WAI Stage10 A/B priorities

1. lean quality vs expanded quality
2. minimum negative vs long negative
3. `[ACT]` only vs `[ACT]+one targeted support`
4. `[VISIBILITY]` 一要素追加時の target retention
5. base pass vs Hires.fix pass を別採点

---

## 4. Illustrious XL

### 4.1 Confirmed official direction

`OFFICIAL_FACT`
- Illustrious XL v1.1 は公式に v1.0 より natural-language focused な refined model と説明
- v2 系も high-res / natural language prompting を公式生成プラットフォームで前面に出している

### 4.2 PROMPT interpretation for hard targets

`PROJECT_HYPOTHESIS`

Illustrious は booru-tag centered heritage を維持しつつ、natural language support の余地を family 内で分けて見る。

最初から全て prose にしない。

初期比較候補:

A. `tag-centered`
- `[ACTOR/COUNT]`
- `[ACT]`
- `[SITE] / [OBJECT]`
- `[POSE]`
- `[VISIBILITY]`

B. `tag + one short relation sentence`
- 上記タグ構造を維持
- actor-target binding が崩れる時のみ `[RELATION]` を一文相当で補う

### 4.3 Illustrious-specific cautions

`PROJECT_HYPOTHESIS`
- same-role composition tag conflict を避ける
- natural language が効くことと、長文ほど強いことを同一視しない
- v1.0 / v1.1 / v2 / WAI derivative を一つの family behavior に潰さない
- hard-target で target が消えた場合、training familiarity と compositional failure を分離

### 4.4 Illustrious Stage10 priorities

1. tag-centered vs tag+short relation support
2. simple Special vs relational Special
3. one actor vs multi actor binding
4. body-site precision
5. composition support density

---

## 5. NoobAI XL 1.1

### 5.1 Official facts

`OFFICIAL_FACT`
公式 README にて:
- native tags caption
- Danbooru / e621 dataset
- caption order:
  `<count>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`
- CFG 5–6
- Steps 25–30
- Euler a
- 1024 前後の総面積を推奨
- quality prefix / negative の公式例あり

### 5.2 PROMPT interpretation for hard targets

NoobAI では現時点で **Special placement を特に壊さない**。

初期候補:

`[COUNT] -> [IDENTITY] -> [SPECIAL: ACT/SITE/OBJECT] -> [GENERAL SUPPORT: POSE/VISIBILITY] -> [OTHER/QUALITY]`

PROMPT監査では:
- `[ACT]` を general/support に埋没させない
- alias/broad tag へ置換した結果、native caption surface から遠ざかっていないか見る
- non-human / appendage 系で e621 混合の恩恵があるかは期待に留め、実画像で検証

### 5.3 NoobAI-specific failure suspicion

- `NOOB_SPECIAL_DISPLACED`: Special が general support の後ろに埋もれる
- `NOOB_ALIAS_MISMATCH`: canonical / alias の training response 差
- `NOOB_NEG_CONFLICT`: 公式 default negative を hard-target に機械適用し semantic collision
- `NOOB_NONHUMAN_PRIOR`: e621由来を期待しすぎ、実際の relation/binding が追いつかない

### 5.4 NoobAI Stage10 priorities

1. canonical vs alias response
2. Special placement
3. Special + minimum general support
4. e621-related non-human target familiarity
5. official default negative の target-specific interaction

---

## 6. Anima

### 6.1 Official facts

`OFFICIAL_FACT`
公式 model card:
- Danbooru-style tags / natural-language captions / combinations で学習
- tag order:
  `[quality/meta/year/safety] [count] [character] [series] [artist] [general tags]`
- section 内 tag order は arbitrary
- pure natural language は descriptive にし、少なくとも 2 sentences 程度を公式推奨
- tags + natural language を混在可能
- multiple characters ではキャラ名だけでなく basic appearance を書くことが特に重要
- random tag dropout 学習のため、関連 tag を全列挙する必要はない
- Aesthetic版では positive quality tag は必須でなく、score_* を強く使いすぎると slop 側へ押し得る旨を作者が説明
- weighting は機能するが典型的 SDXL より高い weight が必要な例を公式提示

### 6.2 PROMPT interpretation for hard targets

Anima では **relation / ownership / multi-actor** の扱いを他 family より独立検証する価値が高い。

候補構造:

A. `tag-only`
- family tag order に沿う
- `[ACT] / [SITE] / [OBJECT]` を concise に保持

B. `hybrid`
- tag core を保持
- `[RELATION]` を短い自然文で追加
- multi actor では actor appearance anchor を必要時のみ付与

### 6.3 Anima-specific failure suspicion

- `ANIMA_RELATION_UNDERDESCRIBED`: tag-only で actor-target relation が弱い
- `ANIMA_APPEARANCE_LEAK`: left/right 等の曖昧な actor 呼称で属性が混線
- `ANIMA_OVERDESCRIPTION`: descriptive prose を増やしすぎて target core が散る
- `ANIMA_SCORE_SLOP`: Aesthetic版で score tag を過積載
- `ANIMA_WEIGHT_OVERSHOOT`: SDXL感覚の weighting 微調整をそのまま流用して効かない / 強くしすぎる

### 6.4 Anima Stage10 priorities

1. tag-only vs hybrid relation support
2. actor appearance anchor 有無
3. one relation sentence vs longer descriptive prose
4. Aesthetic版 quality-free / lean quality / score-heavy
5. weighting on/off を target単位で独立比較

---

## 7. Cross-family matrix

| Audit axis | WAI v17 | Illustrious | NoobAI 1.1 | Anima |
|---|---|---|---|---|
| First prompt style | tag-first | tag-centered | native-tag-order | tag or hybrid |
| Special placement importance | High | High | Very high / explicit caption slot | general-tag system; relation support may be prose |
| Natural-language relation support | HOLD / targeted | Candidate | HOLD / targeted | Strong candidate |
| Quality tag density | Lean | family/version dependent | official prefix exists | Aesthetic can be quality-light |
| Long negative | Avoid | HOLD | official baseline exists; hard-target collision test required | family/profile dependent |
| Multi-actor support | binding test | binding test | binding test | appearance-anchor test high priority |
| Weighting | targeted only | targeted only | targeted only | works but family-specific magnitude |
| Non-human/appendage hypothesis | test | test | e621-related candidate | test |
| Hires.fix audit | separate pass | separate pass | separate pass | workflow-specific |

---

## 8. Hard-target slot architecture

PROMPT班では露骨な core を広い一枚 slot へ逃がさず、**監査可能な semantic slot** に分ける。

最低限:

- `[ACT]`
- `[SITE]`
- `[OBJECT]`
- `[ACTOR_A]`
- `[ACTOR_B]`
- `[RELATION]`
- `[POSE]`
- `[VISIBILITY]`

ただし user-facing の手動差し替えは増やさない。
この分割は内部監査・構造化のためであり、最終UIで user に8項目入力を要求する意味ではない。

原則:
- 内部では細かく分ける
- user には第一推奨を完成形として出す
- ambiguity のある部分だけ最小選択へ戻す

---

## 9. Family-specific A/B template

### 9.1 WAI

- A: `[CORE] + lean quality + minimum negative`
- B: A + one support only
- 別実験: lean quality vs expanded quality
- 別実験: minimum negative vs long negative

### 9.2 Illustrious

- A: tag-centered core
- B: A + one short relation support
- 別実験: composition support 1要素追加

### 9.3 NoobAI

- A: official caption order に沿う core
- B: Special placement のみ変える
- 別実験: canonical vs alias

### 9.4 Anima

- A: tag-only
- B: tag core + short `[RELATION]`
- 別実験: actor appearance anchor 有無
- 別実験: quality-light vs quality-heavy

---

## 10. Hard-target quality score decomposition

単一 winner に潰さない。

### Semantic axes
- `ACT_RETENTION`
- `SITE_ACCURACY`
- `ACTOR_TARGET_BINDING`
- `OBJECT_INTEGRITY`
- `RELATION_CORRECTNESS`

### Composition axes
- `POSE_GEOMETRY`
- `VISIBILITY`
- `OCCLUSION`
- `FRAME_READABILITY`

### Finish axes
- `ANATOMY_COHERENCE`
- `FACE_HAND_QUALITY`
- `STYLE_COHERENCE`
- `ARTIFACT_RATE`
- `OVERALL_FINISH`

### Operational axes
- `PROMPT_COMPLEXITY`
- `USER_REPAIR_BURDEN`
- `REPRODUCIBILITY`
- `PROMPT_ONLY_LIMIT`

---

## 11. Failure-to-intervention routing

### TARGET_MISSING
Do not immediately add quality tags.
Check:
1. family trigger familiarity
2. Special placement
3. canonical / alias surface
4. core conflict

### SITE_WRONG
Check:
1. `[SITE]` ambiguity
2. competing site tags
3. pose geometry
4. crop / visibility

### BINDING_LOST
Check:
1. actor count / identity
2. relation phrase
3. appearance anchor
4. multiple competing acts

### OBJECT_DEGRADES
Check:
1. object identity
2. object role
3. source / attachment relation
4. frame visibility

### GEOMETRY_BREAK
Do not keep adding semantic tags.
Check:
1. pose conflict
2. support density
3. assisted-control candidate

### HIGH_QUALITY_BUT_WRONG
Reject as target success.
Visual quality cannot compensate for semantic failure.

### CORRECT_BUT_LOW_QUALITY
Keep semantic success separately and optimize finish in a second lane.

---

## 12. What must not be generalized

- WAI v17 quality behavior -> all Illustrious
- Illustrious natural-language support -> NoobAI caption behavior
- NoobAI e621 familiarity -> guaranteed non-human relation success
- Anima natural-language strength -> long prose always better
- one model's weighting scale -> another model
- one negative profile -> every hard target
- one simple-tag evaluator threshold -> rare relational / composite target

---

## 13. Stage10 experiment order recommendation

After dictionary freeze / evaluator coverage handoff:

### Phase F1 — family baseline
Same abstract hard target across WAI / Illustrious / NoobAI / Anima with family-native grammar.
Do **not** force identical surface Prompt.
Compare intent-equivalent family-native Prompts.

### Phase F2 — binding
- single actor / simple relation
- multi actor
- body-site / ownership
- object relation

### Phase F3 — support
One support at a time:
- Frame
- Viewpoint
- Geometry
- Visibility
- Relation support

### Phase F4 — quality / negative
Only after semantic target is stable.

### Phase F5 — production stress
Multiple Special / multiple relation / difficult geometry / finish quality.

### Phase F6 — ceiling
Prompt-only vs assisted-control candidate boundary.

---

## 14. Acceptance rule

A family-specific Prompt rule may be promoted only when:

1. source/evidence lane is explicit
2. target class is explicit
3. family/version is explicit
4. fixed-seed A/B or equivalent controlled evidence exists
5. semantic score and image-quality score are both recorded
6. negative/support side effects are known
7. failure cases are retained, not hidden
8. result is not generalized outside tested family/class without evidence

---

## 15. Current provisional recommendation

### WAI v17
`LEAN_TAG_FIRST`
- lean quality
- short negative
- Special-centered
- one support at a time

### Illustrious
`TAG_CENTERED_WITH_TARGETED_RELATION_OPTION`
- booru-tag core
- relation prose only when binding requires it

### NoobAI 1.1
`NATIVE_CAPTION_ORDER_SPECIAL_FIRST`
- official special/general layering を尊重
- canonical/alias response difference を優先検証

### Anima
`HYBRID_CAPABLE_RELATION_AWARE`
- tags + natural language を正規候補として扱う
- multi-actor では appearance anchor を高優先検証
- Aesthetic は quality overloading を避ける

すべて `CANDIDATE`。Stage10画像根拠前に production FACT としない。

---

## 16. Boundary

- production `data/**` を変更しない
- #32 verdict を変更しない
- KNOWLEDGE #44 corpus を代行しない
- Stage10 production A/B を開始しない
- hard-target の具体的な露骨な完成 Prompt をこの文書へ固定しない
- userへの手作業を増やすための slot 分割ではない

この文書の目的は、**hard-targetを高品質に成立させるため、family差を保持したままStage10で何を比較すべきかを監査可能にすること**。
