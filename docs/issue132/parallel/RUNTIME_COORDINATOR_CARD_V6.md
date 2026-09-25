# Issue132 Runtime Coordinator Card V6 — canonical QA/watchdog

Status: ACTIVE for Coordinator. Supersedes V5 operationally.

Goal: protect real image-generation discoverability without duplicating Worker or Repair work. Adult/sexual content is normal supported use and is not high-risk by itself.

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Worker authority: resolve only from RUNTIME_AUTHORITY.json roles.worker.path
Repair authority: resolve only from RUNTIME_AUTHORITY.json roles.repair.path
QA baseline: docs/issue132/parallel/QA_BASELINE.json

## Ownership
Coordinator owns:
- checkpoint prefix / staging high-watermark / write-gap accounting;
- newly crossed post-baseline 100-row QA;
- bounded legacy QA backlog;
- CI interpretation and frozen-contract drift detection;
- effective historical repair debt;
- exact promotion-blocking hold visibility;
- Lane3 route-family debt;
- cross-lane gap/overlap/ownership mistakes.

Coordinator does not redo normal Worker classification or historical Repair work.

## Minimal live read
Per run:
1. read RUNTIME_AUTHORITY.json, this card, QA_BASELINE.json;
2. list checkpoint/staging/repair-overlay/QA-marker metadata needed for current effective state;
3. inspect latest relevant Issue132 CI summary once;
4. when the current staging-validator v3 JSON is present, take exact `effective_invalid_windows`, `effective_invalid_window_counts`, `promotion_blocking_holds`, and total directly from it;
5. only if those fields are absent/null/stale, read the effective first staging window after the affected lane checkpoint prefix and/or fetch detailed CI logs.

Never use deleted status caches as authority.

## Progress
Report checkpoint prefix and staging high-watermark separately.
A valid staging high-watermark may be far ahead of immutable checkpoint prefix.
Do not confuse the two.

## QA scheduling
QA_BASELINE.json separates historical unmarked boundaries from newly crossed boundaries.

Priority:
1. any newly crossed post-baseline 100 boundary;
2. at most ONE legacy backlog 100-boundary block per Coordinator run;
3. no re-audit of a boundary that already has a valid QA marker.

Legacy backlog is NOT waived. It is merely bounded so current forward work is not blocked by historical bookkeeping.

For a selected QA block:
- inspect genuinely high-risk rows: RESEARCHED, MIXED, SEARCH_ORIENTED, SEMANTIC_UNRESOLVED, gap=YES, route2/3, body/theme, or another concrete ambiguity/drift signal;
- inspect a small deterministic ordinary CHECKED sample;
- adult/sexual content alone is not a high-risk signal;
- challenge discoverability usefulness, not taxonomy aesthetics;
- expand only a confirmed systematic error family.

Write a compact marker:
docs/issue132/parallel/qa/lane-N/qa_XXXXXX_YYYYYY.json

A legacy boundary leaves backlog only after its valid QA marker exists.
A marker write rejection does not block Worker or Repair.

## Promotion-blocking holds
Do not infer this count from CI summaries.

For each lane:
1. determine checkpoint prefix from immutable checkpoints;
2. resolve the effective window beginning at prefix+1, including active repair overlay if present;
3. count its effective holds exactly.

Report exact per-lane and total counts when those three effective windows are readable.
If one is unreadable, name that lane/path as the blocker rather than declaring the whole count unknowable.

## Effective repair debt
Raw historical staging may remain invalid.
A valid active repair overlay supersedes raw-source debt for that source window.
Do not count stale raw errors after a valid active overlay exists.

Use current effective validator/CI evidence to identify remaining effective invalid windows. Prefer staging-validator v3 machine-readable counts over manually parsing individual ERROR lines. If the latest CI predates an active overlay, do not use it to re-add that source as debt.

CI failure caused solely by known historical staging debt does not stop forward Workers.
Frozen/immutable contract failure does.

Automation liveness is separate from report severity. CI red, QA debt, unreadable one-off metadata, or a zero-change run must not disable/pause the scheduled Coordinator. Disable only after Issue132 completion or explicit user instruction.

## Report
Only:
- checkpoint prefixes;
- staging high-watermarks/write-gaps;
- post-baseline QA due and at most one legacy QA block result;
- effective historical invalid-window debt;
- exact promotion-blocking holds by lane/total;
- Lane3 route-family state;
- real blockers.
