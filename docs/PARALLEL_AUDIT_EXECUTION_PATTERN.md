# Parallel audit execution pattern

Status: reusable research/engineering pattern. This note is intentionally generic so it can be reused by the dictionary lanes as well as Issue #180.

## Why the recent audit became much faster

The speedup did **not** come from lowering validation standards. It came from changing the shape of the work.

### 1. Wide independent reads instead of a long serial chain
Independent GitHub reads are issued together: workflow state, branch/main diff, Issue/PR state, scripts, policies, review CSVs, and artifact metadata. None of these needs the previous read to finish, so serializing them only adds latency.

### 2. Separate CPU/data work from asynchronous waiting
GitHub Actions is allowed to run independently. Do not repeatedly poll an in-progress run inside one assistant turn. While CI is running, perform independent audits/design/file checks. Check CI once at a synchronization point.

### 3. Deterministic scripts do the bulk census
Use Python/scripts for full-population counting, bucketing, conflict detection, and deterministic sample generation. Reserve semantic/manual review for the reduced ambiguous set.

### 4. Fail closed at every authority boundary
Fast bulk processing is safe only when uncertain rows become REVIEW/UNKNOWN instead of being guessed. A wrong accepted relation/tag classification is more expensive than leaving it unresolved.

### 5. Artifacts are the synchronization boundary
A CI artifact is treated as the result of one reproducible batch. Inspect/count from the artifact, freeze the result, then design the next batch. Do not mix half-finished CI state with semantic conclusions.

### 6. Parallelize breadth, serialize dependencies
Good parallel targets:
- branch/main diff
- workflow/run/job/artifact status
- independent source/policy files
- multiple review batches
- counts and distributions
- validation of unrelated authority families

Keep sequential:
- a write that depends on a just-produced artifact
- semantic approval that depends on evidence
- merge after validation
- production promotion after merge

### 7. Small synchronization points prevent unrecoverable stalls
A long chain such as write -> wait -> poll -> fetch logs -> rewrite -> wait -> poll is fragile. Prefer:
wide reads/work -> one write batch -> one CI check -> stop if still running.
A later turn can resume from GitHub because commits/artifacts are durable.

## Reuse for dictionary work

The same pattern should be used for large dictionary audits:

1. freeze accepted source and rules;
2. run deterministic full-dictionary census;
3. split rows into PASS / mechanical-fix candidate / semantic-review / unknown;
4. rank recurring defect patterns by affected-row count;
5. generate deterministic review batches across different semantic clusters;
6. review multiple independent clusters in parallel;
7. encode only confirmed reusable rules;
8. rerun full census and regression controls in CI;
9. preserve unresolved rows rather than guessing;
10. merge/promote only after artifact-backed validation.

For the Special Core Dictionary this means broad mechanical validation and cluster discovery can be highly parallel, while semantic meaning, generation usefulness, and sensitive core-tag distinctions remain evidence-gated.

## Operational guardrails

- GitHub remains the durable source of truth.
- No production mutation during research/audit.
- No old relation/classification is promoted merely because it is frequent.
- Counts must reconcile to the full population.
- Every automation rule needs regression controls.
- Parallelism is for independent work; it must not bypass evidence dependencies.
