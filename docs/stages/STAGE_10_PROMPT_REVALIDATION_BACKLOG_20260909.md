# Stage10 PROMPT revalidation backlog — current-purpose alignment

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: experiment/backlog candidate. No production rule changes.

## Purpose

`STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md` で抽出した「Stage9安全策としては合理的だが、現在の最終目的に対して未検証の仮定」を、Stage10/future #42で検証しやすい順に並べる。

現在目的:
- user intentを保持する
- model familyで成立しやすくする
- multiple-Special / relation / bindingを扱う
- userの手直しを減らす
- Promptを必要以上に肥大化しない
- runtimeはlocal / non-LLM

## Priority A — false confidenceを防ぐ

### A1. CORE_SUPPORT + ADDITIVE auto-selection effectiveness

**Current Stage9 behavior**
semantic `CORE_SUPPORT + ADDITIVE` はdefault auto-selected。

**Risk**
Stage9 spec自身が「semantic supportはgeneration effectivenessの証明ではない」としている。意味上関連するsupportが画像生成でも有効とは限らず、Prompt densityや競合を増やす可能性がある。

**Required test**
- Special only
- Special + one CORE additive
- 必要なら Special + all current CORE additive

同一seed/settingsで、
- Special retention
- target observability
- new artifacts/conflict
- Prompt density
を分離評価。

**Decision enabled**
- auto-select維持
- suggestedへ降格
- class/model-specific auto-select
- particular support relation only auto-select

### A2. Baseline block order / Special position

**Current behavior**
Stage9 baselineは `META_QUALITY -> COUNT -> RELATION -> IDENTITY -> SPECIAL -> SUPPORT...`。Special位置はprofileで可逆。

**Risk**
baselineはproject profileであってmodel truthではない。family別caption/trigger構造差がある。

**Required test**
familyごとに同一内容で最低限:
- current baseline
- family evidence-aligned position
- Special earlier/later variant where justified

**Decision enabled**
ComposerProfileのfamily別validated block order。

### A3. Support presence != support utility

**Risk**
Promptにvisibility/geometry supportが入ったことで「支援済み」と見なすと、実画像ではpose drift、crop、別部位強調、relation崩れが起きても見逃す。

**Required test**
各supportを一度に1blockだけ追加し、`NO_SUPPORT -> Frame -> Viewpoint -> Geometry -> targeted visibility` と段階化。

**Decision enabled**
support class別の実効性/副作用記録。

### A4. canonical / Alias / model-trigger surface equivalence

**Current safety rule**
identity/provenanceを保持し、silent replacementしない。

**Risk**
辞書identityとmodel response surfaceが同一とは限らない。

**Required test**
同じsemantic targetで
- canonical
- approved Alias
- family-specific known trigger variant（KNOWLEDGE evidenceがある場合のみ）
を比較。

**Decision enabled**
identityを保持しつつrender tokenをfamily/profileで選べるかの判断。

## Priority B — current user goal（狙った複雑画像）の成立率

### B1. Multi-Special retention / binding

**Required sequence**
`A_ONLY -> B_ONLY -> AB minimal -> AB + one targeted support`。

判定は単一winnerだけでなく:
- A retained?
- B retained?
- actor/target correct?
- body-site correct?
- relation correct?
- visibility sufficient?
を分ける。

### B2. tag-only vs short relation sentence

特にrelation/bindingが難しいfamilyで、tag列だけと短い自然文補助を別条件として比較する。

global adoption禁止。family別。

### B3. Prompt density / minimum sufficient

単なるtoken長ではなく、
- Special count
- support block count
- competing camera/pose count
- relation count
- aesthetic block count
を記録。

`minimum -> useful support -> over-supported` の破綻曲線を測る。

### B4. Visibility support side effects

`full body / cowboy shot / upper body / from side / three-quarter / focus` 等を「観測性だけを変える透明な補助」と仮定しない。

- target visibility
- pose fidelity
- relation fidelity
- subject size
- unintended composition drift
を同時記録。

## Priority C — user effort reduction

### C1. Default recommendation vs manual choice

Stage9はALTERNATIVE/CONTEXTUALをuser choiceへ送る。現在目的では、選択数を増やすほど良いとは限らない。

検討する出力:
- recommended default 1
- alternatives collapsed/secondary
- REVIEW only when ambiguity affects meaning

まずPrompt班のmanual testで「毎回何選べばいいかユーザーが考える必要がある箇所」を記録し、後でUI/DEVへhandoff可能にする。

### C2. Replacement slot burden

測る:
- slot count
- slot scope
- userがタグを検索する必要がある回数
- Prompt本文の再構築が必要か

目標はzero guaranteeではなく、必要最小。

### C3. Optimized suggestion vs faithful explicit output

user-explicit conflicting tagsを削除しない原則はtraceability上重要。

将来、
- `faithful` = user入力保持 + warning
- `recommended` = conflictを解消した候補Prompt
を別表示できると、無断変更せずuser負担を下げられる可能性。

PROMPT単独では仕様変更しない。

## Priority D — production-worthy model profiles

### D1. Negative profile candidates

Stage9ではNegativeを書き換えない。Stage10ではfamily/target別に、
- current user Negative
- minimal family baseline
- target-conflict-safe variant
を一質問ずつ比較する。

### D2. Quality/meta minimum set

quality/metaは画質だけでなくstyle/compositionを変え得るため、familyごとに最小setを確認し、追加語はindependent variableとして扱う。

### D3. Weighting

現在automatic weightなしを維持。必要性が実画像で示された場合のみ、neutral vs one controlled weightを比較。

自動weightへ直接進まない。

## Priority E — Prompt-only ceiling and assisted control

### E1. Escalation boundary

Prompt-onlyでrelation/pose/bindingが失敗してもsupportを無限追加しない。

同じfailure classがsupport escalation後も残る場合、
- PROMPT_ONLY_LIMIT
- ASSISTED_CONTROL_CANDIDATE
を分ける。

ControlNet/OpenPose/Regional/Forge Couple等で成功しても、Prompt-only successとして数えない。

## Proposed execution order after gates permit

1. A1 support auto-selection
2. A2 family block order / Special position
3. B1 multi-Special retention + binding
4. B4 visibility side effects
5. B3 density/minimum sufficient
6. A4 canonical/Alias/trigger surface
7. B2 tag-only vs short relation sentence
8. D1 Negative
9. D2 quality/meta
10. C1/C2 user-effort review
11. E1 Prompt-only ceiling

順番はfinal dictionary / KNOWLEDGE #44返却 / Stage10 Gateにより調整する。

## Non-actions

- Stage10本番A/Bをまだ開始しない。
- #32 verdictを変更しない。
- Stage9 Composer specを上書きしない。
- auto-selection/weighting/Negative rewriteをproductionへ実装しない。
- KNOWLEDGE #44の調査課題をPROMPT班が代行しない。
