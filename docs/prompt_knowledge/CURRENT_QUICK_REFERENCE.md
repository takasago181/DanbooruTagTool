# PROMPT Current Quick Reference

Owner: PROMPT / Issue #5
Purpose: 人間/ChatGPTが30秒程度でPROMPT班の現在知識を復元するための要約。
Last normalized: 2026-09-09

**これは詳細正本ではない。Current verdictは `CLAIM_REGISTRY.md`。**

---

## 1. 何を作っているか

DanbooruTagTool PROMPT側の目的:

> 日本語の制作意図からSpecialを核に、対象modelで成立しやすい構造/supportを選び、高品質で難しいニッチ/複合画像を少ない手直しで狙えるPromptへ変換する。

- runtimeはlocal / non-LLM
- userへ2788件探索を戻さない
- `minimum` = shortestではなくminimum sufficient
- target fidelityと見た目の綺麗さを別評価

---

## 2. 今まず使うmodel

**WAI Illustrious v17 + Forge Neo**

Exact local checkpoint:
`sd\\waiIllustriousSDXL_v170.safetensors`

SHA-256:
`f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`

Issue #30 pipeline:
`PASS_PIPELINE`

Author accepted baseline:
- Euler a
- Steps 15–30
- CFG 5–7
- Forge Neo recommended
- integrated VAE
- avoid excessive quality/aesthetic tags
- avoid overly long Negative

Project test candidate, **not yet production fact**:
- Steps 25
- CFG 6
- `LEAN_TAG_FIRST`
- 1024x1024 causal / 1024x1344 portrait stress
- Hires OFF semantic first pass
- LoRA/control OFF Prompt-only baseline

Claims:
- accepted: `K-WAI-001`–`004`, `K-WAI-008/010`
- candidate/HOLD: `K-WAI-005/006/007/009`

---

## 3. Model familyを混ぜない

### WAI17
- lean tag-first candidate
- short quality/Negative direction

### NoobAI 1.1
- official special-before-general caption structure
- native caption baseline

### Illustrious
- exact version required
- `booru-only` universal rule is rejected
- WAI derivativeをbaseへ流用しない

### Anima
- tags + natural language + hybrid supported
- official tag count `1girl/1boy`
- multi-character appearance description important
- short relation sentence optimizationはcandidate
- Qwen “1k token / 300 words” rationaleはrejected

---

## 4. Prompt内部で何を見るか

Hard targetは内部で分解:
- ACT
- SITE
- OBJECT
- ACTOR_A / ACTOR_B
- RELATION
- POSE / GEOMETRY
- VISIBILITY

これはuserへ8入力を要求する意味ではない。
PROMPT側が内部診断に使う。

---

## 5. 失敗の見方

「出なかった」で一括しない。

最低限:
- TARGET_MISSING
- SITE_WRONG
- BINDING_LOST
- OBJECT_DEGRADES
- GEOMETRY_FAILURE
- VISIBILITY_FAILURE
- ATTRIBUTE_LEAKAGE
- COUNT_FAILURE
- OVERPROMPTED_CONFLICT
- PROMPT_ONLY_LIMIT

Research-backed accepted principles:
- missing targetとwrong bindingは別failure
- multi-object/relationは別difficulty class
- attribute leakageは既知problem

---

## 6. 画像評価

別々に見る:
- T target
- B binding
- V visibility
- G geometry
- Q final quality
- C conflict/artifact
- M model evidence
- U user repair
- R reproducibility

**綺麗だけどtargetが消えた = successではない。**

WD EVA02:
- rare vocabularyには構造的限界あり
- unsupported/low confidenceはREVIEW
- relation/bindingをtag confidenceだけで確定しない

---

## 7. Promptだけで粘らない境界

Repeated controlled failureなら別lane候補:

- actor/attribute mixing -> Forge Couple / Regional
- pose/layout instability -> ControlNet
- local face/hand defect after semantic success -> ADetailer
- Hires -> second-pass finish/repair

**assisted success != PROMPT_ONLY success**

自動昇格threshold自体はまだHOLD。

---

## 8. 今の主要HOLD

高優先:
1. support auto-selectionは本当にgeneration benefitがあるか
2. family block order / Special位置の最適化
3. canonical vs Alias vs model-facing surface
4. visibility support副作用
5. Prompt density / multiple-Special pressure
6. anatomy-sensitive Negative collision
7. family-specific Negative / quality minimum set
8. WAI17 local-first candidate settings/grammar
9. Prompt-only ceiling判定
10. assisted-control automatic threshold
11. final evaluator allocation

Current statusは `CLAIM_REGISTRY.md`。
詳細HOLDは `09_HOLD_CONFLICT_AND_REVALIDATION.md`。

---

## 9. 情報を信じる順番

Claimの種類で正本を変える:

- tag meaning -> Danbooru
- exact model grammar/settings -> exact model official/author
- parser/extension -> official runtime repo
- failure mechanism -> research
- practical tips -> community + controlled reproduction

Community例だけでproduction ruleへしない。

---

## 10. 旧資料との関係

Current verdict:
`CLAIM_REGISTRY.md`

Readable explanation:
`01`–`10`

Old detailed evidence:
`docs/stages/STAGE_10_PROMPT_*.md`

Old label translation:
`LABEL_MIGRATION_MAP.md`

Old docとRegistryが食い違えば、current verdictはRegistry。

---

## 11. 新チャットの最短復元

1. CURRENT_STATE
2. PERMANENT_RULES
3. Issue #5 latest checkpoint
4. README
5. this Quick Reference
6. Claim Registry
7. WAI17 profile if current task is WAI
8. USE_CASE_ROUTES for task-specific reading

---

## 12. 今の停止地点

- Stage9 overall Gate: completed
- Stage10 production A/B: not started by PROMPT
- PROMPT: knowledge normalization + WAI17-first test preparation
- exact representative production testing waits current project gates

Do not infer that knowledge preparation means Stage10 production has started.
