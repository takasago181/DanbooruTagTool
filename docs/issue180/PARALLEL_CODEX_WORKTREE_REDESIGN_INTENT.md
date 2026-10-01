# Issue #180 — Parallel Codex Worktree Redesign Intent

Status: **SUPERSEDED — ACTIVE V1 IS docs/issue180/parallel/PARALLEL_EXECUTION_V1.md**

Repository: `takasago181/DanbooruTagTool`
Research branch: `research/issue180-single-home-pilot`

## Purpose

The user wants Issue #180 to adopt the same broad operating idea now used for Issue #132:

- multiple independent Codex Worktrees / execution contexts;
- clear ownership boundaries so work can proceed in parallel;
- an independent QA / repair role rather than repeatedly handing intermediate batches back to the user;
- GitHub as the shared source of truth;
- as few user-mediated handoffs as practical.

This document records that intent so it is not lost between chats.

## Important: this intent has been implemented

This file is historical design intent. Do **not** execute from this file. The active contract is `docs/issue180/parallel/PARALLEL_EXECUTION_V1.md` plus `PARALLEL_EXECUTION_V1.json`, with branch-specific CI/write guards.

A new ChatGPT design chat must first inspect the live #180 branch, current Issue #180 body/comments, v3 pipeline, current evidence/decision ledgers, residual-unit model, CI/write-scope constraints, and the lessons from #132's Codex Worktree redesign.

That chat will decide the exact #180 model, including:

- number of forward/research roles;
- whether work is partitioned by research-unit buckets, deterministic shards, authority families, or another stable key;
- ownership rules that prevent two Worktrees from editing the same evidence/decision rows;
- whether a dedicated QA/REPAIR role is sufficient or additional integration/coordinator logic is required;
- QA epoch/cadence and what must receive full vs sampled independent review;
- safe GitHub persistence/rebase/fast-forward rules for parallel work;
- conflict/retry behavior;
- how residual units are rebuilt when evidence changes the graph;
- how existing baseline/migration/evidence work is preserved;
- completion/stop conditions;
- AGENTS.md / runbook / CI guard updates;
- final per-Worktree start prompts.

## Existing work must be preserved

The redesign must **not** restart Issue #180 from zero.

Preserve the current v3 evidence-driven HOME resolver and all valid accumulated work, including:

- target invariant: `Character -> HOME_COPYRIGHT (0..1)`;
- missing/wrong-safe policy: missing relation is preferable to a wrong relation;
- current evidence ledger and reviewed authority;
- v2->v3 migration reconciliation/provenance;
- current residual Research Unit model and closure-sweep work;
- existing first-party/curated evidence CSVs;
- Issue #179 boundary/handoff semantics;
- existing branch history and valid decisions.

Parallelization is a scheduling/execution improvement, not permission to loosen evidence quality or bulk-guess HOME relations.

## Safety

Until the redesign is explicitly activated:

- keep using the existing #180 research branch/protocol as current authority;
- no merge to main;
- no production apply;
- do not mutate accepted Issue #70 source;
- do not mutate Issue #179/#132 data;
- do not force-push;
- do not treat this intent document as authorization to create competing unsynchronized ledgers.

## Desired user experience

The eventual design should aim for a workflow similar in spirit to #132:

1. the user starts a small fixed number of Codex Worktree chats once;
2. the Codex roles continue research/QA/repair autonomously under GitHub-backed rules;
3. normal batch completion, routine ambiguity, or routine repair does not require user relay;
4. only a true policy/specification blocker returns early;
5. after all #180 research and internal QA are complete, return once for final independent ChatGPT review.

The dedicated design audit selected **5 Worktrees total: 4 Forward + 1 QA/Integrator**. Exact ownership, QA cadence, push protocol and start prompts are frozen in the active parallel contract.
