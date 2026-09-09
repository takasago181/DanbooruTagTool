# Stage10 PROMPT — Stage9 delta audit against current high-quality hard-image goal

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT-side audit candidate. No production specification change.

## Purpose

Stage9 Prompt Composerは、安全で決定的なComposer基盤を作る目的では非常に良く機能した。

ただし現在の製品目的は、より明確に次へ寄っている。

> **高品質で生成難度の高い成人向け・ニッチ・複合画像を、日本語意図から少ない手直しで狙い通り生成できるPromptへ変換する。**

そのため、Stage9の各安全策を以下へ分類する。

- `KEEP_CORE` — 現在目的でも中核原則
- `KEEP_TRACEABILITY` — 生成最適化とは別に追跡性のため維持
- `REFRAME` — 文言/目的を再解釈すべき
- `STAGE10_TEST` — 実画像根拠で判断すべき
- `FUTURE_DEV_DECISION` — PROMPT単独では変更不可
- `REJECT_AS_FINAL_DOCTRINE` — Stage9安全策として有効でも最終製品の絶対原則にはしない

---

## 1. Special identity / rendering

### S9-01 Special is first-class and never demoted to General support
Verdict: `KEEP_CORE`

理由:
- Special中心という製品目的そのもの。
- supportによってユーザー意図が一般化される事故を防ぐ。

ただし「first-class」は**identity/provenance上の地位**を意味し、同じsurface tokenを永久固定することとは分離する。

### S9-02 Support may help but never replace Special identity
Verdict: `KEEP_CORE + REFRAME`

保持:
- semantic identityをsupportで黙って置換しない。

再解釈:
- model-specific trigger / approved Alias / relation sentence等が画像上より有効だとStage10で確認された場合、identityを保持しながらrender strategyを変更する余地は残す。

### S9-03 Distinct Special identities are never silently collapsed
Verdict: `KEEP_TRACEABILITY`

画像生成時にrender tokenが一部共有されても、ユーザーが選んだ別identityは内部で失わない。

### S9-04 Same rendered token may dedupe while preserving owners
Verdict: `KEEP_CORE`

Prompt肥大化防止とtraceabilityの両方に一致する。

### S9-05 Canonical/Alias authority resolves identity, not generation superiority
Verdict: `KEEP_CORE`

辞書上の正規化とmodel responseは別問題。

`canonical vs Alias vs family trigger` は `STAGE10_TEST`。

---

## 2. Support selection

### S9-06 CORE_SUPPORT + ADDITIVE auto-selected by default
Verdict: `STAGE10_TEST`

Stage9 spec自身がsemantic supportはgeneration effectivenessの証明ではないとしている。

現製品目的では、意味的に正しいだけでなく次を満たす必要がある。
- target成立率が上がる
- bindingが壊れない
- composition driftが許容範囲
- artifactが増えない

将来候補:
- always auto-select
- family-specific auto-select
- Special-specific validated auto-select
- recommended-only

### S9-07 ALTERNATIVE requires user choice
Verdict: `REFRAME + FUTURE_DEV_DECISION`

Stage9安全策として妥当。

しかしユーザー負担を減らす現在目的では、証拠が十分なら
- recommended defaultを1つ提示
- alternativesはsecondary
- meaning ambiguityだけREVIEW
が望ましい可能性が高い。

### S9-08 CONTEXTUAL suggested unless context known
Verdict: `KEEP_CORE`

ただしcontextがComposerで判定できるようになった場合、validated ruleに限り自動推奨へ進める余地を残す。

### S9-09 OPTIONAL_VARIATION is suggested, not auto-selected
Verdict: `KEEP_CORE`

高品質化とvariationを混同しないため維持。
Aesthetic/variationはtarget成立後に扱う。

### S9-10 UNRESOLVED / NO_SUGGESTION remain valid
Verdict: `KEEP_CORE`

無根拠supportを発明して高品質に見せない。

---

## 3. Prompt density / dedupe

### S9-11 No universal role-count threshold
Verdict: `KEEP_NOW + STAGE10_TEST`

global thresholdは維持しない。
将来、family / role / failure class別のvalidated limitが得られればprofile rule候補。

### S9-12 No automatic weighting
Verdict: `KEEP_NOW + STAGE10_TEST`

weightは無害な強度調整ではなく別intervention。
neutral baselineとのA/Bが必要。

### S9-13 No rule that duplicate tags strengthen generation
Verdict: `KEEP_CORE`

重複による見かけの強調をproduction doctrineにしない。

### S9-14 Safe identity-based dedupe only
Verdict: `KEEP_CORE`

fuzzy/substringによる意味削除を防ぐ。

### S9-15 broad + specific is not automatically redundant
Verdict: `KEEP_CORE + STAGE10_TEST`

画像上では有効な場合も競合する場合もあり得る。
辞書意味だけで削除しない。

### Current reinterpretation of Prompt-bloat avoidance
Verdict: `REFRAME`

旧来の誤読:
- 短いほど良い

現在:
- **target成立に必要な構造は入れ、効果のない/重複/競合だけ削る**
- hard imageはeasy imageよりsupportが多くてもよい

---

## 4. User explicit choices

### S9-16 User-explicit choices are not silently removed
Verdict: `KEEP_CORE`

ユーザー意図保全のため維持。

ただし現目的では、conflictを検出した際に
- `Faithful` — 元入力保持 + warning
- `Recommended` — conflictを解消した候補
を併存させる方向を将来検討する。

Verdict for dual-output idea: `FUTURE_DEV_DECISION`

### S9-17 Explicit include overrides default-off
Verdict: `KEEP_TRACEABILITY`

### S9-18 Explicit exclude overrides auto-selection
Verdict: `KEEP_TRACEABILITY`

ユーザーoverrideは保持するが、quality riskがある場合はwarning理由を出せる方がよい。

---

## 5. Candidate-source lanes

### S9-19 Semantic / cooccurrence / user explicit lanes remain separate
Verdict: `KEEP_CORE`

意味根拠と統計根拠を一つのopaque scoreに潰さない。

### S9-20 Do not combine all evidence into one opaque ranking score
Verdict: `KEEP_CORE`

ただしuser-facing UIで全laneを毎回見せる必要はない。
内部evidenceを保持したままrecommended resultへ集約するのは将来検討可能。

Verdict for UI simplification: `FUTURE_DEV_DECISION`

### S9-21 Co-occurrence Conditional Rate is not proven utility
Verdict: `KEEP_CORE`

生成品質との因果を混同しない。

---

## 6. Conflict policy

### S9-22 Positive/Negative exact collision warning
Verdict: `KEEP_CORE`

### S9-23 Adult intent vs Negative `nsfw` warning
Verdict: `KEEP_CORE`

### S9-24 Negative remains unchanged except warning
Verdict: `REFRAME + STAGE10_TEST`

Stage9 pure Composerでは妥当。
最終製品では、targetと衝突しないfamily-specific Negative candidateを推薦できる方が高品質目的に合う可能性がある。

自動rewriteはStage10 evidence + DEV decisionなしに行わない。

### S9-25 No warning merely because N same-role tags exist
Verdict: `KEEP_NOW`

ただしStage10でfamily/role-specific conflict evidenceが出れば、approved incompatibility authorityとして追加可能。

### S9-26 User conflict retained + non-destructive warning
Verdict: `KEEP_CORE`

高品質化を理由にuser intentを黙って削らない。

---

## 7. Model-aware profiles

### S9-27 Model behavior must be profile-driven, not global
Verdict: `KEEP_CORE`

現在目的ではむしろ重要度が上がった。

### S9-28 Anima must not inherit Illustrious/WAI/NoobAI assumptions globally
Verdict: `KEEP_CORE`

### S9-29 Baseline block order is project profile, not universal truth
Verdict: `KEEP_CORE + STAGE10_TEST`

family別block order / Special positionを実画像で検証する。

### S9-30 validation_status distinguishes design candidate vs image-validated
Verdict: `KEEP_CORE`

production-quality toolでは必須に近い。

---

## 8. Stage10 reversible knobs

### S9-31 Special position reversible
Verdict: `KEEP_CORE`

### S9-32 broad-support additions reversible
Verdict: `KEEP_CORE`

### S9-33 role density reversible
Verdict: `KEEP_CORE`

### S9-34 weight reversible
Verdict: `KEEP_CORE`

### S9-35 LoRA contraction reversible
Verdict: `KEEP_CORE`

これらはwinnerをStage9で決めなかった点が正しい。

---

## 9. LoRA / assisted control / post-processing

### S9-36 No automatic LoRA Prompt contraction
Verdict: `KEEP_NOW + STAGE10_TEST`

LoRA導入で元tag/supportが不要になるとは限らず、逆にcompetitionを起こす可能性もある。

### S9-37 No automatic CFG/model-setting change with LoRA
Verdict: `KEEP_CORE`

### S9-38 Prompt-only as primary baseline
Verdict: `KEEP_BASELINE + REFRAME`

DanbooruTagToolはPrompt支援が主役なのでPrompt-only baselineは必要。
ただし難しいrelation/pose/bindingでceilingへ達した時、無限にsupportを追加することを成功戦略にしない。

将来:
- `PROMPT_ONLY`
- `ASSISTED_CONTROL_CANDIDATE`
を明確に分ける。

### S9-39 Hires/ADetailer/etc. rescue does not prove base Prompt success
Verdict: `KEEP_TRACEABILITY`

高品質最終画像の評価とPrompt-only能力評価を別軸にする。

---

## 10. Ordering / rendering

### S9-40 Preserve user order where practical
Verdict: `KEEP_TRACEABILITY`

生成性能上の最適順序とは別。

### S9-41 Preserve selected Special order
Verdict: `KEEP_TRACEABILITY + STAGE10_TEST`

ユーザー順を履歴として保持しつつ、family-specific render order最適化の可能性は別途検証できるようにする。

### S9-42 Baseline `RELATION` immediately after `COUNT`
Verdict: `STAGE10_TEST`

project baselineとして保持。global optimalとはしない。

### S9-43 Negative is separate channel
Verdict: `KEEP_CORE`

### S9-44 Reuse canonical/tag rendering convention
Verdict: `KEEP_NOW`

ただしfamily-specific surface differencesが実証された場合はprofile-specific renderer候補。

---

## 11. Stage9 test philosophy vs current product quality

Stage9 test suiteは主に
- deterministic
- no data loss
- no silent rewrite
- provenance
- reversible profile
を保証した。

これは現在も重要だが、**高品質画像生成能力そのものを保証してはいない**。

現在追加で必要なStage10 evidence:

1. target visual realization
2. multi-Special retention
3. actor-target / body-site binding
4. geometry / visibility effectiveness
5. quality/coherence
6. Negative interference
7. family-specific grammar
8. prompt density / conflict curve
9. user repair burden
10. Prompt-only ceiling

---

## 12. Highest-risk Stage9 assumptions for the current goal

優先順:

### RISK-1
`CORE_SUPPORT + ADDITIVE = auto-selectしてよい`

意味関係しか証明していないため、生成品質のfalse confidenceにつながりやすい。

### RISK-2
`same canonical surface = best model trigger`

identityとgeneration responseを混同する恐れ。

### RISK-3
`user choiceへ送れば安全`

品質は守れても操作負担が高く、完成品として弱い可能性。

### RISK-4
`warningだけでNegative conflict対応は十分`

実用Promptとしてはtarget-safe recommendationが欲しい可能性。

### RISK-5
`minimal Prompt = good Prompt`

hard imageではunder-supportを起こし得る。

### RISK-6
`Prompt-only failure = supportをもっと足す`

ceilingを超えるとcompetitionが悪化する可能性。

---

## 13. Current PROMPT recommendation

現時点ではStage9 production仕様を変更しない。

Stage10では、Stage9を**安全なbaseline generator**として扱い、次を実画像で昇格/降格する。

- support auto-selection
- family block order
- model trigger surface
- quality/meta profile
- Negative profile
- density/pruning
- multi-Special support escalation
- user default recommendation

最終完成品では、

> **意味を守る安全性 + modelでの成立率 + 完成画像の品質 + 少ないユーザー作業**

を同時に満たすことを目標とする。

---

## Boundary

- production data変更なし
- Stage9 spec上書きなし
- #32 verdict変更なし
- KNOWLEDGE #44作業の代行なし
- Stage10 production A/B開始なし
- PROMPT班だけでDEV/UI仕様変更なし
