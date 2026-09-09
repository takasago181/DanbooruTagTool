# Stage10 PROMPT Toshiaki diffusion Wiki ingestion rules

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: prompt-side source ingestion contract candidate. **Not production specification.**

## 1. Purpose

としあきdiffusion WikiからPrompt知識を取り込む際、旧情報・model差・UI parser差・community仮説を混同しないための規則。

---

## 2. Required metadata per claim

Wiki由来claimをPROMPT knowledgeへ入れる場合、最低限以下を記録する。

- source page title
- source URL
- page last-modified date if available
- claim section
- target model family
- target model version / derivative if known
- UI/runtime: A1111 / Forge / Forge Neo / ComfyUI / unknown
- parser/extension if relevant
- evidence label
- external corroboration source if available
- known contradiction
- Stage10 validation need

**ページ更新日だけでclaimの鮮度を判定しない。**
本文中に「v0.1時点」「2023年情報」等があれば、そのclaimのeffective dateを優先する。

---

## 3. Evidence labels

### `OFFICIAL_MATCH`
Wiki claimがmodel author / official repo / official docsと一致。

利用:
- strong candidate
- ただし別familyへ横展開しない

### `COMMUNITY_VALIDATED`
community knowledgeだが、実装仕様・複数source・本プロジェクト知識と整合。

利用:
- Stage10 design candidate
- production factではない

### `COMMUNITY_CANDIDATE`
有望な日本語圏実践知識。

利用:
- A/B backlogへ
- auto rule化しない

### `RAW_COMMUNITY`
「みんなの呪文広場」等のmodel/version不明prompt fragment。

利用:
- support candidate discovery only
- semantic truth / causal effectには使わない

### `VERSION_SCOPED`
特定のmodel/version/checkpointに限って有効とみなす。

例:
- early Illustrious v0.1 prompting
- WAI v17 creator recommendation
- Anima Aesthetic/Turbo profile

### `UI_PARSER_SCOPED`
A1111/Forge parserやextensionによって成立する記法。

例:
- prompt editing
- `AND`
- `BREAK`
- Dynamic Prompts syntax

### `ENV_SPECIFIC_HOLD`
Forge Neo/ComfyUI/extension/version差で挙動が変わる可能性が高い。

### `CONTRADICTED_BY_OFFICIAL`
Wiki claimがofficial sourceと衝突。

利用:
- productionへ昇格禁止
- 誤り/モード混同の可能性を記録

### `RATIONALE_INCORRECT`
結論・実践注意には価値があっても、説明に使われた技術理由が誤っている。

利用:
- 実践部分と根拠部分を分離

### `HISTORICAL_ONLY`
現行familyへそのまま移植しない旧手法。

### `DO_NOT_PROMOTE`
根拠不足・危険な一般化・誤記・unscoped advice。

---

## 4. Mandatory separation axes

### 4.1 Model grammar vs UI parser grammar

以下を混同しない。

- modelが学習したcaption/tag surface
- tokenizer/text encoder behavior
- A1111 parser syntax
- Forge/Forge Neo parser behavior
- extension template syntax

例:
`[A:B:0.5]`がA1111で働くことは、Animaがこの文字列を学習していることを意味しない。

### 4.2 Canonical tag vs rendered Prompt surface

保持するもの:
- canonical identity
- alias relation
- semantic meaning

別に持つもの:
- family-specific rendered surface
- underscore/space handling
- escaping
- `@artist` 等のfamily-specific decoration

### 4.3 Base family vs derivative checkpoint

禁止:
- Illustrious base advice → WAI v17へ無検証コピー
- Anima Base advice → Aesthetic/Turboへ無検証コピー
- NoobAI advice → all Illustrious derivativesへ一般化

### 4.4 Prompt-only vs assisted-control success

Forge Couple / Regional / ControlNet / Inpaint等で成功した場合:
- Prompt-only成功として数えない。
- assisted-control laneとして記録。

---

## 5. Adoption workflow

1. Wiki claimを抽出
2. page date / claim date / model versionを確定
3. claim typeを分類
   - semantic
   - model grammar
   - parser grammar
   - generation setting
   - support heuristic
   - evaluator/tooling
4. official/author sourceを確認
5. contradictionを探す
6. evidence label付与
7. product goal relevanceを判定
8. 必要ならStage10 A/B questionへ変換
9. image evidence後にのみproduction candidateへ昇格

---

## 6. Prompt-specific ingestion rules

### 6.1 Positive/support terms

Wikiに「効く」と書かれていても:
- tag existence
- model recognition
- causal generation benefit
を分ける。

`support`に入れるには最低でも:
- meaning roleが説明可能
- targetを弱めない
- same-role競合がない
- model scopeが分かる
が必要。

### 6.2 Negative Prompt

古いテンプレを現行profileへ継承しない。

特に:
- WAI v17はauthor guidanceを優先
- anatomy-sensitive hard-targetではgeneric `bad anatomy / extra limbs` 等を機械投入しない
- CFG=1/Turboではnegative conditioning挙動を別確認

### 6.3 Weighting

Wikiのweight例は:
- parser syntax
- model response
の2段階に分ける。

高weightが効いた成功例だけからglobal defaultを作らない。

### 6.4 Natural language

Anima/新Illustrious等でNL候補がある場合:
- tag-only baselineを保持
- relation文は1要素ずつ追加
- prose lengthを無制限に増やさない
- appearance leakage / relation inversionを評価

### 6.5 Dynamic Prompts

Auditで利用する時:
- seed固定
- deterministic/combinatorial preference
- template保存
- resolved actual Prompt保存
- wildcard version/hashを可能なら保存

---

## 7. Tooling-specific rules

### Forge Neo
- versionを記録
- extension compatibilityをversion-pinnedで見る

### Forge Couple
- Prompt-only ceiling後の候補
- target regions / shared prompt / actor countを証跡化

### WD Tagger
- tool version/modelを記録
- raw confidenceを保存
- unsupported conceptをREVIEWへ
- ground truth扱い禁止

### X/Y/Z / Prompt S/R
- causal isolation思想は採用可
- old UI implementationへの依存はしない
- current #30 automationが同等以上ならautomationを優先

---

## 8. Explicit known corrections

- Anima tag-mode countはofficial exampleで `1girl/1boy`。Wikiの「`1 girl`が必須」型説明をglobal factにしない。
- Anima Qwen encoderを「1k token limit」とする説明を技術FACTにしない。
- generic Illustrious long-negative adviceをWAI v17へ継承しない。
- `BREAK` on Animaはparser/environment scopedとして扱う。

---

## 9. Historical quarantine

以下のような情報はmodern Stage10 defaultから隔離:
- 2022 NAI万能呪文
- SD1.5向け大量weightテンプレ
- old generic long-negative boilerplate
- version不明のsampler/CFG絶対値
- old extension compatibility claims

Historical knowledgeは「なぜ現在の慣習があるか」を理解する用途に限る。

---

## 10. Boundary

- This contract does not update production Prompt rules by itself.
- No #32/#44 authority is overridden.
- No Stage10 production A/B is authorized.
- Videos are excluded from this corpus.
