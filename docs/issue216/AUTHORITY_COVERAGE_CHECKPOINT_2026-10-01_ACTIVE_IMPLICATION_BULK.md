# Issue #216 Active Implication Bulk Checkpoint — 2026-10-01

## Current cohort state

- Frozen cohort / accounted: **13983 / 13983**.
- Terminalized: **3908 (27.9482%)**.
- HOME_CONFIRMED: 3818.
- SOURCE_RESEARCHED_NO_SAFE_EVIDENCE: 68.
- POLICY_BLOCKED: 2.
- IDENTITY_BLOCKED: 12.
- EVIDENCE_CONFLICT: 8.
- UNRESEARCHED: **10075**.
- Top500 open: **136**; Top2000 open: **1002**.
- Source registry: 1102; exact member rows: 3941; reused terminalized member rows: 3490 (ratio 0.882427).
- Missing Copyright roots: 0; existing #180 HOME changes: **0**.

This checkpoint preserves the decisions and source work accumulated before the semantic-bulk change, including the 21 exact HOME decisions since `4d9aece`. No unresolved route is terminalized from absence in a partial source.

## Targeted high-value roster integration

- Integrated one official `DRAGON BALL THE ONE` poll-eligible roster scope after the cohort-wide semantic pass. Its embedded module lists 212 exact named poll-eligible characters; source scope is complete only for eligibility, and omission is not franchise-wide negative evidence.
- Exact catalog/unique Issue #70 alias join produced 15 frozen-cohort identities; 5 were already terminal, and 10 open identities were accepted as exact Dragon Ball membership using the existing #180 `dragon_ball` root normalization PASS. No popularity/rank field was used.
- Batch result: 10 HOME decisions from 1 new reviewed source scope / 1 new URL (**10 terminalized per reviewed source and per new URL**). The remaining 38 root-routed open rows are outside this source's exact positive scope; no absence inference was applied.
- New source: `https://db1.dragon-ball-official.com/en/`; roster module SHA-256 `8df0bf89a2aa75b14e535b71a0ecf13845cbc9609e52b072d5e5f9096ee76667`; source page SHA-256 `4eadeb0ce55e81dd7d66438f766adf35b3b216c115e49ea46d5b88af312feed2`.

## Route accounting

- Added deterministic per-character route accounting for all **10075** currently open Characters: **59709** route rows, bound to the exact #180 structure graph SHA-256 `218cf30cb21695472e276cce327cd96a132665f3473c8925954059c3432c4bea` and active implication snapshot hash above.
- Route states: POSITIVE 6, NEGATIVE_COMPLETE 10126, AMBIGUOUS 13, CONFLICT 0, NOT_APPLICABLE 19543, UNCHECKED 30111. A COMPLETE roster absence closes only that exact source route. Partial/unknown absence and retained-member omissions remain UNCHECKED. Candidate roots are never written as HOME evidence.
- Deterministic route-ledger rebuild: PASS. The ledger does not terminalize decisions.

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
- This continuation added 10 exact HOME decisions across 1 new roster review: **10 terminalized / new source scope** and **10 / new URL**. The earlier +21 decisions across four positive scopes remain historical and are not included in this new-source yield.
- No roots are declared complete from partial roster coverage.

## Validation

- Authority coverage schema/root/cardinality validation: **PASS_INCOMPLETE** (10075 remain).
- Deterministic implication join, semantic membership projection, and offline cohort bulk checks: **PASS**.
- Issue #216 tests: **60/60 PASS** (including five active implication snapshot tests and three route-accounting tests); Issue #180 v3 regression tests: **24/24 PASS**; combined: **84/84 PASS**.
- Python compile and `git diff --check`: **PASS**.
- Full Issue #180 Character data regression: not run because the ignored preflight inputs are absent from this worktree. CI: not run.

No main merge or production apply. Continue with high-value residual authority scopes; keep the implication and hierarchy tables as reusable evidence, and route unresolved source research by actual evidence scope after the semantic bulk pass. Current gates: Top500 open 136, Top2000 open 1002, missing roots 0, existing #180 HOME changed 0.
