# Issue132 Runtime Coordinator Card V2 — QA and watchdog only

Status: ACTIVE for Coordinator.

Goal lock: preserve real image-generation discoverability for users who do not know exact Danbooru tags, including normal adult/sexual workflows, while preventing semantic drift and avoiding duplicated worker overhead.

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Worker authority: RUNTIME_WORKER_CARD_V6.md
Repair authority: RUNTIME_REPAIR_CARD_V5.md

## Coordinator owns

- effective forward frontier/high-watermark and write-gap accounting;
- 100-row QA;
- high-risk semantic audit and small deterministic ordinary sample;
- CI interpretation and drift detection;
- historical effective repair debt;
- Lane3 route-family debt;
- cross-lane gaps/overlaps/ownership mistakes.

Coordinator does NOT redo normal forward classification.

## Minimal live read

Per run:
1. List actual checkpoint/staging/repair-overlay/QA-marker metadata needed to derive effective state.
2. Read latest relevant Issue132 CI summary once.
3. Fetch detailed CI logs only if run/head/failure class changed or effective debt cannot otherwise be determined.
4. Ignore stale status.json, repair_status.json, coordinator_status.json as authority.

Do not reread old cards/issues/frozen docs unless current-card or contract invariants conflict.

## QA

Worker performs no 100-row QA.

For each newly crossed lane-local 100 boundary not already QA-marked:
- inspect all high-risk rows: RESEARCHED, MIXED, SEARCH_ORIENTED, SEMANTIC_UNRESOLVED, gap=YES, route2/3, body/theme, adult/sexual;
- inspect a small deterministic ordinary CHECKED sample;
- challenge discoverability using the product goal, not taxonomy aesthetics;
- expand only a confirmed systematic error family, not the whole block by default.

Adult/sexual content itself is not a defect/risk signal; only classification uncertainty or discoverability mistakes are.

When QA completes, prefer a NEW compact marker:
docs/issue132/parallel/qa/lane-N/qa_XXXXXX_YYYYYY.json
so later runs do not repeat the same audit. Marker contains only boundary, source window identities/SHAs or commit/head reference, counts, and compact flags; no large prose.

## Repair/effective state

Raw historical staging may remain invalid.
Exactly one valid unsuperseded overlay under lane-N/staging/repairs/ becomes effective state after source binding + compact-v2 validation.
Do not keep counting raw-source errors once an overlay is valid.

CI failures caused solely by known historical debt do not stop forward workers.

## Write policy

Coordinator metadata writes are optional.
Prefer append-only QA markers over mutable status files.
If a marker write is rejected, report it; do not loop or block Worker/Repair.

Never evade safeguards.

## Report

Only effective lane high-watermarks/write-gaps, NEW progress since prior effective view when determinable, QA findings, historical effective debt counts, Lane3 route-family state, and real blockers.
