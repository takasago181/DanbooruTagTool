# Issue #216 Active Implication Bulk Checkpoint — 2026-10-01

## Current cohort state

- Frozen cohort / accounted: **13983 / 13983**.
- Terminalized: **3898 (27.8767%)**.
- HOME_CONFIRMED: 3808.
- SOURCE_RESEARCHED_NO_SAFE_EVIDENCE: 68.
- POLICY_BLOCKED: 2.
- IDENTITY_BLOCKED: 12.
- EVIDENCE_CONFLICT: 8.
- UNRESEARCHED: **10085**.
- Top500 open: **137**; Top2000 open: **1004**.
- Source registry: 1101; exact member rows: 3931; reused terminalized member rows: 3480 (ratio 0.882129).
- Missing Copyright roots: 0; existing #180 HOME changes: **0**.

This checkpoint preserves the decisions and source work accumulated before the semantic-bulk change, including the 21 exact HOME decisions since `4d9aece`. No unresolved route is terminalized from absence in a partial source.

## Danbooru active implication snapshot

- Source: one active implication snapshot filtered on consequent Copyright category 3; 5,920 rows over 6 pages.
- Snapshot time / SHA-256: `2026-09-30T23:22:03Z` / `c535be66210785124af3359bf95a1afaaf229d9c06ad7f5ff1831ad216fec58c`.
- Verified Issue #70 alias index: `3f942704a10bb342ae7368024337849d392d54745061cf9259e51b9f6080a394`; tag catalog: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`.
- Exact cohort Character → Copyright relations: **0**; unique HOME candidates: **0**; multi-root conflicts: **0**; no direct implication: **10085**.
- Copyright → Copyright hierarchy edges: 2785; hierarchy is context only and creates no transitive Character HOME.
- New decisions from this snapshot: **0**. Deleted/retired relations are excluded; ambiguous aliases and non-canonical roots do not resolve identities.

## Cohort-wide offline rejoin and residual census

The same frozen cohort was rejoined against accepted exact source/member records, the verified alias snapshot, validated #180 family/root qualifiers, and PASS variant/base rows. The accepted source inventory audit found **0 open AUTO candidates** and **20 REVIEW_REQUIRED** candidates. Cached explicit Danbooru wiki lists yielded 0 additional decisions. The deterministic cohort-wide rule check found 0 new safe qualifier, membership, or variant decisions.

Residual census (routing only; no terminal states assigned):

| Residual class | Count |
| --- | ---: |
| A_DIRECT_IMPLICATION_MISSING_BUT_STRONG_IP_ROUTE | 8433 |
| B_VARIANT_IDENTITY_MISSING | 627 |
| C_MULTIPLE_COPYRIGHT_IMPLICATION_CONFLICT | 0 |
| D_CREATOR_ARTIST_QUALIFIED_OC | 973 |
| E_REAL_PERSON_MASCOT_NON_WORK_CANDIDATE | 0 |
| F_PLATFORM_COMPANY_GENERIC_FAMILY_CANDIDATE | 0 |
| G_ROOTLESS_IN_FROZEN_STRUCTURAL_GRAPH | 32 |
| H_OTHER_LONG_TAIL | 20 |


The creator/artist-category suffix signal appears on 979 rows; that signal alone does not establish non-work status. No row was classified as real-person/non-work or platform/company because the current accepted relation set does not establish those meanings. The 32 graph-rootless rows are not proven authority-unavailable.

## Queue and efficiency

- Queue rebuilt from current decisions: 2042 routing roots; 34 scouted roots / 81 source scopes.
- Yield states: {"ESTIMATED": 216, "KNOWN_POSITIVE": 0, "KNOWN_ZERO": 1, "UNKNOWN": 1825}. UNKNOWN remains distinct from KNOWN_ZERO.
- Post-count snapshot SHA-256: `893fbf07c7d0250e1c30d43b9e01aca69d56e2e6f3d742dcc233e889dfec5aec`; current for this decision set: True.
- Since `4d9aece`: 21 exact HOME decisions across 4 positive reviewed source scopes, plus one implication snapshot review with zero decisions: **4.2 terminalized / all reviewed scopes**. This is a small transition batch, not a yield target.
- No roots are declared complete from partial roster coverage.

## Validation

- Authority coverage schema/root/cardinality validation: **PASS_INCOMPLETE** (10085 remain).
- Deterministic implication join, semantic membership projection, and offline cohort bulk checks: **PASS**.
- Issue #216 tests: **57/57 PASS** (including five active implication snapshot gate tests); Issue #180 v3 regression tests: **24/24 PASS**; combined: **81/81 PASS**.
- Python compile and `git diff --check`: **PASS**.
- Full Issue #180 Character data regression: not run because the ignored preflight inputs are absent from this worktree. CI: not run.

No main merge or production apply. Continue with high-value residual authority scopes; keep the implication and hierarchy tables as reusable evidence, and route unresolved source research by actual evidence scope after the semantic bulk pass.
