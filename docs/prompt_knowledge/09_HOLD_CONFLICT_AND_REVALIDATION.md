# 09 HOLD, conflict and revalidation

Owner: PROMPT / Issue #5
Status: consolidated uncertainty register. **HOLDをFACTへ昇格させない。**

## 目的

PROMPT班の未確定事項を一箇所へ集める。

この文書にあるものは、忘れてよい宿題ではなく、**production behaviorを決める前にexact model/local A/Bまたは上位証拠が必要なもの**。

---

## A. Semantic / render surface

### A1 canonical / Alias / model-trigger equivalence
HOLD。

semantic identityが同じ/近いことと、checkpoint responseが同じことは別。

必要:
- canonical
- approved Alias
- evidence-backed alternate surface
のcontrolled A/B。

### A2 broad vs specific
HOLD as generation rule。

semantic hierarchyはDanbooruで確認できるが、broad+specific/specific-onlyどちらがrealizationに良いかはmodel/target dependent。

### A3 e621 -> NoobAI response
HOLD。

NoobAIのe621 training factはあるが、non-human/appendage hard targetsが実際に優位とは未証明。

---

## B. Support / structure

### B1 CORE_SUPPORT + ADDITIVE auto-selection
HOLD for effectiveness。

Stage9 semantic safetyとしては有用でも、generation benefit・side effectsは未確定。

### B2 family block order / Special position
HOLD beyond official baseline。

training caption orderは強いbaselineだがinference optimumではない。

### B3 support presence == support utility
REJECT as assumption。

supportをPromptに入れた事実だけでは成功扱いしない。

### B4 visibility phrase side effects
HOLD。

frame/viewpoint/full-body等でtarget observabilityは上がってもpose/relation/subject scaleが悪化し得る。

### B5 density / simultaneous Special limits
HOLD。

exact token数の閾値ではなく、concept/relation/support competitionを測る。

---

## C. Negative / quality / weighting

### C1 anatomy-sensitive Negative collision
HOLD / high priority。

unusual anatomy/limb configurationsとgeneric bad-anatomy negativesが衝突する可能性。

必要:
- Negative ON/OFF
- target retention
- unwanted artifact suppression
を別評価。

### C2 family-specific Negative profiles
HOLD。

WAI17はlean author baseline候補。
NoobAI/Anima/Illustriousはexact profile/version別。

global万能Negative禁止。

### C3 quality/meta minimum set
HOLD by family。

quality語増加はtarget fidelity/style/compositionへ副作用を持つ。

### C4 automatic weighting
HOLD / currently NO。

必要性が実画像で出たtargetだけneutral vs one controlled weight。

### C5 numeric community weights
`MODEL_LOCAL_OBSERVATION`のみ。

global defaultへ昇格しない。

---

## D. Model-specific conflicts

### D1 WAI17 author primary source
Current author/mirror guidanceは強いがfinal production promotion前にexact author primary再照合を望む。

### D2 Illustrious version flattening
禁止。

v0.1/v1.0/v1.1/v2+およびWAI derivativesを分離。

### D3 Anima count surface
公式tag mode: `1girl/1boy`。
communityでspaced countの実践例があってもglobal defaultにはしない。

もしderivative/workflowで優位性主張が出ればexact A/B。

### D4 Anima Qwen “1k token limit”
`RATIONALE_INCORRECT`。

長文化を避ける実践原則は残るが、1k固定/300 words固定production ruleは不採用。

### D5 Anima BREAK
`ENV_SPECIFIC_HOLD`。

BREAKはparser/runtime feature。Anima universal model ruleにしない。

### D6 Anima Turbo CFG=1 × Negative
HOLD exact Forge behavior。

standard CFG theoryではguidance scale 1でusual classifier-free guidanceの意味が変わる/無効になる。
Forge Neo Anima実装やNegPiP等のextension差があるためexact local A/B必要。

### D7 NoobAI camera placement
HOLD。

native caption schemaにcamera専用最適位置は公式確定していない。捏造しない。

---

## E. Runtime / parser / postprocess

### E1 A1111/Forge weighting syntax
parser-scoped fact。exact weight効果はmodel-specific。

### E2 CLIP chunk / 75-token / BREAK知識
SD/SDXL parser lane限定。
Anima等へ無条件移植しない。

### E3 Hires.fix semantic retention
HOLD。

base -> second passでrepairもdriftもあり得る。
pre/post分離。

### E4 ADetailer impact on Special judgement
HOLD。

base failureをlocal inpaintが修復する場合がある。
pre/post分離。

### E5 LoRA interaction
HOLD。

- style dominance
- concept interference
- trigger collision
- identity drift
- base Special suppression

`weight 0.Xなら安全`のglobal閾値なし。

### E6 Forge Couple / Regional assistance threshold
HOLD for automatic escalation。

assisted controlは候補として有効だが、いつ自動案内するかはStage10/future #42 evidence待ち。

---

## F. Evaluator

### F1 WD EVA02 rare coverage
Known structural limit:
- 600 images未満tagはtraining vocabularyからfilter

HOLD:
- final Special corpusでのcoverage
- class-specific threshold
- alias/component-only routing

### F2 global threshold
禁止仮定。

model-card P=R thresholdやeasy tag marginをrare/composite/relationへそのまま使わない。

### F3 relation/binding machine judgement
原則REVIEW lane。

blind spots:
- VOCAB_ABSENT
- VOCAB_ALIAS_ONLY
- TARGET_TOO_RARE
- COMPONENT_ONLY_DETECTION
- RELATION_NOT_EXPRESSED
- BINDING_NOT_EXPRESSED
- COUNT_AMBIGUOUS
- OCCLUDED_TARGET
- CROPPED_TARGET
- CONFIDENCE_NEAR_TIE
- EVALUATOR_MODEL_DISAGREEMENT
- HUMAN_EVALUATOR_DISAGREEMENT

`REVIEW`はfailureではない。

### F4 final evaluator allocation
Dictionary freeze + KNOWLEDGE coverage待ち。

---

## G. User effort / product doctrine

### G1 selected Special same surface forever
Stage9 safetyとしては有用だがfinal doctrineとしてHOLD。

identity/provenanceを守りつつ、validated model-facing surfaceを使う余地をfuture decisionへ。

### G2 user choice is always safer/better
REFRAME candidate。

可能ならRecommended default + secondary alternatives、ambiguityだけreview。

### G3 Negative warning-only
REFRAME candidate。

family/target-specific safe Negative suggestionが有用かStage10で確認。

### G4 Prompt-only is only success form
REJECT as product doctrine。

Prompt-only能力は独立評価しつつ、ceiling後はassisted laneを持つ。

### G5 automatic assisted-control escalation
HOLD。

production UI/runtime decisionはPROMPT単独権限外。

---

## H. Experiment methodology

### H1 one seed
production rule確定には不足。

### H2 family cross-comparison settings
2種類を分離:
- `CONTROLLED_SAME_SETTINGS`
- `FAMILY_OPTIMAL_BASELINE`

結論を混ぜない。

### H3 resolution/aspect ratio
semantic test conditionの一部。

full-body/visibility/subject scaleへ影響するのでPromptだけの効果としない。

---

## Revalidation priority after gates

1. support auto-selection
2. family block order / Special position
3. multi-Special retention + binding
4. visibility side effects
5. density/minimum sufficient
6. canonical/Alias/trigger surface
7. tag-only vs short relation sentence
8. Negative
9. quality/meta
10. user effort/replacement burden
11. Prompt-only ceiling/assisted control

WAI17-first実験では `10_WAI17_LOCAL_FIRST_PROFILE.md` を優先。

## Future #42 connection

現在#42はRESERVED ONLY。

Stage10前のproduct-purpose improvement候補として、上記のうちproduction architecture変更を伴うものは、activation条件を満たしてから#42/DEVへ正式handoffする。

## 詳細資料

- `docs/stages/STAGE_10_PROMPT_REVALIDATION_BACKLOG_20260909.md`
- `docs/stages/STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md`
- `docs/stages/STAGE_10_PROMPT_AUDIT_RUNTIME_EVALUATOR_SUPPLEMENT.md` on branch `prompt/audit-knowledge-reservoir-20260909`
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
