## CI execution lesson for dictionary audits

Issue #180 exposed an execution-pattern problem that should be reused by dictionary/taxonomy audits (especially #132).

### What was inefficient
A long audit was split into too many tiny cycles:
1. assistant writes one small change;
2. GitHub Actions runs and stops;
3. next user turn is needed to inspect it;
4. another small change is submitted;
5. CI starts again.

GitHub Actions does **not** autonomously continue the research after a workflow finishes. It only executes the workflow that was committed, then stops. Therefore excessive synchronization points translate directly into excessive user "continue" turns.

### Rule for future dictionary audits
Prefer one bounded pipeline per dependency stage:
- deterministic census
- shard/parallel independent review inputs
- apply already-collected evidence
- second-review gate
- full regression
- human-readable export
- artifact upload

Put these in the same CI run whenever there is no real human decision or external evidence dependency between them.

### Why this is faster
- fewer commit -> CI -> inspect round trips;
- fewer user turns used only as synchronization;
- GitHub Actions spends more of each run doing useful work;
- deterministic validation remains intact;
- parallel breadth can stay high while authority-dependent writes remain serialized;
- unresolved rows still fail closed rather than being guessed.

### Stop points that SHOULD remain
Stop only when:
- human review/approval is explicitly required;
- new external authority evidence must be researched;
- a gate fails;
- accepted-source/main/production mutation would begin.

This complements docs/PARALLEL_AUDIT_EXECUTION_PATTERN.md: maximize horizontal work inside a stage, but minimize unnecessary CI synchronization boundaries.
