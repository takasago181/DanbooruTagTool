# Issue #180 — Codex Worktree start prompts v1

Create exactly five Worktrees from the current `research/issue180-single-home-pilot` authority after the parallel-design commit is present.

## Forward 0

Branch: `research/issue180-forward-0`

Read root AGENTS.md, Issue #180 latest comments, `docs/issue180/parallel/PARALLEL_EXECUTION_V1.md`, `PARALLEL_EXECUTION_V1.json`, and v3 README. Fetch canonical, merge it into this branch when needed, run the v3 pipeline and parallel assignment builder, then continuously process only FORWARD assignments with owner_slot=0. Write append-only proposal JSON files only under `docs/issue180/parallel/proposals/fwd-0/`. Never edit canonical evidence/decision/terminal-review rows or push canonical. Preserve the HOME 0..1 rule and missing-over-wrong policy. Check actual source pages; no guessing. Commit/push coarse proposal batches and continue. Routine unresolved cases, graph rebuilds and technical retry are not user blockers. Return only for a true semantic/protected-source blocker or when no slot-0 assignments remain.

## Forward 1

Same contract as Forward 0, but branch `research/issue180-forward-1`, owner_slot=1, proposal path `docs/issue180/parallel/proposals/fwd-1/`.

## Forward 2

Same contract as Forward 0, but branch `research/issue180-forward-2`, owner_slot=2, proposal path `docs/issue180/parallel/proposals/fwd-2/`.

## Forward 3

Same contract as Forward 0, but branch `research/issue180-forward-3`, owner_slot=3, proposal path `docs/issue180/parallel/proposals/fwd-3/`.

## QA / Integrator

Branch: `research/issue180-qa-integrator`

Read root AGENTS.md, Issue #180 latest comments, `docs/issue180/parallel/PARALLEL_EXECUTION_V1.md`, config, v3 README and current migration/Research Unit ledgers. You are the only canonical writer. Fetch canonical and all four forward branches directly; do not ask the user to relay worker output. First handle QA-owned buckets (SAFE_STRUCTURE_READY, POLICY_BLOCKED, IDENTITY_BLOCKED, STRUCTURAL_NO_SAFE_PATH, CONFLICT_REVIEW). Then ingest new forward proposals in epochs, independently review them under the runbook, reject stale/unowned proposals, and integrate accepted facts into the existing canonical evidence/decision/terminal-review ledgers without weakening evidence rules. Append every QA decision to QA_REVIEW_LEDGER_V1.csv. After each epoch run full v3 + assignment rebuild + tests + guards, push this QA branch, require green CI, then fast-forward the exact green HEAD to `research/issue180-single-home-pilot`. Never force push, merge main, production-apply, or mutate #70/#179/#132. Diagnose and repair routine harness/CI defects autonomously. Rebuild units after evidence changes and continue until OPEN/PENDING=0. Return early only for a true semantic/protected-source blocker; otherwise return once for final independent ChatGPT audit.
