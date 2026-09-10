# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: #49 `[DICT-PROMOTION][DEV] Apply audited Issue #32 fixes to production`
- State: open / current DEV
- Branch: `codex/issue49-dict-promotion`
- Start base: latest `main` (`origin/main` at branch creation)
- Activation: `AUTHORIZED_TO_SYNC_AND_START_ISSUE49` (Issue #49 comment `5611412073`)
- Audit authority: Issue #48 final verdict `APPROVE_WITH_REQUIRED_PROMOTION_CONTRACT` (comment `5605993533`)
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読めるようにする同期ミラー。

## Purpose and source authority

Issue #32 quarantineで独立監査済みのproduction-safe effective FIX subsetだけを、current mainのproduction profileへ適用する。

Read-only source authority:

- `dict-validation/quarantine`
- `validation_quarantine/PROMOTION_READINESS_PACKAGE_20260910.md`
- `validation_quarantine/CANDIDATE_FIX_CROSS_CONSISTENCY_R2_20260910.md`
- `validation_quarantine/candidate_fixes.csv`
- `validation_quarantine/candidate_fix_blocks/**`
- Issue #48 final audit contract

Quarantineはproduction baseにしない。production implementationはlatest mainから開始する。

## Required promotion contract

1. Special 2,788件のexact identity set、row count、fixed orderを完全維持する。
2. `candidate_fixes.csv` + `candidate_fix_blocks/**` から deterministic machine-readable effective-candidate manifestを作成する。
3. effective active candidateだけを採用し、`WITHDRAWN_AFTER_SIBLING_CHECK`、superseded、history-only、non-effectiveを除外する。
4. 同一 `(special_id, field)` にconflicting effective assignmentがあれば、書き込み前にSTOPする。
5. Special単位で承認field setをgroup化し、各Specialの適用をatomicに扱う。
6. candidateで明示されたfieldだけを変更し、sibling/adjacent fixを推測しない。
7. REVIEW 305 / Special IMAGE_TEST_REQUIRED 17を昇格しない。
8. semantic-supportのparked IMAGE_TEST_REQUIRED 33件のdefault/additive behaviorを変更しない。
9. WAI17 / Illustrious / NoobAI / Anima等のmodel-scoped claimをglobal truthへ平坦化しない。
10. rejected completeness 5件（`cervix_removal`, `fallopian_tubes_removal`, `ovaries_removal`, `uterus_removal`, `spread_eagle`）を追加しない。
11. canonical / Alias / Japanese / search / ranking / Prompt composer / #36 Japanese overlayを変更しない。
12. Stage10 production A/Bを開始しない。

## Allowed production scope

Primary and intended production target is:

- `data/generation/special2788_generation_profile.csv`

Any other `data/**` modification is forbidden unless it is an existing strictly derived integrity/manifest artifact required by project machinery and is explicitly justified in the report.

## Mandatory pre-write gates

Before any production write, record and verify:

- production profile current SHA-256 and Git blob;
- 2,788 unique identities and fixed order;
- source candidate file/blob hashes;
- active candidate row count and affected Special count;
- zero conflicting effective `(special_id, field)` assignments;
- every target `special_id` exists exactly once;
- before hashes/manifests for protected files touched or integrity-coupled.

If any gate fails, stop without partial write.

## Post-write gates

- rows = 2,788;
- identity/order unchanged;
- every effective candidate applied exactly once;
- excluded candidate/status not applied;
- non-candidate field changes = 0;
- rejected five not added;
- semantic data unchanged;
- all changed cells trace to candidate evidence;
- required tests/integrity checks and `git diff --check` pass;
- production data diff scope explicitly reported.

## Durable outputs

Commit these reviewable outputs on the feature branch:

- effective-candidate manifest;
- exact applied-diff report;
- implementation/completion report;
- test results;
- protected-data integrity evidence;
- rollback/reversion instructions.

Do not copy protected raw datasets into GitHub.

## Stop point and verdict

After implementation and push, stop. Do not merge main, start Stage10 A/B, promote #36, or declare production promotion complete. A separate post-write independent audit is mandatory before merge.

The handoff verdict must be exactly one of:

- `READY_FOR_POST_WRITE_AUDIT`
- `HOLD_PROMOTION_IMPLEMENTATION`

## Codex Gate

Issue #49 / `CURRENT_STATE.md` / this file are synchronized. Codex may implement only Issue #49 audited generation-profile promotion on `codex/issue49-dict-promotion`.
