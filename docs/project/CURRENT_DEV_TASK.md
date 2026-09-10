# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: #49 `[DICT-PROMOTION][DEV] Apply audited Issue #32 fixes to production`
- Parent / source lane: #32 dictionary validation + #48 independent promotion audit
- State: active
- Production base: latest `main`
- Implementation branch: dedicated Issue #49 feature branch created from latest `main`
- Purpose: Codexが現行DEV task contractをrepository内から読めるようにする同期ミラー。詳細・結果証拠はIssue #49を正本とする。

## Purpose

Issue #32 quarantine validationとIssue #48 independent auditでproduction-safeと承認されたeffective FIX subsetだけを、current productionのSpecial generation profileへ反映する。

Quarantineはread-only evidenceとして扱い、production implementationのbaseには使わない。

## Source authority

- Issue #32 quarantine results
- branch `dict-validation/quarantine`
- Issue #48 final verdict comment `5605993533`
- `validation_quarantine/PROMOTION_READINESS_PACKAGE_20260910.md`
- `validation_quarantine/CANDIDATE_FIX_CROSS_CONSISTENCY_R2_20260910.md`
- `validation_quarantine/candidate_fixes.csv`
- `validation_quarantine/candidate_fix_blocks/**`

## Start gate

実装前に必ず:

1. `docs/project/CURRENT_STATE.md` のcurrent DEVが #49 であることを確認する。
2. このファイルが Source Issue #49 / State active であることを確認する。
3. Issue #49本文と最新checkpointを読む。
4. latest `main` から専用feature branchを作る。`dict-validation/quarantine` をproduction baseにしない。
5. 不一致があればSTOPし、管理同期を先に直す。

## Required promotion contract

1. Special identity set / row count / orderingを正確に維持する: 2,788 entries。
2. `candidate_fixes.csv` + `candidate_fix_blocks/**` からdeterministic machine-readable effective-candidate manifestを作る。
3. `WITHDRAWN_AFTER_SIBLING_CHECK`、superseded、history-only、non-effective rowsを除外する。
4. 同一 `(special_id, field)` に conflicting effective assignments があれば書き込み前にSTOPする。
5. Special単位でapproved field setをatomicに適用する。
6. effective candidateで明示されたfield以外は変更しない。sibling/adjacent fixを推測しない。
7. REVIEW / IMAGE_TEST_REQUIRED outcomesをproductionへ昇格しない。
8. semantic-support parked 33 IMAGE_TEST_REQUIRED rowsのdefault/additive behaviorを変更しない。
9. WAI17 / Illustrious / NoobAI / Anima等のmodel-scoped generation claimsをglobal truthへ平坦化しない。
10. rejected completeness 5件を追加しない: `cervix_removal`, `fallopian_tubes_removal`, `ovaries_removal`, `uterus_removal`, `spread_eagle`。
11. canonical / Alias / Japanese / search / ranking / Prompt composerを変更しない。
12. Stage10 production A/Bを開始しない。

## Allowed production diff scope

Primary intended target:

- `data/generation/special2788_generation_profile.csv`

追加の `data/**` 変更は禁止。ただし既存project machineryで必須なstrictly-derived integrity/manifest artifactだけは例外になり得る。その場合はcompletion reportでpath・理由・generated-from関係を明示し、scopeを黙って広げない。

## Pre-write machine gates

production write前に必ず:

- input production profileがcurrent approved production baseに対応することを確認
- 2,788 unique Special identities / fixed order確認
- effective-candidate manifest作成
- active candidate row count / unique affected Special countを記録
- conflicting effective `(special_id, field)` assignments = 0
- target `special_id` がexactly once存在
- touched / integrity-coupled protected filesのpre-write SHA-256 / manifest記録

1つでも失敗したらpartial writeせずSTOP。

## Post-write checks

- exact profile row count = 2,788
- identity / order unchanged
- each effective candidate applied exactly once
- excluded / withdrawn candidate applied = 0
- non-candidate field changes = 0
- rejected completeness candidates added = 0
- semantic-support data unchanged（通常）
- required tests / integrity checks実行
- `git diff --check` PASS
- before/afterの全変更セルをeffective candidate rowへtraceできるdiff report作成
- protected-data integrity evidence記録

## Required durable outputs

feature branchへcommit:

- machine-readable effective-candidate manifest
- exact applied-diff report
- implementation/completion report
- test results
- protected-data integrity evidence
- rollback/reversion instructions

protected raw datasets自体はGitHubへコピーしない。

## Stop point / acceptance verdict

実装・test・push後にSTOPする。mainへmergeしない。Stage10 A/Bを開始しない。production promotion completeを宣言しない。

別のpost-write independent auditが必須。

DEV handoff verdictはexactly one:

- `READY_FOR_POST_WRITE_AUDIT`
- `HOLD_PROMOTION_IMPLEMENTATION`

## Forbidden

- #36 Japanese overlay production promotion
- canonical / Alias / Japanese/search/ranking/Prompt changes
- REVIEW / IMAGE_TEST_REQUIREDの数合わせ昇格
- protected integrity weakening
- alternate snapshot substitution
- `git clean` によるprotected data cleanup
- main merge
- Stage10 production A/B

## Codex Gate

Issue #35はcompleted / closed。current DEVは **Issue #49**。

CodexはIssue #49 contractの範囲だけを実装し、`READY_FOR_POST_WRITE_AUDIT` または `HOLD_PROMOTION_IMPLEMENTATION` で停止する。
