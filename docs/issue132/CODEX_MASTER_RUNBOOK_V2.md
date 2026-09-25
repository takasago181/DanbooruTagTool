# Issue #132 — Codex Master Runbook V2

Status: **HANDOFF READY / GUARDED CODEX EXECUTION / CHATGPT AUTOMATIONS PAUSED**

Repository: `takasago181/DanbooruTagTool`
Canonical branch: `research/taxonomy-usability-audit`

## Purpose

Finish Pass A with Codex as the bulk execution engine while preserving the manually repaired baseline, frozen taxonomy vocabulary, audit trail, and ChatGPT semantic QA ownership.

This changes the executor and QA controls, not the frozen taxonomy.

## Authority order

Every Codex session MUST recover live repository truth in this order:

1. `docs/issue132/parallel/RUNTIME_AUTHORITY.json`
2. this runbook
3. role-specific card named by live authority
4. current semantic guardrail policy named by live authority
5. `docs/issue132/parallel/CODEX_QA_STATE.json`
6. frozen machine-readable semantic vocabulary
7. current write-request protocol for forward Worker work
8. current repository files and CI results

Old Issue comments, old handoff status text, and chat history are not execution authority.

## Roles

Run four independent Codex roles/worktrees:

- CODEX-L1: Lane 1 forward semantic review only
- CODEX-L2: Lane 2 forward semantic review only
- CODEX-L3: Lane 3 forward semantic review only
- CODEX-REPAIR: invalid/hold windows, materializer/validator/CI defects, bounded targeted repair only

ChatGPT remains specification owner and semantic QA supervisor.

## Shared branch safety

- canonical publish target is only `research/taxonomy-usability-audit`;
- separate temporary worktree/branch per role;
- fetch/rebase canonical before publish;
- revalidate after rebase;
- fast-forward push only;
- no force push;
- no merge to main;
- no production apply;
- no Issue #132-external mutation.

Historical checkpoint/staging data remains immutable except existing append-only repair overlays.

## Current manually audited baseline

Accepted saved population through:
- Lane 1 = 1125
- Lane 2 = 1225
- Lane 3 = 1200

The manual audit already repaired:
- structural historical defects via append-only repair overlay;
- 216 clear semantic errors via correction/repair overlays.

Do not redo this baseline as ordinary forward work.

## Forward Worker loop

For L1/L2/L3:

1. Read live authority, Worker card, current semantic policy, QA state.
2. Resolve own frontier from staging + pending requests + deferred markers.
3. Enforce own lane QA watermark.
4. Enforce unresolved persistence-debt limit.
5. Read only required neutral shard(s).
6. Inspect every identity individually.
7. Reason in blocks up to 100.
8. Persist exact 25-slot V2 requests.
9. Validate locally.
10. Before publish re-read authority/policy/QA state.
11. Rebase current canonical, revalidate, fast-forward push.
12. Continue only while below QA and persistence-debt gates.

Do not stop merely because one 25-row slice succeeded.

## Semantic behavior

The frozen vocabulary plus current semantic guardrail policy are mandatory.

Do not:
- infer unclear identity meaning from spelling alone;
- bulk-classify from suffix/prefix/regex;
- default proper names to SEARCH_ORIENTED;
- extrapolate one researched sibling to unseen siblings;
- alter taxonomy vocabulary;
- treat adult/sexual identity as an error/risk by itself.

Use the guardrail research minimum for ambiguous Danbooru/reference/meme identities.

## First calibration

The first Codex batch is deliberately bounded to 100 new accepted rows per lane.

Codex stops each lane at:
- L1 1225
- L2 1325
- L3 1300

ChatGPT then performs full semantic QA of those 300 new rows.

Only after that QA passes does ChatGPT widen `CODEX_QA_STATE.json`.

This prevents a bad new Codex decision habit from multiplying across thousands of rows.

## Steady-state QA cadence

After calibration:
- a lane may advance at most 500 accepted rows beyond its last ChatGPT QA watermark;
- QA checks all risk rows, family consistency, and deterministic stratified ordinary CHECKED samples;
- a confirmed family defect freezes/repairs that family/range without discarding unrelated valid progress.

## Persistence-debt gate

Per lane, unresolved persistence debt is:
- pending request slots without canonical staging;
- plus deferred slots.

Maximum comes from live authority.

When the limit is reached, forward work stops for that lane until debt is reduced.

## Version trace

All new V2 requests record:
- semantic policy id;
- policy Git blob SHA;
- per-row decision reason codes.

Historical policy versions remain accepted if registered in authority.
A newer policy does not automatically invalidate older accepted rows; it creates targeted QA when the change is semantically relevant.

## CODEX-REPAIR

Priorities:
1. pipeline/CI/materializer defects that block valid forward work;
2. pending persistence debt;
3. invalid/hold historical windows;
4. bounded targeted semantic repair explicitly identified by ChatGPT QA.

Repair may not invent taxonomy policy or mass-reclassify valid rows from heuristics.

## Completion

Pass A is complete only when:
- accepted_total = 31,003;
- invalid windows = 0;
- holds = 0;
- missing identities/ranges = 0;
- duplicate coverage = 0;
- fatal contract errors = 0;
- pending materialization = 0;
- deferred ranges = 0;
- QA watermark violations = 0;
- ChatGPT final semantic QA has passed;
- no unresolved systematic semantic defect remains.

Then stop and return control to ChatGPT/user.
Do not build production changes, merge main, or production-apply without separate authorization.
