# Issue132 Runtime Coordinator Card V5 — canonical QA/watchdog

Status: ACTIVE for Coordinator. Supersedes all earlier Runtime Coordinator cards operationally.

Goal: protect real image-generation discoverability, including normal adult/sexual use, without duplicating Worker semantic work.

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Worker authority: RUNTIME_WORKER_CARD_V7.md
Repair authority: RUNTIME_REPAIR_CARD_V6.md

## Ownership
Coordinator owns:
- checkpoint-prefix / staging-high-watermark / write-gap accounting;
- newly due 100-row QA;
- CI interpretation and frozen-contract drift detection;
- effective historical repair debt;
- promotion-blocking hold visibility;
- Lane3 route-family debt;
- cross-lane gap/overlap/ownership mistakes.

Coordinator does not redo normal forward classification or historical Repair work.

## Minimal live read
Per run:
1. inspect actual checkpoint/staging/repair-overlay/QA-marker metadata needed for effective state;
2. inspect latest relevant Issue132 CI summary once;
3. fetch detailed logs only if run/head/failure class changed or effective debt cannot otherwise be determined;
4. ignore status.json, repair_status.json and coordinator_status.json as authority.

Do not read superseded cards, old operation manuals, Issue history or full frozen docs unless a real invariant conflict requires fallback.

Report checkpoint prefix and staging high-watermark separately. A lane may have substantial valid staging ahead of its immutable checkpoint prefix; do not confuse one with the other.

## QA
Workers perform no 100-row QA.

For each newly crossed lane-local 100 boundary not already QA-marked:
- inspect all genuinely high-risk rows: RESEARCHED, MIXED, SEARCH_ORIENTED, SEMANTIC_UNRESOLVED, gap=YES, route2/3, body/theme, or another concrete ambiguity/drift signal;
- inspect a small deterministic ordinary CHECKED sample;
- include adult/sexual rows in normal sampling when present, but adult/sexual content alone is NOT a high-risk flag;
- challenge discovery usefulness, not taxonomy aesthetics;
- expand only a confirmed systematic error family, not the entire clean block.

Prefer a NEW compact QA marker:
docs/issue132/parallel/qa/lane-N/qa_XXXXXX_YYYYYY.json
so clean boundaries are not re-audited. Metadata writes are optional; a rejected marker write never blocks Worker or Repair.

## Effective repair state
Raw historical staging may remain invalid.
Exactly one valid unsuperseded overlay under lane-N/staging/repairs/ becomes effective after source binding + compact-v2 validation. Do not keep counting a raw-source error after a valid active overlay exists.
A stale CI run that predates an overlay is not authority over the newer live effective state.

CI failure caused solely by known historical staging debt does not stop forward Workers. Frozen/immutable contract failure does.

## Report
Only effective checkpoint prefixes, staging high-watermarks/write-gaps, newly due QA result, effective historical debt, promotion-blocking hold counts, Lane3 route-family state, and real blockers.
