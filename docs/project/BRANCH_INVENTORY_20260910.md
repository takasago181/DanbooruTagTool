# Branch Inventory — 2026-09-10

> **HISTORICAL SNAPSHOT — DO NOT USE FOR CURRENT ROUTING**
>
> このInventoryは2026-09-10時点の枝分類です。現在は #46 がsuperseded/closed、#36はV5、#30がcurrent core DEVであり、下記`KEEP_ACTIVE`分類には古い状態が含まれます。
> **現在のbranch用途は `docs/project/CURRENT_STATE.md`、live Issue、実際のremote branch状態を優先してください。**
>
> 2026-09-11 repository cleanup auditで、誤って現行branch表として使われないようhistorical扱いを明示しました。枝自体はこの作業では削除していません。

---

Purpose: reduce branch-name ambiguity without deleting audit/evidence history blindly.

Authority: `docs/project/CURRENT_STATE.md` and live Issues remain the routing source of truth. This file is an inventory, not a task contract.

## Classification rule

- `KEEP_ACTIVE`: current or near-term workstream branch, or an explicitly referenced live input branch.
- `KEEP_EVIDENCE`: completed/superseded branch still useful for audit, rollback, historical comparison, or explicitly referenced evidence.
- `SAFE_TO_DELETE_NOW`: only when branch is no longer active, contains no unique required evidence, and deletion cannot break current restore/audit references.

Conservative rule: uncertainty -> `KEEP_EVIDENCE`.

## KEEP_ACTIVE

- `main`
- `codex/issue46-orchestrator` — live #46 execution lane
- `ui-ja/issue36-final-agent-convergence` — live #36 frozen-contract/data lane
- `knowledge/generation-corpus` — live #44 persistent KNOWLEDGE lane
- `codex/issue30-automation-dry-run-20260908` — #30 preserved pipeline/evaluator baseline used by active Stage10 prep
- `ui-ja/japanese-overlay-quarantine` — keep while #36 UI-JA data convergence/promotion remains incomplete

## KEEP_EVIDENCE — completed core / Stage / audit

- `codex/issue6-preflight-check`
- `codex/issue28-e2e-verdict`
- `codex/issue43-special-core-dictionary`
- `codex/issue49-dict-promotion`
- `codex/issue49-dict-promotion-latest-main`
- `codex/stage9b-main-integration`
- `codex/stage9b-runtime-composer`
- `codex/stage9c9d-completion`
- `dict-validation/quarantine`

Notes:
- `codex/issue43-special-core-dictionary` HEAD `19e2650...` is an ancestor of current main, but Issue #43 and freeze records explicitly cite it; keep as evidence.
- `codex/issue49-dict-promotion-latest-main` HEAD `490f565...` is an ancestor of current main and is the audited production-promotion evidence anchor; keep.
- `codex/issue28-e2e-verdict` is an ancestor of main and remains a completed E2E evidence anchor; keep.
- `codex/stage9b-main-integration` is diverged relative to current main, so it is not safe to delete based only on “Stage9 completed”. Preserve as historical implementation evidence.

## KEEP_EVIDENCE — UI-JA historical / superseded

- `ui-ja/issue35-ui-only`
- `ui-ja/issue36-machine-convergence`
- `ui-ja/issue36-r3-bulk-canary`
- `ui-ja/issue41-pilot`
- `ui-ja/r3-test-engine`

These are not current routing branches. Preserve until #36/#46 final convergence and independent promotion are fully complete, because Issue history explicitly distinguishes failed/superseded pilot evidence from valid final evidence.

## KEEP_EVIDENCE — management / governance history

- `management/chat-start-protocol`
- `management/close-handoff-gaps`
- `management/codex-gh-issue-access`
- `management/current-dev-task-mirror`
- `management/current-state-issues`
- `management/final-governance-hardening`
- `management/proactive-chat-handoff`
- `management/setup`
- `management/stage9-final-audit-gate`
- `docs/organize-agent-rules-no-semantic-change`

Reason: several are diverged from current main and may contain historical governance evolution. Do not infer deletability from age/name alone.

## KEEP_EVIDENCE — Prompt / Stage10 research

- `docs/stage10-ab-automation-temp`
- `prompt/audit-knowledge-reservoir-20260909`
- `prompt/current-purpose-audit-20260909`

Keep until #42/#5/Stage10 handoff is complete, because these may be referenced as historical design/research inputs.

## SAFE_TO_DELETE_NOW

**None.**

No branch is being deleted in this pass.

Rationale:
- active branches obviously remain;
- multiple completed branches are explicit evidence anchors in Issues/docs;
- some old-looking branches are diverged from main, so deleting them without a per-branch evidence/reference audit would discard unique history;
- branch count alone is not sufficient reason to delete audit history.

## Cleanup policy going forward

When Stage10 preparation reaches another major freeze point, re-run this inventory and promote a branch to `SAFE_TO_DELETE_NOW` only if all are true:

1. owning Issue/workstream is completed or superseded;
2. branch is not named by current restore/checkpoint/audit contracts;
3. any unique required artifact is already on main or in another durable evidence branch;
4. compare-to-main is understood;
5. deletion does not remove rollback/reproduction evidence still needed by an open Issue.

This keeps the branch list manageable without trading away traceability.
