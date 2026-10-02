# Project Execution Architecture

Purpose: let capable Codex/ChatGPT runs spend effort on the actual problem instead of reconstructing unchanged project ceremony.

## 1. Default contract

The project should normally specify:

- **WHAT** outcome is needed;
- **WHY** it matters;
- **HARD BOUNDARIES** that must not be crossed;
- **ACCEPTANCE** evidence that demonstrates success.

The model owns **HOW** unless the task genuinely requires a fixed procedure.

This includes:
- work decomposition;
- analysis method;
- helper scripts/tools;
- implementation order;
- refactor granularity;
- whether an existing subsystem should be kept, wrapped, rewritten, deleted, or archived;
- whether an existing OSS implementation is preferable to local code.

A planned checklist is not a quota.

## 2. Risk-based execution

### READ_ONLY
Examples: inspect, compare, audit, benchmark, review.

Use the minimum evidence necessary. Expand only when findings expose a dependency.

### APPEND_ONLY
Examples: immutable review/result ledgers.

Verify the target/contract, append the next useful bounded result, validate it, and avoid unrelated full-project preflight.

### NORMAL MUTATION
Examples: source/docs/tests/tooling changes.

Recover current task authority, change the bounded subsystem, run relevant regression/quality checks, and leave recoverable evidence. Use a branch/PR when the change is substantial or risky; do not require it for every trivial personal-repo edit.

### PROTECTED / DESTRUCTIVE / PRODUCTION
Examples: UserData migration, runtime promotion, accepted authority replacement, broad cleanup.

Use full provenance, backup/recovery, exact affected scope, rollback, and appropriate acceptance testing.

Autonomy and efficiency do not weaken this tier.

## 3. Cold vs warm state recovery

Cold start is for:
- a new session;
- changed lane/contract;
- uncertain branch/authority;
- material conflict.

Warm resume is for the same task/contract with recoverable progress.

Warm resume should inspect changed state and immutable progress, not reread large unchanged docs.

Use live GitHub and immutable evidence to resolve stale summaries. Fall back to broader reading only when the conflict matters.

## 4. Evidence model

Prefer:
- immutable result/checkpoint/manifest;
- current source/tests;
- reproducible benchmark;
- live Issue decision.

Treat status/progress summaries as derived convenience.

A stale cache/dashboard does not roll back validated work.

## 5. Large inputs

Do not make the model repeatedly read giant source/evidence files when a deterministic projection can preserve the task-relevant information.

Useful pattern:

`authority -> pinned hash/manifest -> compact bounded input -> work -> result -> targeted validation -> final parity/audit`

Compact inputs are transport/cache, not replacement authority.

The exact shard size, batch size, or QA cadence should be chosen from task complexity and measured failure risk rather than copied as a universal quota.

## 6. Quality strategy

Prefer risk-based validation:
- exact/deterministic checks for schema, hashes, IDs, counts, migration, persistence;
- semantic review where judgment is actually required;
- focused regression around changed boundaries;
- full regression when the change/risk justifies it;
- production smoke only when production/runtime behavior is involved.

Do not equate quality with repeated full rereads or duplicated test suites.

## 7. Refactoring/replacement

When historical structure is costly, Codex may recommend or perform a bounded replacement instead of incrementally beautifying the old code.

Use parity/strangler techniques when they reduce risk, especially for high-value production semantics.

Do not require a formal strangler sequence for tiny changes where direct replacement is obviously safer.

## 8. External reuse

Before implementing substantial commodity functionality, inspect maintained existing tools/libraries/data when reuse could materially improve the result.

Evaluate:
- fit to DTT's actual use case;
- behavior parity;
- maintenance/upstream risk;
- network/local-state implications;
- integration complexity.

For the current private/local-only project, do not turn license/provenance research into a default blocker. Record the upstream source when practical. Escalate to a real legal/provenance review only when there is an obvious restriction or before distribution/publication/shared-service/commercial use.

Possible result:
- adopt/port;
- wrap;
- imitate UX/architecture;
- use only as test/reference;
- reject and keep DTT.

The goal is not maximum dependency reuse; it is avoiding unnecessary reinvention.

## 9. Reporting and checkpoints

Record enough to resume/review:
- result;
- branch/commit/PR when changed;
- important tests/measurements;
- protected/production impact;
- unresolved decision.

Do not produce large repetitive compliance reports unless the task itself is an audit.

## 10. Anti-patterns

Avoid:
- fixed batch/row quotas without evidence;
- rereading unchanged full authority every run;
- stopping on harmless stale dashboard text;
- cleaning an implementation that is about to be replaced;
- introducing abstraction/frameworks for aesthetics;
- preserving Issue-era ownership only because tests are named after it;
- implementing future-feature architecture before the feature needs it;
- requiring the user to choose routine internal engineering decisions.


## 11. Single-user workstation assumption

Current default is a private, single-user Windows workstation tool, not a distributable desktop product.

Therefore these are **not universal acceptance gates**:
- launching on a second PC;
- portable folder-copy verification;
- self-contained or single-file packaging;
- zero DLL/PDB packaging shape;
- avoidance of machine-specific paths when a stable local path is simpler;
- offline operation for every feature;
- PR/reviewer ceremony for every small change.

Keep or use any of them when they materially improve the user's workflow or recovery, but do not block unrelated work merely to satisfy distribution-quality packaging.

What remains mandatory is practical safety on the actual workstation:
- current runtime can start and perform the changed workflow;
- UserData is preserved;
- source/runtime provenance is recoverable enough to roll back;
- destructive changes are bounded;
- regressions relevant to the change are tested.
