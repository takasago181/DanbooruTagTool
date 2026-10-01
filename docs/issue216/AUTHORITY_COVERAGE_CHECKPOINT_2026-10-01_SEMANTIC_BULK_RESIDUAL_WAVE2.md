# Issue #216 Semantic Bulk / Residual Wave 2 — 2026-10-01

## Cohort state

- Frozen cohort / accounted: **13983 / 13983**.
- Terminalized: **3932 (28.1199%)**.
- HOME_CONFIRMED: 3842.
- SOURCE_RESEARCHED_NO_SAFE_EVIDENCE: 68.
- POLICY_BLOCKED: 2.
- IDENTITY_BLOCKED: 12.
- EVIDENCE_CONFLICT: 8.
- UNRESEARCHED: **10051**.
- Top500 open: **134**; Top2000 open: **992**.
- Source registry: 1109; exact member mappings: 3965; reused members: 3511 (reuse ratio 0.882383).
- Missing Copyright roots: 0; existing #180 HOME changed: **0**.

## Cohort-wide semantic pass

One active Copyright implication snapshot was joined to the open cohort after normalization through the verified alias index. Snapshot SHA-256: `c535be66210785124af3359bf95a1afaaf229d9c06ad7f5ff1831ad216fec58c` (5,920 active rows, 6 pages). It yielded **0 direct Character → Copyright relations**, **0 unique HOME candidates**, and **0 multiple-root conflicts**. The 2,785 Copyright → Copyright relations are used for validated title-to-franchise root normalization and Browse context only; no Character HOME is inferred from hierarchy without an independent exact member source.

Rejoining accepted sources yielded 0 AUTO candidates and 20 REVIEW_REQUIRED associations across 8 source scopes / 18 distinct open Characters. Integrator rechecked them against source scope, exact identity, aliases and validated HOME/root rules; none resolved safely. Cached exact membership, current qualifier evidence and validated variant inheritance produced 0 additional decisions. No route is terminalized merely because a ledger lacks evidence.

## Residual census

- A_DIRECT_IMPLICATION_MISSING_BUT_STRONG_IP_ROUTE: 8399
- B_VARIANT_IDENTITY_MISSING: 627
- C_MULTIPLE_COPYRIGHT_IMPLICATION_CONFLICT: 0
- D_CREATOR_ARTIST_QUALIFIED_OC: 973
- E_REAL_PERSON_MASCOT_NON_WORK_CANDIDATE: 0
- F_PLATFORM_COMPANY_GENERIC_FAMILY_CANDIDATE: 0
- G_ROOTLESS_IN_FROZEN_STRUCTURAL_GRAPH: 32
- H_OTHER_LONG_TAIL: 20


The census is routing-only. It does not turn candidate roots, creator/artist wording, page rank, or missing graph edges into HOME evidence.

## Root-scoped residual wave

Since parent pushed HEAD `a446863ac225c682ebbecef77dc2a24f7301cb1d`, 11 exact HOME decisions have been integrated across 5 positive source scopes / 5 new accepted source records. The new batches are Cloud of Darkness (1), hololive Myth lineup (3), Dragon Ball Super: SUPER HERO (5 across 2 official pages, normalized through active Copyright edges 26622/5965 to stable `dragon_ball`), and VA-LIV (2 exact official members, normalized through active Copyright edge 83161 to stable `idolmaster`). The yields were 1, 3, 1, 4, and 2 per positive scope: **2.20 terminalized per positive source scope**.

Nine new source URLs were opened in the broader residual wave; the ratio is **1.22 terminalized per new URL**. Three repeated fetches were recorded (two Gundam URLs and one P5T URL); they produced no decisions. A separate Persona page exposed no extractable names. Three new Hololive talent profiles named six mascot/shikigami candidates, but all six were held after the integrator found an explicit prior Issue #180 QA rejection for the same Fubuki mascot-to-`hololive` HOME proposals on company/platform HOME grounds. No policy override was made. Two further Hololive surfaces remain REVIEW_REQUIRED; the pages’ partial omissions are not negative evidence.

## Route and queue validation

- Route ledger: 59534 rows for 10051 open Characters; route builder terminalized 0.
- Route states: `{"AMBIGUOUS":10,"CONFLICT":0,"NEGATIVE_COMPLETE":10092,"NOT_APPLICABLE":19475,"POSITIVE":4,"UNCHECKED":29953}`.
- Queue: 2042 root rows; 34 roots / 81 source scopes scouted; Top500 open 134; Top2000 open 992.
- Rootless open count: 79; missing roots 0.

## Validation

- Issue #216 + #180 v3 focused suites: **84/84 PASS** (pytest Temp redirected to ignored worktree scratch after host Temp cleanup hit sandbox ACL failures).
- Implication join, route accounting, source-yield queue, and membership projection deterministic rebuilds: PASS.
- Python compile and `git diff --check`: PASS.
- Full #180 regression and CI: not run; full regression inputs are unavailable in this worktree.
- Coverage validator: structurally valid but incomplete while UNRESEARCHED remains.

## Next gate

Continue cohort-wide residual processing, selecting source scopes using current exact open overlap and empirical yield. Preserve explicit #180 policy decisions; in particular, do not convert company affiliation or mascot association alone into a HOME. Keep all source omissions non-negative unless a COMPLETE scope is proven. No main merge or production apply.
