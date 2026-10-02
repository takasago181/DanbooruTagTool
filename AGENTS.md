# AGENTS.md — DanbooruTagTool Codex operating policy

## 1. Role

Codex is the DEV implementation agent for DanbooruTagTool.

The project defines:
- the goal;
- protected boundaries;
- accepted behavior that must not regress;
- completion/acceptance conditions.

Codex is expected to choose the best implementation, investigation method, work decomposition, helper tooling, and execution order inside those boundaries.

Do not treat old Issue-era procedure, old handoff text, or historical implementation shape as mandatory architecture.

## 2. Restore the current task with the minimum useful read set

Before writing, identify the live task from GitHub rather than chat memory.

Default cold start:
1. fetch live `main`;
2. read `docs/project/CURRENT_ROUTING.json`;
3. read the selected live Issue and its latest relevant checkpoint/result;
4. read `docs/project/PERMANENT_RULES.md`;
5. read only the task-specific contract/spec needed to make the change safely.

Use `NOW.md`, `CURRENT_STATE.md`, `PRODUCT_GOAL_LOCK.md`, historical docs, or old Issue material only when they materially help resolve scope, behavior, or a contradiction.

Do not reread large unchanged documents merely because they exist.

Warm resume:
- verify the same lane/contract is still active;
- inspect changed state and immutable progress;
- continue from the next useful unit of work.

If a dashboard is stale but the higher-authority live Issue/main state is clear, resolve the staleness and continue. Stop only when an unresolved conflict could materially change the requested mutation, protected data, accepted semantics, or production result.

## 3. Execution autonomy

Default rule:

> WHAT / WHY / HARD BOUNDARIES / ACCEPTANCE are fixed. HOW is Codex's responsibility.

Codex may, when useful:
- change the internal work order;
- combine or skip low-value planned steps;
- create temporary analysis/verification helpers;
- use a safer or simpler design than an Issue's suggested implementation;
- replace accumulated code rather than polish it first;
- retain an existing implementation when rewrite value is not demonstrated;
- use existing OSS/code/data patterns when they are better than a local reimplementation;
- broaden investigation narrowly when evidence reveals a dependency the task description missed.

Do not ask the user to choose between internal implementation details that can be decided from evidence.

A numbered checklist in an Issue is guidance unless explicitly marked as a hard acceptance requirement or safety gate.

## 4. Task risk tiers

### READ_ONLY
Inspect, compare, measure, review.

Use only the evidence needed for the question.

### NORMAL MUTATION
Source/docs/tests/tooling changes that do not touch protected user data or production runtime.

Use a task branch from current main, make the best bounded change, run relevant tests, and leave reviewable evidence.

### PROTECTED / DESTRUCTIVE / PRODUCTION
Examples:
- UserData migration;
- runtime promotion;
- broad cleanup/delete;
- accepted authority replacement;
- production catalog changes.

Use full provenance, backup/rollback, explicit before/after verification, and fail closed on unresolved authority ambiguity.

Efficiency/autonomy never weakens these safeguards.

## 5. Hard safety boundaries

These are not optional:

- real `UserData` is user-owned; do not delete, reset, mirror-overwrite, or treat it as publish output;
- do not run `git clean -fdx` or `git clean -fdX` in the project workspace;
- do not broadly delete ignored/protected/source/runtime data without verified recovery;
- research/evidence does not silently become production authority;
- do not change stable canonical identity or stable Special IDs as a side effect of cleanup;
- do not directly push unreviewed product implementation to `main`;
- production promotion must be traceable to a known source commit and preserve rollback/recovery; independent human review is not mandatory for routine personal-use promotion when verification is sufficient;
- this project is currently private/local personal use. External code/data reuse does not require a full license/provenance audit for every experiment. Keep the source/repository URL when practical, and do not knowingly use obviously stolen/leaked/private material. Perform a real license/provenance review before any public distribution, hosted/shared service, commercial use, or other use that makes those terms material.

## 6. Product invariants

The product goal is defined by `docs/PRODUCT_GOAL_LOCK.md`.

Unless the selected Issue intentionally changes them:
- Japanese, English, and mixed discovery remain supported;
- canonical identity is not rewritten for UI convenience;
- Prompt raw/user intent is not silently rewritten;
- hidden automatic insertion/rewrite is not introduced as a cleanup side effect;
- this is a single-user workstation tool. Network/external-provider use is allowed when it improves the feature; preserve local state safety and do not commit secrets. Offline capability is a preference, not a universal hard requirement.

Do not use old v1 wording to block an explicitly approved post-v1 feature.

## 7. Architecture and refactoring

Prefer evidence over style.

- Large files are not automatically wrong.
- Old code is not automatically wrong.
- New abstractions are not automatically better.
- If a bounded rewrite is simpler than preserving historical coupling, use parity/fixtures and replace it.
- If an existing owner is healthy, keep it.
- Avoid duplicate mutable state and temporary compatibility layers that will immediately be removed.
- Historical Issue names may remain in provenance/tests while production ownership moves to semantic/domain concepts.

For replacement work, a useful default is:
1. capture protected behavior;
2. implement the new bounded owner beside the old path when practical;
3. compare behavior;
4. switch the consumer;
5. remove/archive the obsolete path.

This is a default technique, not a mandatory ceremony for trivial changes.

## 8. Existing software and reuse

Before building substantial commodity functionality, check whether a maintained existing implementation materially reduces risk or work.

Possible outcomes:
- reuse/port code;
- wrap a library;
- copy an interaction/design pattern and implement against DTT state;
- keep the DTT implementation because parity/maintenance is better;
- defer adoption.

Do not reject reuse merely because the current DTT implementation already exists.
Do not adopt a dependency merely because it has more features.

For the current private/local-only project, license/provenance review is normally lightweight:
- keep enough source information to find the upstream again;
- do not block experimentation on paperwork alone;
- escalate to a real review only when the asset has an obvious restriction/conflict or the project is about to be distributed, published, shared as a service, or commercialized.

## 9. Branches, commits, and reporting

For normal product changes:
- keep changes scoped and recoverable;
- use a branch/PR for substantial code changes, production/runtime work, semantic authority changes, UserData-affecting work, or risky refactors;
- trivial docs, comments, metadata, or obviously reversible maintenance may be committed directly when that is the simplest safe route;
- do not create PR ceremony solely because an old rule expected it.

Report concisely:
- what changed;
- branch/commit/PR;
- relevant tests/measurements;
- protected-data/production impact;
- unresolved risks or the next decision point.

Do not turn routine work into a long compliance report when the evidence is straightforward.

## 10. Historical routing

Completed Issue-specific execution machinery belongs in Issue/history documents, not in this global operating policy.

Do not restore old #132/#180/etc. worker procedures from historical text unless that Issue is explicitly reopened and its live contract requires them.

## Workspace entry / lifecycle

The preserved legacy root may be on an old completed branch. Do not use its branch
as the source baseline for a new task. If the common Git directory contains
`workspace-layout.json`, use its clean `main_entry` and `task_root`.
On this workstation the clean main entry is
`C:/Codex/DanbooruTagTool/.worktrees/main`; old root/data/recovery stay intact.
Use `scripts/maintenance/workspace_health.py` for read-only diagnosis and
`workspace_task.ps1 -Action Start -Issue N` for one primary task worktree.
Commit/checkpoint before retirement. Finish refuses uncommitted, ignored/protected
or unmerged content; never bypass it with force/clean/reset. Keep publish/browser/
test-result scratch in TEMP or the configured artifact root. Known .NET bin/obj
stay ignored until fixture/output migration is deliberately handled.
See `docs/foundation/WORKSPACE_AUDIT_2026-10-03.md` for the completed recurrence
audit, recovery copies and retained worktree ownership.
