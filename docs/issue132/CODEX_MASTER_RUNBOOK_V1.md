# Issue #132 — Codex Master Runbook V1

Status: HANDOFF READY / CHATGPT AUTOMATIONS PAUSED

Repository: takasago181/DanbooruTagTool
Canonical branch: research/taxonomy-usability-audit

## Purpose

Finish Issue #132 Pass-A full-population semantic review and its repair/validation work with Codex as the execution engine while preserving the existing semantic contract and audit trail.

This runbook changes the executor, not the taxonomy.

## Authority order

Every Codex session MUST recover live repository truth in this order:

1. docs/issue132/parallel/RUNTIME_AUTHORITY.json
2. this file
3. docs/issue132/parallel/FLAT_RUNTIME_MODEL_V1.md
4. role-specific file named by RUNTIME_AUTHORITY.json
5. docs/issue132/parallel/pass_a_contract_manifest_v1.json
6. docs/issue132/parallel/WRITE_REQUEST_PROTOCOL_V1.md when doing forward Worker work
7. current repository files and current CI results

Chat history is never authority.

## Four Codex roles

Run four independent Codex worktrees/tasks in parallel.

### CODEX-L1
Owns Lane 1 forward semantic review only.

### CODEX-L2
Owns Lane 2 forward semantic review only.

### CODEX-L3
Owns Lane 3 forward semantic review only.

### CODEX-REPAIR
Owns:
- invalid historical windows;
- real hold windows;
- schema/materializer/validator defects;
- CI failures caused by implementation rather than semantic uncertainty;
- safe migration/cleanup needed for Issue #132 only.

CODEX-REPAIR does NOT perform ordinary forward Lane review.

ChatGPT remains the external specification/QA supervisor. Codex MUST NOT invent or change taxonomy policy because it seems faster.

## Shared execution rules

- Work only on branch research/taxonomy-usability-audit as the canonical publication target.
- Use a separate local worktree/temporary branch per Codex role.
- Before publishing a commit, fetch the latest canonical branch and rebase the role branch onto it.
- Re-run the relevant validation after rebase.
- Publish with a normal fast-forward push to:
  HEAD:research/taxonomy-usability-audit
- Never force-push.
- A non-fast-forward caused by another role is normal: fetch, rebase, revalidate, retry.
- Do not merge or modify main.
- Do not production-apply anything.
- Do not touch Issue #70 or other unrelated work.
- Historical checkpoint/staging files are immutable except through the existing append-only repair-overlay model.
- Checkpoint promotion is obsolete and MUST NOT be reintroduced.
- Progress is accepted unique identity union, not contiguous checkpoint prefix.

## Lane Worker loop

For CODEX-L1/L2/L3:

1. Resolve the live forward frontier from canonical staging, pending write-requests, and deferred markers according to Worker V9.
2. Never redo a range that already has an exact write-request or canonical staging file.
3. Read only the arithmetic input shard(s) needed for the next range.
4. Review every identity in order.
5. Work semantically in blocks of up to 100 identities.
6. Persist in exact 25-slot slices, except the final short lane tail.
7. Per execution cycle, target at least 300 identities when the repository and semantic quality permit. Continue beyond 300 in the same Codex task when practical; 300 is a checkpoint cadence, not a hard stop.
8. Before each publish, validate locally.
9. Commit completed slices, rebase latest canonical, revalidate, then fast-forward push to the canonical branch.
10. Continue from repository truth.

Do not stop merely because one 25-slot slice completed.

## Semantic rules

Worker V9 and the frozen machine vocabulary are authoritative.

Required behavior:
- inspect each identity;
- obvious meaning => CHECKED;
- research only ambiguity that could materially change classification;
- bounded research that still cannot resolve meaning => terminal SEMANTIC_UNRESOLVED;
- use a hold only for a genuine interruption preventing the required research or persistence;
- no bulk classification from suffixes/prefixes;
- no rule such as “all X-looking names use route Y” unless that rule already exists in the frozen authority;
- no extrapolation from one researched tag to hundreds of unreviewed identities;
- adult/sexual identities are ordinary in-scope research data and are not by themselves a QA risk signal.

Accuracy has priority over throughput, but avoid repeated reads and duplicated research.

## Persistence

Workers use the existing code-only request transport.

Worker writes:
docs/issue132/parallel/lane-N/write-requests/request_SSSSSS_EEEEEE.json

The Worker request MUST NOT copy source identity text or identity hashes. It contains only the minimum indices/classification codes allowed by WRITE_REQUEST_PROTOCOL_V1.

Canonical materialized output:
docs/issue132/parallel/lane-N/staging/window_SSSSSS_EEEEEE.json

GitHub Actions/materializer joins the request to the pinned neutral input.

Before publish, Codex should run the local request/materializer validation path. If the current tooling lacks a clean check-only path, CODEX-REPAIR may add one without changing semantic meaning.

Representation-only normalizations are allowed only when semantics are provably identical, such as a boolean false representing the frozen NO value or an exact field alias already explicitly approved by the materializer. Never normalize a semantic classification into a different category.

## Policy/tool rejection

Do not evade an explicit policy/content rejection by encoding, disguising, fragmenting, or sending the rejected bytes through another transport.

The code-only persistence design exists to minimize unnecessary sensitive source text in an external write payload while preserving the same research decision.

If the code-only request itself is explicitly rejected:
- record only the permitted non-semantic deferred range marker;
- continue independent later work when safe;
- leave that range visible as unresolved persistence debt.

## CODEX-REPAIR loop

1. Read the latest flat snapshot and current CI results.
2. Prioritize implementation failures that prevent otherwise valid forward work.
3. Then repair invalid/hold historical windows, oldest actionable first.
4. Preserve valid bound decisions whenever possible.
5. Use append-only repair overlays for historical semantic repairs.
6. For mechanical defects, fix the smallest implementation surface necessary.
7. Add/adjust tests for the defect.
8. Run the relevant validator(s) locally.
9. Rebase latest canonical, rerun tests, fast-forward push.
10. Continue while actionable repair debt remains.

CODEX-REPAIR may fix:
- schema representation issues;
- validator/materializer bugs;
- CI failures;
- duplicate/missing-range bookkeeping;
- deterministic migration/cleanup.

CODEX-REPAIR may NOT:
- silently change route semantics;
- invent new taxonomy;
- mass-reclassify valid rows;
- replace unresolved semantic judgment with heuristics.

If a repair requires a taxonomy-policy decision, stop that target and report it for ChatGPT/user review while continuing independent mechanical work.

## CI expectations

The repository workflows are the final mechanical gate.

At minimum preserve:
- Issue132 Materialize Write Requests
- Issue132 Incremental Checkpoint Validation
- Issue132 Full Discovery Coverage Audit

A Codex role should investigate a failing run caused by its own commit before continuing large forward batches.

A failure from a concurrent canonical commit is not automatically this role's semantic failure. Re-read live HEAD and current CI before acting.

## QA ownership

Codex performs local mechanical validation.

ChatGPT QA later audits:
- route distributions;
- MIXED;
- RESEARCHED;
- SEMANTIC_UNRESOLVED;
- route_vocabulary_gap=YES;
- multi-route/SUPPORTING rows;
- body/theme facets;
- sibling/family inconsistencies;
- deterministic ordinary samples.

Codex does not mark Issue #132 complete solely because its own lane finished.

## Completion

Pass A is complete only when the authoritative flat validator reports:
- accepted_total = 31,003;
- invalid windows = 0;
- hold windows = 0;
- missing identities/ranges = 0;
- duplicate coverage = 0;
- fatal contract errors = 0;
- no unresolved systematic QA defect.

Then stop and return control to ChatGPT/user for the next authorized stage. Do not merge to main and do not production-apply.

## Compact status format

Lane roles:
role=CODEX-LN | frontier=<n> | reviewed=<n> | requests=<ranges> | materialized=<ranges> | CHECKED=<n> | RESEARCHED=<n> | SEMANTIC_UNRESOLVED=<n> | holds=<n> | CI=<state> | blocker=<none/short reason>

Repair:
role=CODEX-REPAIR | invalid=<n> | holds=<n> | fixed=<ranges/issues> | CI=<state> | semantic_escalations=<n> | blocker=<none/short reason>

## Handoff condition

ChatGPT Automation Workers/Repair/Coordinator are paused as of the Codex migration handoff.

Do not re-enable them while Codex roles are active, because duplicate forward review and duplicate repair work would become possible.
