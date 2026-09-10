# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][TEMP][DESIGN_READY] Forge Neo evaluator calibration & A/B automation`
- State: **ACTIVE / CALIBRATION_DESIGN_READY / CONTROLLED_EXECUTION_NOT_YET_STARTED**
- Branch: `codex/issue30-calibration-design`
- Previous DEV: #43 `[NAMING][COMPLETED] Finalize Special Core Dictionary naming and freeze handoff`
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #44で確定した3 evaluator coverageを受け取り、Stage10本番A/Bの前に、代表Special Core Entryを使った実画像キャリブレーションを再現可能な形で設計・実施する。

Calibration design is now materially complete and reviewable. Current representative design is **32 cases × 4 images = planned 128 images**. All planned images are screened first by WD14 / Kagami-24k / CL Tagger v2.00. Human review is concentrated on protected-route anchors, evaluator exceptions and a stratified AUTO-likely sample.

The controlled 128-image execution has **not started** merely because the design exists. Execute only after explicit authorization under Issue #30.

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

## Current design artifacts

- `docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_DESIGN_20260910.md`
- `docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_CASES_20260910.csv`
- `docs/testing/ISSUE30_REAL_IMAGE_CALIBRATION_RESULT_SCHEMA_20260910.json`

## Next work

1. Review/accept the completed calibration design if not already explicitly accepted.
2. Only after explicit authorization, execute the controlled 32-case / 128-image calibration.
3. Compare human image-level reference with WD14 / Kagami / CL v2.00 raw outputs.
4. Compare evaluator-alone / OR / AND / majority / CL-primary + support / disagreement-to-human / limited component proxy strategies.
5. Prioritize precision and false-positive suppression over automation rate.
6. Calibrate provisional `AUTO / HUMAN REVIEW / BLOCKED` routing.
7. Define only evidence-supported candidate `A_WIN / B_WIN` behavior.
8. Hand final operational constraints/results to #42 / #5 / `STAGE_10_PREP.md`.

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
Historical Issue #46 Codex orchestration is **superseded / closed** and does not replace or alter this #30 core DEV contract.

## Hard prohibitions

- Stage10 production A/Bを開始しない
- explicit authorization前にcontrolled 128-image calibrationを開始しない
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

Issue #30 is not complete at design-ready state. Completion requires the authorized controlled calibration to return reviewable evidence and a final capability-aware routing result suitable for #42/#5 handoff, or an explicit HOLD/BLOCKED disposition.

## Start / continuation Gate

Codexは作業継続前に必ず:
1. latest `main` を取得する。
2. `docs/project/CURRENT_STATE.md` が Current Core DEV = **#30** であることを確認する。
3. このファイルの Source Issue = **#30** と Issue #30 本文のscope/stateが一致することを確認する。
4. stale branch/mirrorを見ている場合は更新し、なお不一致ならSTOPして報告する。

Issue本文・CURRENT_STATE・CURRENT_DEV_TASKが一致して初めて #30 calibration workを継続する。
