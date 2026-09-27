# Issue #132 production candidate gate

**Verdict: `READY_FOR_MAIN_REVIEW = YES`**

The exact accepted 274-pair secondary-route delta passes production-size identity, shelf, functional, performance, and retained-memory checks against a fresh catalog built from live main and current protected inputs.

## Projection reconciliation: root cause of the 10 shelf differences

Pass C's `shelf_before_after.csv` uses the Pass B `current_routes` research projection. The earlier production gate counted browseable identities in the actual catalog and `UnifiedBrowseIndex`. The identity-level comparison covers the same 31,003 normalized canonical identities and proves that the 339 differing memberships all exist only in the research projection. There are zero memberships found only in the runtime projection. Each route's count delta equals `only_in_research - only_in_runtime`, and the runtime membership count equals the actual browse shelf count.

| Route | Pass C research | Actual runtime | Research only | Runtime only |
|---|---:|---:|---:|---:|
| RELATION_ROLE | 102 | 73 | 29 | 0 |
| BODY_SITE | 2,371 | 2,343 | 28 | 0 |
| CLOTHING_EXPOSURE | 8,972 | 8,915 | 57 | 0 |
| TOOL_OBJECT | 5,691 | 5,660 | 31 | 0 |
| NONHUMAN_TRANSFORM | 101 | 83 | 18 | 0 |
| ACTION_CONTACT | 3,928 | 3,840 | 88 | 0 |
| FLUID_EXCRETION | 217 | 176 | 41 | 0 |
| SCENE_BACKGROUND | 1,075 | 1,074 | 1 | 0 |
| STYLE_PROCESSING | 1,027 | 1,026 | 1 | 0 |
| CONTENT_RATING | 52 | 7 | 45 | 0 |

This fully explains the previous BLOCKED result as a difference between research projection and actual runtime projection. The Pass C research artifacts remain unchanged. The production shelf gate now uses the actual live-main runtime baseline. The complete identity and source mapping is in [research_runtime_route_membership_diff.csv](research_runtime_route_membership_diff.csv).

## Candidate identity and shelf validation

- Input remains exactly 274 accepted pairs across 273 identities from reconciliation head `de450958eb598a2c7c3a34b112f139dfba617c6e`; the embedded asset is SHA-256 pinned.
- All target identities resolve to one already-browseable General/Special runtime identity. All routes exist, no route is already present, and the overlay only adds memberships through the existing `UnifiedBrowseIndex` path.
- Actual delta: **274 route additions**, **273 changed identities**, **0 unexpected changed identities**, **0 removals**, **0 non-#132 metadata changes**. The catalog remains at 31,003 ordinary identities and 124,895 total entries.
- All 19 runtime shelves satisfy `actual before + accepted additions = actual after`. This includes BODY_SITE +97, POSE_POSITION +52, ACTION_CONTACT +18, COMPOSITION_CAMERA +17, FLUID_EXCRETION +15, and RELATION_ROLE +15.
- Serialized catalog delta is +8,192 bytes. Same-condition build allocation remains 247,520,632 bytes for both catalogs. UnifiedBrowseIndex allocation is 78,246,136 baseline / 78,258,136 candidate (+12,000 bytes).

## Performance and retained memory

Search and browse timings use interleaved baseline/candidate operations: five rounds of seven samples per case. Results are medians from the same process and runtime. Search ranking and `FilterSearchHits` results match exactly.

| Operation | Baseline median | Candidate median | Result |
|---|---:|---:|---|
| English search | 49.20 ms | 50.81 ms | +3.3%, below regression threshold |
| Japanese search | 51.29 ms | 52.10 ms | +1.6%, below threshold |
| Mixed search | 67.12 ms | 67.68 ms | +0.8%, below threshold |
| Long neutral browse (28,344 rows) | 0.84 ms | 0.88 ms | same rows, below threshold |
| Sexual neutral browse (2,964 rows) | 0.68 ms | 0.71 ms | same rows, below threshold |
| GeneralPurpose neutral browse (27,055 rows) | 0.79 ms | 0.82 ms | same rows, below threshold |
| Sexual body + theme browse (33 rows) | 1.28 ms | 1.05 ms | same rows |

FilterSearchHits medians round to 0.00 ms in the summary; unrounded measurements and all browse cases are in the machine report. No case crosses the recorded material-regression thresholds.

Retained-memory measurements use five fresh processes per build. Each process loads the catalog, then builds the `UnifiedBrowseIndex`; full blocking compacting GC runs before each sample, with the measured objects kept alive. Median managed bytes:

- Catalog: 261,175,344 baseline / 261,207,440 candidate (**+32,096 bytes**).
- Catalog + index: 284,942,880 / 284,975,200 (**+32,320 bytes**).
- Index incremental retained bytes: 23,767,536 / 23,767,760 (**+224 bytes**).
- Candidate is lower in median process private bytes and working set; per-process samples are preserved in the JSON report because those OS readings vary more than managed retained memory.

The candidate's +32,320 managed bytes is below the gate's material growth limit of 2,849,428 bytes (1% of baseline combined managed memory). No material memory regression was observed.

## Build and regression

- Full tests: 212 passed, 16 skipped, 0 failed.
- Release solution build: succeeded, 0 warnings and 0 errors.
- Existing runtime-index performance test passed.
- No manual GUI launch or interactive prompt smoke has yet been run at this review gate; those checks are part of the authorized production promotion step.

## Provenance and boundaries

- Live main baseline: `e5d0f7d954ff491c1a5661a0652e6142f2b0d08d`.
- Baseline catalog hash matches the current runtime catalog: `14ad53d8a917ee2fc31c27fc20e2c364536a65a4339a25185df7cd43ca68f705`.
- Candidate catalog hash: `24665d7c92b9de9b22d92c7713f4e9876dc9c15b98e02324bbe670448bea7ff9`.
- Protected source hashes match the previous gate report. Source inputs, installed runtime, and UserData were read-only during this gate.
- No production apply or main modification occurred during gate evaluation.
- Follow-up research remains separate in [FOLLOW_UP_FINDINGS.md](FOLLOW_UP_FINDINGS.md).

Machine-readable full results: [gate_report.json](gate_report.json).
