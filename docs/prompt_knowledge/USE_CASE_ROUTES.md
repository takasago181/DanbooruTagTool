# PROMPT Knowledge Use-Case Routes

Owner: PROMPT / Issue #5
Purpose: 「何をしたいか」から最短で必要文書へ到達するための読取ルート。
Last normalized: 2026-09-09

## 0. 新しいPROMPTチャットを復元する

Read:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 latest checkpoint
4. `docs/prompt_knowledge/README.md`
5. `CLAIM_REGISTRY.md`
6. 今やる用途のrouteだけ

Do not:
- legacy Stage10 docsを最初から全読する
- chat summaryをGitHubより優先する

---

## 1. WAI17でまずPromptを作る/試す

Read:
1. `10_WAI17_LOCAL_FIRST_PROFILE.md`
2. `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md`
3. `07_EVALUATION_AND_STAGE10_TESTING.md`

If failure:
4. `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md`

If quality/Negative/camera question:
5. `06_QUALITY_CAMERA_NEGATIVE_DENSITY.md`

Check unresolved:
6. `09_HOLD_CONFLICT_AND_REVALIDATION.md`

Current claim IDs to watch:
- `K-WAI-*`
- `K-STRUCT-*`
- `K-QUALITY-*`
- `K-TEST-*`

---

## 2. hard-target / niche categoryのPrompt構造を考える

Read:
1. `04_HARD_TARGET_GENRES.md`
2. `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md`
3. `02_MODEL_FAMILY_PROFILES.md`
4. `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md`

Do not:
- broad themeだけでrender-critical detailを代表させる
- familyを無視して同じPrompt grammarを使う

Useful claim groups:
- `K-SEM-*`
- `K-STRUCT-*`
- `K-FAIL-*`

---

## 3. 生成画像が狙い通りにならない原因を切り分ける

Read:
1. `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md`
2. `07_EVALUATION_AND_STAGE10_TESTING.md`
3. relevant model section in `02_MODEL_FAMILY_PROFILES.md`

Check in order:
- target missing?
- site wrong?
- actor/target binding?
- object integrity?
- geometry?
- visibility/crop?
- quality/style only?
- postprocess/control rescued it?

If repeated structural failure:
- check `K-FAIL-004`
- check `K-CTRL-*`

---

## 4. Stage10 A/Bを設計する

Read:
1. `07_EVALUATION_AND_STAGE10_TESTING.md`
2. `CLAIM_REGISTRY.md` — test対象claimのSTATUS/VALIDATION確認
3. target model profile
4. `09_HOLD_CONFLICT_AND_REVALIDATION.md`

Rules:
- one experiment = one question
- A/B差分以外固定
- exact checkpoint/runtime/seed/resolutionを保存
- multiple seeds before production rule promotion
- final PNGだけでbase Prompt successを判定しない

Current primary test IDs:
- `K-SEM-004`
- `K-STRUCT-004/005`
- `K-QUALITY-004/007/008`
- `K-WAI-005/006/007`
- `K-FAIL-004`

---

## 5. 新しいmodel family/checkpointを追加する

Read:
1. `00_KNOWLEDGE_GOVERNANCE.md`
2. `02_MODEL_FAMILY_PROFILES.md`
3. `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`
4. `VERSION_AND_FRESHNESS.md`

Process:
1. exact model/version official source
2. training/caption/prompt/settings claimsをsource-scopedで抽出
3. community知識を分離
4. existing family ruleを無断流用しない
5. new Claim IDsを作る
6. Stage10 validationが必要なoptimization claimをCANDIDATEにする
7. exact local checkpoint/hashがある場合Freshness registryへ

---

## 6. 新しいサイト/Wikiを「学習」する

Read:
1. `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`
2. `00_KNOWLEDGE_GOVERNANCE.md`
3. `LABEL_MIGRATION_MAP.md`

Audit:
- spelling/canonical
- model/version
- tag vs natural-language phrase
- success/failure sample conditions
- official conflict
- safety/out-of-scope
- freshness

Output:
- detailed audit evidence
- relevant category summary update
- Claim Registry update only for material claims
- HOLD/CONFLICT update
- Legacy source map entry
- Issue #5 checkpoint

---

## 7. 「この知識って本当に確定？」を確認する

Read only:
1. `CLAIM_REGISTRY.md`
2. target Claim ID row
3. if needed, `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`
4. evidence pointer / legacy doc

Interpret:
- `ACCEPTED` = scope内で現在採用
- `CANDIDATE` = 有望だがproduction確定ではない
- `HOLD` = 未解決
- `CONFLICT` = 根拠衝突
- `REJECTED` = current defaultとして使わない
- `HISTORICAL` = 履歴のみ

Do not infer status from prose tone in old docs.

---

## 8. 旧資料から根拠を追う

Read:
1. `LEGACY_SOURCE_MAP.md`
2. source document
3. `LABEL_MIGRATION_MAP.md` if old labels appear

Rule:
Legacy source = evidence/provenance.
Current verdict = `CLAIM_REGISTRY.md`.

---

## 9. HOLDだけ確認する

Read:
1. `09_HOLD_CONFLICT_AND_REVALIDATION.md`
2. `CLAIM_REGISTRY.md` high-priority unresolved section

Typical unresolved classes:
- render surface equivalence
- support effectiveness
- Negative collision
- visibility side effects
- density
- exact assisted-control threshold
- evaluator allocation

---

## 10. user負担を減らす設計を考える

Read:
1. `01_PRODUCT_PURPOSE_AND_GUARDRAILS.md`
2. `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md`
3. `09_HOLD_CONFLICT_AND_REVALIDATION.md` section G
4. claim group `K-UX-*`

Goal:
- userへ2788件探索を戻さない
- recommended defaultをPROMPT側で最大限作る
- ambiguityだけreview
- provenanceは保持

Production UI/runtime変更はDEV decisionが必要。
