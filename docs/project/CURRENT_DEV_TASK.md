# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][TEMP][CALIBRATION_READY] Forge Neo A/B automation & external-tool integration`
- State: **ACTIVE / CALIBRATION_DESIGN**
- Branch: task branch to be created from latest `main` for Issue #30 calibration-design work
- Previous DEV: #43 `[NAMING][COMPLETED] Finalize Special Core Dictionary naming and freeze handoff`
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #44で確定した3 evaluator coverageを受け取り、Stage10本番A/Bの前に、代表Special Core Entry約30件を使った実画像キャリブレーションを再現可能な形で設計する。

今回のDEV passはまず設計・結果schema・ケース選定・実行手順・Gate定義を完成させる。`AUTO_CANDIDATE` を自動採点承認とみなさない。

## Authoritative #44 handoff

- Issue #44 correction checkpoint: `5614819866`
- machine-generated coverage commit: `557aa4c`
- #30 handoff sync commit: `dba23df`

Current desk results:
- Special: 2,788 / 2,788
- WD14 direct: 658 (23.60%)
- Kagami direct: 1,412 (50.65%)
- CL Tagger v2.00 direct: 1,704 (61.12%)
- 3-evaluator direct union: 1,725 (61.87%)
- observable including components: 1,957 (70.19%)
- exact 3-evaluator: true
- AUTO_CANDIDATE: 939
- REVIEW_REQUIRED: 1,018
- BLOCKED: 831
- relation/binding structural risk: 918

## Required work

1. latest `main` から Issue #30 用task branchを作る。
2. Issue #44の `representative_calibration_cases.csv` を優先し、約30件の代表ケースを確定する。
3. easyだけでなく、以下のhard/failure strataを必ず含める。
   - simple unary
   - rare / tail vocabulary
   - multiple Specials
   - person relationship
   - subject/object binding
   - body-part binding
   - quantity
   - spatial/directional relation
   - insertion/contact/restraint
   - compound Special
   - component-only
   - evaluator disagreement
   - AUTO_CANDIDATE control
   - REVIEW_REQUIRED boundary
   - BLOCKED failure control
4. 実画像キャリブレーション仕様書を作る。
5. machine-readable result schemaを作る。
6. 人間reference判定と WD14 / Kagami / CL v2.00 のraw outputを比較できる設計にする。
7. evaluator単独 / OR / AND / majority / CL中心+他補助 / disagreement→human review / limited component proxy を比較可能にする。
8. precision / false positive抑制をautomation率より優先した暫定routing ruleを定義する。
9. Stage10 production A/Bへ進める明示Gateを定義する。
10. 必要性が実証された場合のみ最小限の補助scriptを追加する。大規模な独自runner/GUI/dashboardは作らない。
11. review可能なbranch/commit/reportを残し、Issue #30へcheckpointできる状態にする。

## Result schema minimum

各画像について最低限:
- case_id
- Special ID
- canonical
- model / checkpoint / model version
- Prompt / Negative Prompt
- Seed
- sampler / steps / CFG / resolution
- LoRA state + weight
- generated image path/hash
- human reference verdict
- human judgment dimensions
- WD14 raw score / detected tags
- Kagami raw score / detected tags
- CL v2.00 raw score / detected tags
- evaluator correctness
- evaluator agreement/disagreement
- relation/binding required flag
- final calibration verdict

Human judgment dimensions should separate where applicable:
- target concept present
- actor/subject correct
- target/object correct
- body-part ownership/site correct
- count correct
- spatial relation correct
- compound elements retained
- unwanted extra interpretation
- usable for Stage10 preference judgment

## Evaluation rules

- Human image-level judgment is the reference; tagger vocabulary is not semantic authority.
- Direct vocabulary match does not prove relation/binding correctness.
- `AUTO_CANDIDATE` = calibration candidate only, not auto-score approval.
- subject/object, actor assignment, body-site ownership, count, spatial topology, insertion/contact/restraint, compound retentionは原則human review側に置く。画像校正証拠なしにAUTOへ昇格しない。
- evaluator disagreement / weak rare-tail / component-only proxyはhuman reviewへ戻せる設計にする。
- one experiment = one question.
- fixed seed / actual Prompt / metadata traceabilityを保持する。
- false positiveを増やしてまでautomation率を上げない。

## Preserved infrastructure baseline

- prior evidence branch: `codex/issue30-automation-dry-run-20260908`
- evidence commit: `f2fc7acb15f996630c9f008284d80cf3261fb32f`
- Forge Neo API: `neo-2.29`
- fixed model baseline: `waiIllustriousSDXL_v170` / hash `f116b0c78f`
- generation -> PNG SHA-256 -> `/sdapi/v1/png-info` -> evaluator raw output path already demonstrated

## Hard prohibitions

- Stage10 production A/Bを開始しない
- 2,788-image sweepをしない
- production `data/**` を変更しない
- #32 verdictを書き換えない
- canonicalを変更しない
- unvalidated scoring policyをproduction truthとしてfreezeしない
- model-family差をflattenしない
- protected-data/hash guardを弱めない
- 不要なForge Neo / extension updateをしない
- 外部ツールで足りるのに大型の独自automation platformを作らない

## Completion criteria

- calibration experiment specification exists
- machine-readable result schema exists
- about-30 representative case list + rationale exists
- execution procedure exists
- evaluator comparison strategy exists
- provisional AUTO / HUMAN REVIEW / BLOCKED promotion-demotion rules exist
- explicit Stage10 production-start Gate exists
- expected failure modes documented
- only justified minimal helper tooling added
- `data/**`, #32, canonical unchanged
- reviewable branch/commit/report available

## Start Gate

Codexは実装開始前に必ず:
1. latest `main` を取得する。
2. `docs/project/CURRENT_STATE.md` が Current Core DEV = **#30** であることを確認する。
3. このファイルの Source Issue = **#30** と Issue #30 本文のscopeが一致することを確認する。
4. stale #35 mirror/branchを見ている場合は更新し、なお不一致ならSTOPして報告する。

Issue本文・CURRENT_STATE・CURRENT_DEV_TASKが一致して初めて #30 calibration-design workを開始する。
