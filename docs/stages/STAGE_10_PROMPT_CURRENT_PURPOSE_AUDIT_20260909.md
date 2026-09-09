# Stage10 PROMPT current-purpose audit

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT-side audit candidate. **Not production specification.**

## 1. Current purpose reconstructed from current GitHub + latest user direction

DanbooruTagToolの目的を、単なる「日本語↔Danbooruタグ変換」ではなく、次として扱う。

> **日本語の制作意図から、Specialを核に必要な補助・構造を選び、対象model familyで成立しやすく、ユーザーの手直しが少ない実用Promptへ変換するローカル非LLM制作支援。**

目的の中心は辞書整備そのものではなく、最終的に狙った画像へ到達しやすくすること。

### 現在の優先順位

1. **制作意図の保持** — ユーザーが欲しい意味・強度・関係を勝手に薄めない。
2. **生成成立性** — canonicalを並べただけでなく、model family上で成立しやすい構造へする。
3. **複合成立性** — multiple-Special / actor-target / body-site / relation / visibilityを扱える。
4. **ユーザー負担最小化** — タグ探索、support選択、Prompt再構築を可能な範囲でPROMPT/Composer側が担う。
5. **日本語中心操作** — 日本語の意図・表示・検索から入り、model-facing出力はcanonical English/Danbooru表現を保持する。
6. **model family差の保持** — WAI / Illustrious / NoobAI / Anima等を一つのgrammarへ潰さない。
7. **ローカル非LLM runtime** — 開発時に得た知識をデータ/ルールへ落とし、実利用時はLLMへ依存しない。
8. **再現・監査可能性** — なぜそのSpecial/supportが入ったかと、実際に生成へ渡ったPromptを追跡できる。

## 2. What remains correct from existing Prompt design

### KEEP-01 — 実験分離モードと実戦Stress Testモードの分離

現行方針は維持。

- 実験分離: 1実験1疑問、A/B差分以外固定。
- Stress Test: 実利用に近い完成Promptとして、必要なquality / camera / geometry / visibility / relation / aesthetic supportを組む。

両者を混ぜると、「実験として綺麗だが実戦では弱いPrompt」または「実戦では強いが何が効いたか分からないPrompt」になる。

### KEEP-02 — model familyの分離

現行方針を強く維持。

Prompt grammar、quality/meta、Negative、natural-language併用、Special位置、supportの効き方をglobal truthにしない。

### KEEP-03 — Special / support / canonical identityのtraceability

SpecialをGeneral supportへ黙って吸収しない、supportがSpecial identityを置換したことにしない、canonical/Alias/Semanticを混同しない、というtraceability原則は維持。

### KEEP-04 — one-question A/B / metadata traceability

Stage10検証では維持。

### KEEP-05 — unsupported / low-confidenceをREVIEWへ送る

自動評価器がrelation/binding/rare conceptを理解できない場合、REVIEWは失敗ではなく正しいrouting。

### KEEP-06 — Promptの無用な肥大化を避ける

「supportは多いほど良い」「quality語を多く足すほど良い」を前提にしない。最小十分Promptを最終的な品質目標の一つにする。

### KEEP-07 — replacement slot最小化

ユーザーへSpecial探索・Prompt設計を戻さない。必要な境界だけ最小slot化し、周辺構造はPROMPT側で完成させる。

## 3. Rules that are valid as Stage9 safety but may be too strong as final product doctrine

以下は**今すぐ変更しない**。PROMPT班からの再検討候補として記録し、必要ならfuture #42 / DEV decisionへ渡す。

### REFRAME-01 — 「Selected Specialは常にPrompt tokenとして残る」

Stage9安全策としては妥当。誤ったgeneralizationやsilent replacementを防いだ。

ただし最終目的は「Special tokenを守ること」自体ではなく、**ユーザーの制作意図を最も高い確率で画像へ成立させること**。

将来、controlled image evidenceにより、
- canonical vs Alias/trigger variant
- broad + specific
- model-specific alternate spelling
- short relation sentence
- assisted control

の方が意図保持に優れると確認された場合、Special identity/provenanceを保持したまま**render strategyを変える余地**は再検討すべき。

禁止すべきなのは「意味を勝手に薄める・追跡不能に置換すること」であり、永続的に同一文字列を必須にすることとは分けて考える。

**Status: CANDIDATE_FOR_FUTURE_DECISION / no current spec change.**

### REFRAME-02 — user choiceを要求すること自体を安全側の正解としない

Stage9ではALTERNATIVE / CONTEXTUAL等をuser choiceへ送る設計が安全だった。

現在目的では、ユーザー負担の少なさも主要品質指標。

将来は、証拠が十分な場合に
- 第一推奨を自動で明示
- 理由付きでalternateを折りたたむ
- ambiguousのみuser review

のように、「選択肢を出す」より「高品質な既定候補を出し、必要時だけ選ばせる」方向を検討する価値がある。

**Status: REFRAME / UI-runtime changeはPROMPT権限外。**

### REFRAME-03 — Negativeを単なるpass-throughと考え続けない

Stage9でsilent rewrite禁止は維持。ただし最終Prompt支援では、model familyとtarget Specialに対してNegativeが明確に衝突する場合、警告だけでなく**推奨Negative profile候補**を提示できる方が実用目的に近い。

自動変更はStage10 evidenceなしに行わない。

**Status: HOLD_FOR_IMAGE_EVIDENCE.**

### REFRAME-04 — Prompt-onlyを唯一の成功形にしない

DanbooruTagTool本体の主役はPrompt生成だが、複雑relation/pose/bindingにPrompt-only ceilingがある場合、ControlNet/OpenPose/Regional/Forge Couple等を「Prompt失敗の隠蔽」ではなく別 assisted-control laneとして案内できる設計余地は残す。

ただしPrompt-onlyの能力評価とassisted resultを混ぜない。

**Status: FUTURE_OPTION / not current core requirement.**

## 4. Current definition of a good Prompt

今後PROMPT班がPromptを監査する時、canonical文字列の正しさだけではPASSにしない。

### P1 Intent fidelity
- ユーザー指定の意味、関係、強度、対象を保持している。
- broad化、soft化、別概念化がない。

### P2 Semantic traceability
- Special / canonical / Alias / Semantic / supportの役割が追える。
- supportがSpecial identityに化けていない。

### P3 Model-family fitness
- 対象familyに未検証の別family grammarを流用していない。
- quality/meta/Negative/natural languageの扱いがfamily scopeを保持している。

### P4 Visual realizability
- 必要なpose / geometry / actor arrangementが物理的・視覚的に成立可能な構成になっている。

### P5 Binding correctness
- actor-target、body-site、ownership、relationが誰に属するか不明確になっていない。
- multiple actor / multiple Specialで属性漏れ・役割逆転を誘発する構造を避けている。

### P6 Observability
- 対象Specialがcrop、occlusion、frame外、極端なangleで判定不能になりにくい。
- visibility supportは意味supportと分離している。

### P7 Conflict control
- same-role camera/pose、Positive/Negative、broad/specific、複数relation等の競合を把握している。
- user-explicit intentを無断削除せず、必要ならwarn/HOLDへ送る。

### P8 Minimum sufficiency
- 成立・観測・実用性に寄与しない decorationを惰性で足さない。
- Prompt長ではなく、競合concept / relation / support block数を見る。

### P9 User-effort efficiency
- ユーザーへ2788件探索を要求しない。
- 完成Promptへ可能な限り近づける。
- user choiceが必要な場合も、第一推奨と理由をPROMPT側が出す。

### P10 Reproducibility
- source/template、resolved actual Prompt、Negative、model/settings、support変数を追跡できる。

### P11 Intervention transparency
- LoRA / Hires / ADetailer / ControlNet / regional prompting等を使った場合、Prompt-only成功として扱わない。

## 5. Prompt audit verdicts

PROMPT側の監査判定候補:

- `PASS_CURRENT_PURPOSE`
  - 現在目的に合い、既知HOLDを未検証FACTとして使っていない。
- `PASS_WITH_HOLD`
  - Promptは実用候補だが、特定のsupport/Negative/model反応をStage10で確認する必要がある。
- `REVISE_STRUCTURE`
  - 意図は正しいがcamera/geometry/binding/visibility/density等の構造が弱い。
- `REVISE_USER_EFFORT`
  - 意味は正しいがユーザーへ探索・再構築を戻しすぎている。
- `REJECT_INTENT_DRIFT`
  - user intent / Special specificity / relationを弱めたり別概念へ変えている。
- `REVIEW_MODEL_UNKNOWN`
  - model-family固有反応が未検証で、Prompt設計だけでは決められない。
- `REVIEW_SEMANTIC_AMBIGUITY`
  - canonical/Alias/Semantic/target relation自体が未解決。

## 6. Intake contract for KNOWLEDGE results

KNOWLEDGE #44が新しい知識を返した時、PROMPT班はそのままproduction ruleへコピーしない。

- exact official/strong evidence → **baseline candidate**
- controlled practical evidence → **ADOPT candidate / Stage10 confirm as needed**
- practical/community → **experiment hypothesis**
- conflicting sources → **controlled A/B**
- HOLD → **HOLDのまま**
- model-specific result → **そのfamilyだけ**

PROMPTへ取り込む際は「何を改善する知識か」を必ず分類する:

- intent/semantic
- model grammar
- geometry
- visibility
- binding/relation
- quality/aesthetic
- Negative
- density/pruning
- evaluator/routing
- assisted-control boundary

## 7. Immediate PROMPT-side conclusions

### ADOPT now

- 現在目的の評価軸を「正しいタグ列」から **意図保持 + 成立性 + 複合性 + model適合 + user負担 + traceability** へ広げる。
- Stage10 test Prompt監査でP1–P11を使用する。
- KNOWLEDGEの新成果は上記intake contractで受ける。
- Stress Testでは最小十分Promptを狙い、実験分離Promptの“削りすぎ”をそのまま実戦Promptへ持ち込まない。

### Do not change yet

- Stage9 production Composer invariant
- auto-selected support policy
- automatic weighting
- automatic Negative rewrite
- model-specific trigger replacement
- Prompt-onlyからassisted-controlへ自動昇格
- Stage10 winner/scoring/routing threshold

これらはPROMPT班単独の仕様変更対象ではない。

## 8. Old assumptions most likely to require future revalidation

1. Special tokenを永久に同一surface formで残すことが、常に最善の生成結果につながる。
2. user choiceを多く残すほど安全で良いUXになる。
3. supportをPromptへ足すことと、実際の成立率改善が同義である。
4. Negative warningだけで十分で、model/target別推奨は不要である。
5. Prompt-onlyで解けないケースは単純にPrompt失敗として扱えばよい。
6. easy/common tagで得たPrompt ruleがrare/composite/relational Specialへ移植できる。
7. canonical identityとmodel trigger surfaceが同じであることを期待する。

これらは廃止決定ではなく、**Stage10 / future #42で優先的に証拠確認する古い仮定候補**とする。

## 9. Boundary

この文書はPROMPT班の現在目的監査。

- production `data/**` を変更しない。
- Stage9 Composer仕様を上書きしない。
- Issue #32辞書verdictを変更しない。
- KNOWLEDGE #44の役割を代行しない。
- Stage10本番A/B開始を認可しない。
- main mergeは行わない。
