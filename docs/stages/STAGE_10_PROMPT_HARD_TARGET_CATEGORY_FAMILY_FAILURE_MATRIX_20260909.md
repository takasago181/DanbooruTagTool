# Stage10 PROMPT hard-target category × family × failure matrix

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: research/audit candidate. **Not production specification.**

## 1. Purpose

現在の製品目的は、単なるNSFW化やタグ整形ではなく、**高品質で、生成難度が高く、ニッチ・複合的な成人向け画像を狙い通り成立させること**。

本書では hard-target を具体的な露骨Promptとして保存せず、内部監査用の構造として扱う。

- `[ACT]` 行為コア
- `[SITE]` 対象部位
- `[OBJECT]` 器具・機械・付属肢
- `[ACTOR_A] / [ACTOR_B]` 主体
- `[RELATION]` 誰が誰に何をするか
- `[POSE]` 体勢・幾何
- `[VISIBILITY]` 観測に必要な画角/露出
- `[FINISH]` quality / lighting / aesthetic

ユーザーにこれらを全部入力させる設計ではない。内部で分解し、最終的にはPROMPT側が第一推奨を完成させる。

---

## 2. Evidence anchors

### WAI Illustrious v17
Author/model-card guidance:
- quality/aesthetic tagを足し過ぎない
- overly long negative promptは画質低下・blurry化を起こし得る
- Steps 15–30 / CFG 5–7 / Euler a
- 1024²超の初期解像度、Hires.fix設定例あり

Source:
- https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

### NoobAI XL 1.1
Official README:
- native tag caption
- caption order:
  `<people>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`
- Special tagsがGeneral tagsより前

Source:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

### Illustrious XL
Official v1.1 page:
- official platform advertises natural-language prompting
- v1.1以降をv1.0と同じ「booru tag only」前提で固定しない

Source:
- https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1

### Anima
Official model card:
- Danbooru-style tags + natural-language captions + mixed prompting
- pure natural languageは十分にdescriptiveにすることを推奨
- multiple charactersでは、名前だけでなく基本外見も書くことが重要
- random tag dropout学習

Source:
- https://huggingface.co/circlestone-labs/Anima

### Community evidence
Community evidence is `COMMUNITY`, not universal fact.
- Anima multiple-character users report both good NL separation and attribute bleed / breakage under added complexity.
- SDXL/Illustrious users frequently report attribute mixing and need for regional/inpaint workflows for difficult multiple-character scenes.

Representative:
- https://www.reddit.com/r/StableDiffusion/comments/1r336og/multiple_characters_using_anima_2b/
- https://www.reddit.com/r/StableDiffusion/comments/1tepgn4/sharing_my_experience_with_anima_comfyui_great/
- https://www.reddit.com/r/StableDiffusion/comments/1rg7cpj/how_to_make_multiple_character_on_same_image_but/

---

## 3. Common failure classes

- `ACT_MISSING`: [ACT]が画像上で成立しない
- `SITE_WRONG`: [SITE]が別部位へdrift
- `BINDING_LOST`: [ACTOR_A]/[ACTOR_B]/[RELATION]が混線
- `OBJECT_DEGRADES`: [OBJECT]が背景物・不明物体化
- `VISIBILITY_LOST`: 成立していても観測不能
- `GEOMETRY_BREAK`: pose/contact/拘束点/接続方向が破綻
- `ATTRIBUTE_LEAKAGE`: 属性や役割が別actorへ移る
- `COUNT_FAILURE`: 人数/本数/対象数が崩れる
- `OVERPROMPTED_CONFLICT`: support/quality/negativeを積み過ぎてcoreが弱まる
- `MODEL_TRIGGER_MISMATCH`: canonical/tag surfaceとmodel responseが噛み合わない
- `PROMPT_ONLY_LIMIT`: Prompt追加で改善せず、assisted control候補

---

# 4. Category × family matrix

## 4.A Anal / body-site-specific lane

### WAI v17
**Starting strategy:** `LEAN_TAG_FIRST`

Priority:
1. `[ACT]`
2. `[SITE]`
3. minimum `[POSE]`
4. minimum `[VISIBILITY]`
5. minimal quality/negative

High-risk failures:
- `SITE_WRONG`
- `VISIBILITY_LOST`
- `OVERPROMPTED_CONFLICT`

Why:
- WAI作者がquality/aesthetic/negative過積載を明示的に警告しているため、site-specificなcoreをquality語で埋めない。

Stage10 questions:
- [ACT] only vs [ACT]+[SITE]
- minimum visibility supportの有無
- short negative vs long generic negative

### NoobAI 1.1
**Starting strategy:** `SPECIAL_FIRST_NATIVE_CAPTION`

Priority:
1. count/actor
2. `[ACT]` as special
3. `[SITE]` / necessary general support
4. optional `[VISIBILITY]`

High-risk failures:
- `MODEL_TRIGGER_MISMATCH`
- `SITE_WRONG`
- `OVERPROMPTED_CONFLICT`

Why:
- official caption grammar explicitly separates special tags before general tags.

Stage10 questions:
- special canonical surface vs alternate/alias surface
- special-first vs reordered placement
- site supportをgeneral側へ足したときのrealization gain

### Illustrious
**Starting strategy:** `TAG_CENTERED_WITH_TARGETED_RELATION_OPTION`

High-risk failures:
- `SITE_WRONG`
- `GEOMETRY_BREAK`
- `MODEL_TRIGGER_MISMATCH`

Notes:
- v1.0系とv1.1+を同一grammarとみなさない。
- natural-language supportは版ごとに別評価。

Stage10 questions:
- tag-centered baseline
- targeted short relation sentenceの追加効果
- derivative WAIとの差

### Anima
**Starting strategy:** `HYBRID_SITE_RELATION_AWARE`

Priority:
1. actor/count
2. `[ACT]` / `[SITE]` tags
3. ambiguity時のみshort relation sentence
4. relevant appearance anchor if multi-actor

High-risk failures:
- `BINDING_LOST`
- `ATTRIBUTE_LEAKAGE`
- `OVERPROMPTED_CONFLICT`

Why:
- official card supports tags + natural language mix and explicitly warns that multiple characters need descriptive anchors.

Stage10 questions:
- tag-only vs tag + one short relation sentence
- appearance anchorの有無
- descriptive supportを増やし過ぎた時のcore dilution

---

## 4.B BDSM / bondage / restraint lane

### Shared semantic decomposition
`[THEME]`と`[PHYSICAL_RESTRAINT]`を分ける。

- broad theme: BDSM / bondage / immobilization
- physical: restraint point / method / object
- relational: dominance/submission等
- pose: suspension / seated / standing / restrained geometry

### WAI v17
Starting rule:
- broad themeだけでなく、必要なphysical restraintを少数明示
- quality/negativeは短く維持

High-risk:
- `OBJECT_DEGRADES`
- `GEOMETRY_BREAK`
- `OVERPROMPTED_CONFLICT`

Audit focus:
- 1 restraint point → 2 points の段階化
- full-body visibilityを足したことでcore actが弱まらないか

### NoobAI 1.1
Starting rule:
- restraint act/typeをspecial側
- object/body-state supportをgeneral側

High-risk:
- `OBJECT_DEGRADES`
- `MODEL_TRIGGER_MISMATCH`
- `BINDING_LOST`

Audit focus:
- broad theme only vs specific restraint special
- special position/order
- multiple restraint special同時保持

### Illustrious
Starting rule:
- tag-centered physical description
- relationが必要な場合のみshort support candidate

High-risk:
- `GEOMETRY_BREAK`
- `BINDING_LOST`
- `VISIBILITY_LOST`

Audit focus:
- restraint evidenceとact evidenceを同じframeに残せるか
- natural-language relation supportの版差

### Anima
Starting rule:
- physical restraintsはtags
- dominance/role/actor relationはshort NL candidate
- multi-actorではappearance anchor

High-risk:
- `ATTRIBUTE_LEAKAGE`
- `BINDING_LOST`
- `COUNT_FAILURE`

Audit focus:
- physical tag only vs physical tag + one relation sentence
- left/right等の位置ラベル vs appearance anchor

---

## 4.C Machine / mechanical-device lane

### Shared semantic decomposition
- `[OBJECT]` machine identity
- `[ACTIVE_PART]`
- `[SITE]`
- `[POSE]`
- `[CONTACT_RELATION]`
- `[VISIBILITY]`

### WAI v17
Starting rule:
- machine object + target relationを少数tagで固定
- aesthetic decorationを後回し

High-risk:
- `OBJECT_DEGRADES`
- `GEOMETRY_BREAK`
- `VISIBILITY_LOST`

Escalation trigger:
- machine bodyとcontact pointを同時に見せられない状態がseed acrossで継続

### NoobAI 1.1
Starting rule:
- device/action subtypeがspecialに存在するならspecial-first
- general supportでdevice parts / poseを補う

High-risk:
- `OBJECT_DEGRADES`
- `MODEL_TRIGGER_MISMATCH`
- `GEOMETRY_BREAK`

Audit focus:
- specific machine special vs broad machine concept
- special + general decompositionの有効性

### Illustrious
Starting rule:
- object/tag baseline
- contact relation only targeted NL candidate

High-risk:
- `OBJECT_DEGRADES`
- `BINDING_LOST`
- `GEOMETRY_BREAK`

### Anima
Starting rule:
- object tags + concise relation sentence candidate
- machine/userの位置関係を自然文で補えるか検証

High-risk:
- `BINDING_LOST`
- `ATTRIBUTE_LEAKAGE` equivalent for object ownership
- `OVERPROMPTED_CONFLICT`

Escalation trigger:
- complex machine geometryを文章で増補しても接続が改善せず、別要素が混線

---

## 4.D Tentacle / non-human appendage lane

### Shared semantic decomposition
- appendage identity
- count/distribution
- function split
- target site
- source identity
- pose/visibility

### WAI v17
Starting rule:
- broad appendage + 1 functionから開始
- multiple functionsを最初から詰め込まない

High-risk:
- `COUNT_FAILURE`
- `OBJECT_DEGRADES`
- `OVERPROMPTED_CONFLICT`

### NoobAI 1.1
Starting rule:
- e621/Danbooru native-caption exposureを背景に、specific special surfaceを優先検証

Important:
- e621 exposureから「必ず強い」とは断定しない。
- `EXPECTATION / STAGE10_REQUIRED`。

High-risk:
- `MODEL_TRIGGER_MISMATCH`
- `COUNT_FAILURE`
- `SITE_WRONG`

Stage10:
- broad appendage vs specific special
- one function vs two functions
- canonical vs alias/alternate surface

### Illustrious
Starting rule:
- tag-first baseline
- count/functionが崩れたらprompt-only ceilingを早めに疑う

High-risk:
- `COUNT_FAILURE`
- `BINDING_LOST`
- `GEOMETRY_BREAK`

### Anima
Starting rule:
- tags for appendage identity
- one concise NL sentence for role assignment candidate
- actor/target appearance anchors if needed

High-risk:
- `ATTRIBUTE_LEAKAGE`
- `BINDING_LOST`
- `COUNT_FAILURE`

Community signal:
- Animaはmulti-character/relationで強いという報告と、detailsを増やすとbleedingするという報告が両方ある。
- したがって `CONTROLLED_AB_REQUIRED`。

---

## 4.E Ultra-niche body-site / insertion lane

This lane includes extremely specific body-site/object concepts. Concrete explicit prompt strings are not stored here; use Special identity + placeholders.

### WAI v17
Risk order:
1. `MODEL_TRIGGER_MISMATCH`
2. `SITE_WRONG`
3. `VISIBILITY_LOST`
4. `OVERPROMPTED_CONFLICT`

Default test:
- canonical special only
- + one body-site support
- + one visibility support

### NoobAI 1.1
Risk order:
1. `MODEL_TRIGGER_MISMATCH`
2. `SITE_WRONG`
3. `OBJECT_DEGRADES`

Default test:
- special canonical
- alias/alternate candidate if dictionary evidence exists
- special-first position retained

### Illustrious
Risk order:
1. `MODEL_TRIGGER_MISMATCH`
2. `GEOMETRY_BREAK`
3. `SITE_WRONG`

Default test:
- tag baseline
- NL support only if exact version demonstrates benefit

### Anima
Risk order:
1. `BINDING_LOST`
2. `SITE_WRONG`
3. `OVERPROMPTED_CONFLICT`

Default test:
- tags baseline
- + shortest relation/site sentence candidate
- stop adding text when relation improves but scene detail starts bleeding

---

# 5. Cross-family Stage10 routing hypotheses

## 5.1 WAI v17
Candidate profile: `LEAN_TAG_FIRST`

Escalation ladder:
1. core Special
2. one Meaning/Site support
3. one Geometry/Visibility support
4. minimal negative adjustment
5. if still broken -> Prompt-only limit review

Do **not** use long quality/negative expansion as default rescue.

## 5.2 NoobAI 1.1
Candidate profile: `SPECIAL_FIRST_NATIVE_CAPTION`

Escalation ladder:
1. canonical special in native caption position
2. required general support
3. alias/alternate surface A/B if evidence exists
4. relation support only after native tag path is tested

## 5.3 Illustrious
Candidate profile: `VERSION_SENSITIVE_TAG_CENTERED`

Escalation ladder:
1. exact-version tag baseline
2. targeted support
3. exact-version NL candidate
4. regional/inpaint/assisted-control review for persistent binding failures

Do not generalize WAI derivative behavior to Onoma base, or vice versa.

## 5.4 Anima
Candidate profile: `HYBRID_RELATION_AWARE`

Escalation ladder:
1. tags baseline
2. one short relation sentence
3. appearance anchors for multiple actors
4. one visibility/geometry support
5. if details bleed with complexity -> reduce prose before adding more
6. assisted control if persistent multi-object/LoRA conflict

---

# 6. Most valuable A/B questions

Priority order for hard-target Stage10:

1. **tag-only vs tag + one relation sentence** by family
2. **canonical vs Alias/alternate surface** for rare special
3. **broad theme vs specific special**
4. **no visibility support vs exactly one visibility support**
5. **one function vs multi-function** for appendage/device lane
6. **short negative vs generic long negative** especially WAI
7. **special-first vs reordered special** especially NoobAI
8. **no appearance anchor vs appearance anchor** especially Anima multi-actor
9. **Prompt-only vs assisted control** after repeated binding/geometry failure

---

# 7. Audit rule: do not confuse prettier with more correct

A variant is not winner merely because finish quality improved.

Always keep at least:
- `TARGET_SCORE`
- `SITE_SCORE`
- `BINDING_SCORE`
- `OBJECT_INTEGRITY_SCORE`
- `GEOMETRY_SCORE`
- `VISIBILITY_SCORE`
- `IMAGE_QUALITY_SCORE`
- `USER_REPAIR_COST`

If quality improves while target/binding drops, record trade-off rather than single winner.

---

# 8. Evidence status

### Strong / official
- WAI v17 prompt/negative restraint guidance
- NoobAI 1.1 caption ordering
- Anima mixed prompting and multi-character appearance guidance
- Illustrious v1.1 official natural-language capability statement

### Community-supported only
- Anima natural-language superiority for difficult relation scenes
- SDXL/Illustrious multi-character binding limitations
- regional/inpaint necessity thresholds

### Stage10 required
- hard-category-specific winner grammar
- exact support count/density
- canonical vs alias model-response equivalence
- exact negative minimum set
- exact prompt-only ceiling

---

# 9. Boundary

- production data/spec is unchanged.
- #32 verdict is unchanged.
- KNOWLEDGE #44 corpus is untouched.
- Stage10 production A/B is not started.
- This matrix is a PROMPT-side audit/test planning artifact only.
