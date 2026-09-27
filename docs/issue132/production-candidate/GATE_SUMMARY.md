# Issue #132 production candidate gate

**Verdict: `BLOCKED`**

This branch contains a reviewable implementation of the accepted, isolated secondary-route delta. It does not apply the delta to production or change `main`.

## Candidate and behavior

- Input: exactly 274 route pairs across 273 identities from reconciliation head `de450958eb598a2c7c3a34b112f139dfba617c6e`.
- The embedded CSV is pinned by SHA-256 and validated at catalog construction. The overlay requires each target to resolve to one existing browseable General/Special identity, rejects existing/unknown routes, and only unions the accepted route IDs.
- The candidate keeps the existing `UnifiedBrowseIndex` and search pipeline. Full-catalog comparison found 274 additions across 273 identities, zero unexpected changed identities, zero removals, and zero non-Issue-132 metadata changes. The ordinary identity count remains 31,003.
- Tests cover exact pair application, metadata preservation, search ranking, browse filters, and sexual-intent lens behavior.

## Blocking shelf reconciliation

The full production-size build from live main and current protected source inputs reproduced all 274 additions, but 10 before-counts do not match the accepted reconciliation shelf baselines. Since the exact shelf check is a required gate, the candidate cannot be marked ready until the baseline discrepancy is reconciled by the owning lane. This report does not alter the accepted counts or candidate list.

| Route | Live-main before → after | Accepted before → after |
|---|---:|---:|
| RELATION_ROLE | 73 → 88 | 102 → 117 |
| BODY_SITE | 2,343 → 2,440 | 2,371 → 2,468 |
| CLOTHING_EXPOSURE | 8,915 → 8,926 | 8,972 → 8,983 |
| TOOL_OBJECT | 5,660 → 5,665 | 5,691 → 5,696 |
| NONHUMAN_TRANSFORM | 83 → 83 | 101 → 101 |
| ACTION_CONTACT | 3,840 → 3,858 | 3,928 → 3,946 |
| FLUID_EXCRETION | 176 → 191 | 217 → 232 |
| SCENE_BACKGROUND | 1,074 → 1,090 | 1,075 → 1,091 |
| STYLE_PROCESSING | 1,026 → 1,030 | 1,027 → 1,031 |
| CONTENT_RATING | 7 → 8 | 52 → 53 |

The accepted additions per route match the candidate in all 19 shelves. The live-main baseline catalog hash matches the current runtime catalog hash recorded in the gate report. The gate used fresh catalog construction from protected inputs, not the runtime catalog as its build input. Protected source paths were omitted from the report; source data and UserData were read-only and untouched.

## Performance and regression results

- Full production catalog: 124,895 entries before and after; serialized catalog grows by 8,192 bytes.
- Catalog construction median: 484.10 ms baseline / 489.41 ms candidate; allocated bytes are equal (247,520,632). Retained-heap sampling reported zero for both, so it is not useful as a memory comparison.
- Browse index construction median: 93.28 ms / 90.46 ms; candidate allocation increases by 12,000 bytes. Retained-heap sampling again reported zero for both.
- English, Japanese, and mixed `abduction` searches return the same single ranked hit. Candidate medians were 79.04 ms, 82.89 ms, and 104.24 ms versus 87.43 ms, 89.64 ms, and 110.70 ms baseline. `FilterSearchHits` timing was effectively unchanged.
- Browse cardinality stayed the same for long-neutral (28,344), sexual-neutral (2,964), General-purpose-neutral (27,055), and sexual body+theme (33) queries. Expected candidate shelves grew by their exact route additions.
- Existing runtime-index performance harness passed. Its synthetic 126,427-entry catalog showed indexed search at 596 ms versus 1,584 ms legacy and indexed browse at 0.515 ms versus 1.651 ms legacy. Its heap comparison is separate from the zero retained-heap samples above.

## Verification and boundaries

- `dotnet test src/DanbooruTagTool.sln --no-restore -m:1 -nr:false -v:q`: 212 passed, 16 skipped, 0 failed.
- `dotnet build src/DanbooruTagTool.sln -c Release --no-restore -m:1 -nr:false -v:q`: succeeded, 0 warnings, 0 errors.
- `git diff --check`: clean.
- No production apply, runtime/UserData write, or `main` modification occurred. No manual Windows UI launch/scroll-idle smoke was run.
- Preserved follow-up findings are listed in [FOLLOW_UP_FINDINGS.md](FOLLOW_UP_FINDINGS.md).

Machine-readable measurements and source fingerprints: [gate_report.json](gate_report.json).

## Stop point

Stop at `BLOCKED` pending reconciliation of the 10 shelf baseline discrepancies and a useful retained-heap measurement. Do not promote or merge this candidate based on the current gate.
