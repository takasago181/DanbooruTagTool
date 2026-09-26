# Issue #180 — Legacy Single-Worktree Handoff V1

Status: **ACTIVE TRANSITION FREEZE**

## Purpose

The previous single-Worktree Codex execution stopped because the user's Codex usage allowance was exhausted.

That legacy execution must **not resume ordinary Issue #180 research** when capacity becomes available again.

Its already completed work is preserved and becomes the starting evidence/state for the new five-Worktree parallel execution model.

## Preserved GitHub checkpoint

The last research/data commit immediately before the parallel redesign intent was introduced is:

`3004402b39e48f900ce17cb5d511dc3975f0003c`

The redesign-intent commit `fac7c558280c127c050e6a3ec9c75e2dbef89b15` is its direct child.

The earlier closure-sweep checkpoint `ad3eab21c303f209de62a0a51450ff9c45d385dd` is already an ancestor of `3004402b...`; there are 19 later GitHub-backed commits between them. Therefore the previously completed evidence/decision/terminal-review work is already incorporated into the preserved canonical history.

Do not restart Issue #180 from an earlier checkpoint and do not repeat resolved/terminalized work merely because the scheduling model changed.

## Recovery procedure for the old Codex session

When the old single-Worktree Codex becomes usable again, its only permitted task is **salvage of work that may exist locally but was never pushed**.

It must:

1. inspect `git status`, local HEAD, and local commits relative to GitHub;
2. perform **no new web research and no new Research Unit processing**;
3. preserve any existing uncommitted or unpushed work exactly as found;
4. if there is no local-only delta, report that no salvage is required and stop;
5. if there is a local-only delta, commit only that already-existing delta without extending the research;
6. push it to `research/issue180-legacy-salvage` by normal fast-forward if possible;
7. if that branch cannot accept the local history by fast-forward, push a uniquely named `research/issue180-legacy-salvage-<shortsha>` branch instead;
8. report branch/SHA/files/tests that already existed or were needed only to preserve the delta, then stop.

No force push is allowed.

The pre-created `research/issue180-legacy-salvage` branch points at `3004402b39e48f900ce17cb5d511dc3975f0003c`.

## QA ingestion of salvage

QA / Integrator is the only role allowed to consume a legacy salvage delta.

QA must:

- compare the salvage branch against current canonical state;
- identify only work that is genuinely absent from canonical;
- independently validate semantic changes under the current #180 policy;
- reject duplicate/stale work that is already represented by canonical evidence/decisions/terminal reviews;
- integrate accepted salvage once into the normal canonical ledgers;
- record the ingestion in `QA_REVIEW_LEDGER_V2.csv`;
- rebuild v3 and the v2 authority-campaign queue afterward.

Salvage is not an alternate authority and does not bypass normal QA.

## New execution boundary

After salvage accounting, all continued work is owned by the active five-Worktree model:

- four Forward proposal-only lanes;
- one QA / Integrator canonical writer.

The v2 authority-campaign queue is always rebuilt from the **current canonical residual graph**. Therefore already resolved or terminalized legacy work is naturally excluded from new assignments.

The legacy single-Worktree loop is retired. The old continuous-execution Issue comments remain historical context only where they conflict with this transition freeze.
