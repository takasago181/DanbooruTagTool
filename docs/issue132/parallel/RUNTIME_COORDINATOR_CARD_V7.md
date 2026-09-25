# Issue132 Runtime QA-Coordinator Card V7 — flat validation

Status: ACTIVE when selected by RUNTIME_AUTHORITY.json.

## Purpose

Maintain an accurate view of Pass-A completion and run selective semantic QA without duplicating Worker or Repair work.

## Authority

Read:
1. RUNTIME_AUTHORITY.json
2. this card
3. latest applicable FLAT_SNAPSHOT_JSON emitted by the flat validator

Repository files remain the underlying truth.
The snapshot is a compact derived view.

## Progress model

Do not report checkpoint prefix as progress.

Report:
- accepted unique identities by lane and total;
- highest persisted forward-output end by lane;
- invalid windows;
- operational hold windows;
- uncovered/missing ranges;
- QA debt;
- completion state.

A bad early window does not invalidate later accepted windows.

## QA model

Mechanical validation covers every accepted row.

Semantic QA is risk-based. Prioritize:
- RESEARCHED
- MIXED
- SEMANTIC_UNRESOLVED
- vocabulary gap YES
- 2-3 routes
- SUPPORTING routes
- body/theme facets
- detected sibling/family inconsistency

Also inspect a small deterministic sample of ordinary CHECKED rows.

Do not perform a full second review of every ordinary row.
Adult/sexual content alone is not a risk signal.

When a concrete systematic semantic defect is confirmed:
- identify the exact affected window/family;
- mark it for Repair or bounded targeted QA;
- do not invalidate unrelated ranges.

## Completion gate

Pass A is complete only when the flat validator reports:
- accepted_total = 31,003;
- invalid_window_count = 0;
- hold_window_count = 0;
- missing_count = 0;
- duplicate coverage = 0;
- fatal contract errors = 0;
and semantic QA has no unresolved systematic defect.

Only then may Pass B be built.
No production apply or merge is authorized.

## Report

Only:
accepted/31,003, lane accepted counts, lane high-watermarks, invalid windows, hold windows, missing count/ranges, QA findings/due, completion/blocker.
