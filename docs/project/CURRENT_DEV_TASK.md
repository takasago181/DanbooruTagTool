# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][TEMP][CALIBRATION_READY] Forge Neo A/B automation & external-tool integration`
- State: **ACTIVE / CALIBRATION_DESIGN**
- Branch: task branch from latest `main` for Issue #30 calibration work
- Previous DEV: #43 `[NAMING][COMPLETED] Finalize Special Core Dictionary naming and freeze handoff`
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #44で確定した3 evaluator coverageを受け取り、Stage10本番A/Bの前に、代表Special Core Entryを使った実画像キャリブレーションを再現可能な形で設計・実施する。

Current representative design is 32 cases × 4 images = planned 128 images. All planned images are screened first by WD14 / Kagami-24k / CL Tagger v2.00. Human review is concentrated on protected-route anchors, evaluator exceptions and a small stratified AUTO-likely sample.

`AUTO_CANDIDATE` は自動採点承認ではない。

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

1. latest `main` から Issue #30 用task branchを使用する。
2. approved representative manifestを保持し、controlled real-image calibrationを実施可能にする。
3. easyだけでなく、simple unary / rare-tail / multiple Specials / person relationship / subject-object / body-part / quantity / spatial / insertion-contact-restraint / compound / component-only / disagreement / AUTO control / REVIEW boundary / BLOCKED controlを含める。
4. machine-readable result schemaとgeneration provenanceを保持する。
5. Human referenceと WD14 / Kagami / CL v2.00 raw outputを比較する。
6. evaluator-alone / OR / AND / majority / CL-primary + support / disagreement-to-human / limited component proxyを比較する。
7. precision / false-positive suppressionをautomation率より優先する。
8. Stage10 production A/Bへ進める明示Gateを定義する。
9. 必要性が実証された場合のみ最小限の補助scriptを追加する。

## Result schema minimum

各画像について最低限:
- case_id / Special ID / canonical
- model / checkpoint / model version
- Prompt / Negative Prompt / Seed
- sampler / steps / CFG / resolution
- LoRA state + weight
- generated image path/hash
- human reference verdict + judgment dimensions
- WD14 / Kagami / CL raw scores and tags
- evaluator correctness/agreement/disagreement
- relation/binding required flag
- final calibration verdict

## Evaluation rules

- Human image-level judgment is the reference; Tagger vocabulary is not semantic authority.
- Direct vocabulary match does not prove relation/binding correctness.
- `AUTO_CANDIDATE` = calibration candidate only, not auto-score approval.
- subject/object, actor assignment, body-site ownership, count, spatial topology, insertion/contact/restraint, compound retentionは原則human review側。
- evaluator disagreement / weak rare-tail / component-only proxyはhuman reviewへ戻せる設計にする。
- one experiment = one question.
- fixed seed / actual Prompt / metadata traceabilityを保持する。
- false positiveを増やしてまでautomation率を上げない。

## UI-JA concurrency note

UI-JA current execution route is **Issue #36 V5 ChatGPT-led 31-shard repair/audit** on `ui-ja/issue36-relaxed-v5-chatgpt-repair`.
Historical Issue #46 Codex orchestration is superseded and does not replace or alter this #30 core DEV contract.

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
- representative case list + rationale exists
- execution procedure exists
- evaluator comparison strategy exists
- provisional AUTO / HUMAN REVIEW / BLOCKED rules exist
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
4. stale branch/mirrorを見ている場合は更新し、なお不一致ならSTOPして報告する。

Issue本文・CURRENT_STATE・CURRENT_DEV_TASKが一致して初めて #30 calibration workを継続する。
