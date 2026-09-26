# Issue #180 Parallel Codex Worktree Execution v1\n\n> Historical only. New execution must use `PARALLEL_EXECUTION_V2.md`.

Status: **SUPERSEDED by PARALLEL_EXECUTION_V2**  
Canonical research branch: `research/issue180-single-home-pilot`  
Target: `Character -> HOME_COPYRIGHT (0..1)`

This changes scheduling, ownership and QA only. It does **not** change the accepted HOME semantics, evidence bar, migration reconciliation, Issue #179 boundary, or the current v3 resolver.

## 0. Legacy single-Worktree freeze

The previous single-Worktree Codex run is retired as an execution path. Its GitHub-backed research/data checkpoint through `3004402b39e48f900ce17cb5d511dc3975f0003c` is preserved and must not be redone.

If the old Codex session becomes usable again, it may perform **salvage only** for any local-only delta that was never pushed; it must not continue Research Unit processing. Follow `docs/issue180/parallel/LEGACY_SINGLE_WORKTREE_HANDOFF_V1.md`.

After salvage accounting, all remaining work comes only from a freshly rebuilt current parallel assignment manifest. Historical OPEN counts are not work queues.

## 1. Why five Worktrees

Use **5 Worktrees total**:

- Forward 0 — `research/issue180-forward-0`
- Forward 1 — `research/issue180-forward-1`
- Forward 2 — `research/issue180-forward-2`
- Forward 3 — `research/issue180-forward-3`
- QA / Integrator — `research/issue180-qa-integrator`

Four forward lanes are enough to parallelize web/authority research without creating a coordinator swarm. The fifth Worktree is the only canonical writer and independently checks/repairs forward output.

Do not add a sixth coordinator. QA/Integrator owns coordination, integration and routine repair.

## 2. Bucket ownership

Forward-sharded buckets:
- `FAMILY_ROSTER_HIGH_YIELD`
- `VARIANT_BASE_READY`
- `DIRECT_AUTHORITY_RESEARCH`
- `AMBIGUOUS_LOW_YIELD`

QA-owned, full-review buckets:
- `SAFE_STRUCTURE_READY`
- `POLICY_BLOCKED`
- `IDENTITY_BLOCKED`
- `STRUCTURAL_NO_SAFE_PATH`
- `CONFLICT_REVIEW`

The QA-owned buckets are intentionally not sent through four web-research lanes. They are deterministic reconciliation, protected-policy, #179-boundary, no-safe-path, or conflict work.

## 3. Stable ownership and graph rebuilds

Run:

```
python scripts/issue180/run_issue180_v3.py
python scripts/issue180/build_parallel_assignment_v1.py
```

The generated `artifacts/issue180-v3/parallel_assignments_v1.csv` is the current ownership manifest.

Ownership rules:
- family/base/discovery subjects retain one stable `ownership_key`;
- ungrouped direct work is split to `direct:<canonical_tag>` so one giant long-tail unit cannot monopolize a lane;
- Forward owner = SHA-256(ownership_key) modulo 4;
- QA buckets always belong to QA;
- assignments are bound to the exact Research Unit fingerprint and canonical base SHA.

When evidence changes the graph, rebuild v3 and the assignment manifest. A proposal against a stale unit/member fingerprint is rejected unless it already appears in the QA review ledger. Old units are superseded; they are never silently reinterpreted.

## 4. Single canonical writer

Forward Worktrees **never** edit:
- `docs/issue180/evidence/*.csv`
- `docs/issue180/autonomous/decisions/*.csv`
- `docs/issue180/v3/research_unit_terminal_reviews_v3.csv`
- v3 scripts/resolver/policy
- canonical branch directly

Forward writes are append-only proposal files under exactly:
`docs/issue180/parallel/proposals/fwd-N/*.json`

Only QA/Integrator may turn accepted proposals into canonical evidence/decision/terminal-review rows and advance `research/issue180-single-home-pilot`.

This removes row-level push contention: no two forward lanes ever edit the same evidence/decision row.

## 5. Proposal contract

Machine/field contract: `docs/issue180/parallel/PROPOSAL_SCHEMA_V1.md`.

Each proposal carries:
- proposal_id
- assignment_id / epoch_id
- canonical_base_sha
- unit_id
- source_member_ids_sha256
- assignment_member_ids_sha256
- ownership_key / work_bucket / worker_slot
- proposal_type
- checked source URL and exact claim when evidence is proposed
- payload with the proposed relation or terminal review

Allowed types:
`EVIDENCE_DIRECT_HOME`, `EVIDENCE_FAMILY_HOME`, `EVIDENCE_MEMBER_OF`, `EVIDENCE_VARIANT_OF`,
`TERMINAL_REVIEW`, `SUPERSESSION`, `TECHNICAL_ESCALATION`.

Proposal files are not authority. Canonical evidence exists only after QA acceptance and integration.

## 6. QA cadence and independent review

An integration epoch should run after either:
- 50 new proposals, or
- 250 affected members,
whichever comes first. QA may integrate sooner when a worker finishes a coherent authority batch.

**100% review:**
- every proposed HOME-changing evidence fact;
- every new source-level family/root authority;
- every conflict;
- every migration correction/regression;
- every POLICY_BLOCKED / IDENTITY_BLOCKED / STRUCTURAL_NO_SAFE_PATH terminalization;
- every supersession/fingerprint transition;
- every manually curated or mixed-source mapping.

**Sampled second review is allowed only for deterministic bulk roster extraction after the source itself and mapping rule pass 100% review.**
Sample 10%, minimum 10 and maximum 50 members per source/batch. Any sampled mismatch escalates that whole source/batch to 100% row review.

Low-yield `NO_SAFE_EVIDENCE` proposals are safe-unresolved outcomes rather than positive HOME claims; QA reviews the research protocol and a stratified 10% of such units, but all P1/P2 or multi-member terminal units are checked individually.

Machine validation is always 100% regardless of semantic sampling.

## 7. Git and push protocol

Forward:
1. fetch/prune;
2. merge the current canonical research branch into the worker branch when it advances;
3. CI and the assignment builder both fail closed unless the latest canonical HEAD is an ancestor of the worker HEAD;
4. rebuild v3 + assignments;
5. work only assignments owned by the current slot;
6. commit proposal files in coarse batches;
7. push only the worker branch.

Do not rebase a published worker branch if that would require force-push.

QA/Integrator:
1. fetch/prune canonical + all four workers;
2. merge canonical into QA branch if canonical advanced;
3. read new worker proposal commits directly from GitHub/git; the user is not a relay;
4. independently review and integrate accepted facts into existing canonical ledgers;
5. append QA decisions to `QA_REVIEW_LEDGER_V1.csv`;
6. rerun full v3, assignments, tests and guards;
7. push QA branch;
8. require QA-branch CI green;
9. fast-forward push the exact green QA HEAD to `research/issue180-single-home-pilot`;
10. never force push.

If canonical advanced concurrently, fetch it, merge it into QA, rerun validation, and try the fast-forward again.

## 8. CI/self-repair

Forward CI is deliberately lightweight. It validates research scope, latest-canonical ancestry, branch-specific write scope, deterministic lane ownership, proposal schema, and protected-source boundaries. It does **not** rerun the full 35,890-Character v3 resolver on every proposal push.

Forward workers rebuild v3 + assignments locally when canonical advances or before selecting new work. QA rechecks proposals against a freshly rebuilt full assignment manifest before canonical integration.

Full v3 tests/resolver/reproducibility/#179 freshness run only on QA/Integrator and canonical branch checkpoints. This preserves the accuracy gate while removing four redundant full-pipeline CI runs per proposal wave.

A worker fixes its own proposal/schema mistake autonomously. It does not edit shared harness code.

QA owns technical harness repair. For a technical CI failure:
- inspect the exact failure;
- make the smallest repair;
- run focused + full v3 regression;
- document the repair;
- continue without asking the user.

A transient Actions failure may be rerun. A semantic failure is not “fixed” by weakening a validator.

## 9. True blockers only

Return to the user before final completion only when one of these is required:
- redefine canonical HOME semantics;
- mutate accepted Issue #70 source;
- mutate #179/#132 source/data;
- main merge or production apply;
- choose between genuinely competing roots when current policy cannot safely represent unresolved;
- unexplained loss/corruption of accepted evidence/provenance.

Ordinary missing evidence, inaccessible pages, stale unit fingerprints, routine supersession, routine CI repair, and safe unresolved terminalization are not user blockers.

## 10. Legacy cleanup discipline

The active v3 runtime remains the six scripts listed in `docs/issue180/v3/README.md`. Old v1/v2 and per-batch scripts stay tracked as provenance/history but are not active execution dependencies.

Do not create new `apply_batch_XX.py`, `review_batch_XX.py`, or one-off shard scripts. Parallel work is data/proposal driven through this scheduler. This is the main simplification over the old automation-era accumulation.

## 11. Final gate

Finish only when:
- OPEN/PENDING Research Units = 0;
- every unresolved Character has a concrete reason;
- all migration rows are accounted;
- conflicts/missing roots are safe;
- #179 handoff blob freshness passes;
- full v3 CI is green on canonical;
- protected sources/main/production remain untouched.

After internal QA completion, return once for independent ChatGPT final audit. Do not merge main or production-apply.
