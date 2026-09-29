# Issue #216 — full authority coverage layer v1

## Contract

This layer is additive to the immutable Issue #180 master. Its only members are the 13,983 Characters whose frozen #180 state is `HOME_UNRESOLVED`; it never includes or rewrites the 21,907 baseline-confirmed rows. The #180 HOME policy remains unchanged: zero or one canonical HOME, validated authority only, conflicts unresolved, and no co-occurrence, popularity, candidate-score, or candidate-root inference.

Every frozen cohort member has exactly one research state:

- `UNRESEARCHED` — no terminal classification; cannot satisfy completion.
- `SOURCE_RESEARCHED_NO_SAFE_EVIDENCE` — at least one scoped authority source was actually reviewed and the recorded findings cannot safely prove one HOME.
- `POLICY_BLOCKED` — the single-HOME product policy excludes or cannot normalize the relationship.
- `IDENTITY_BLOCKED` — the Character identity or exact source mapping is not established.
- `EVIDENCE_CONFLICT` — at least two validated candidate roots remain; no winner is selected.
- `HOME_CONFIRMED` — one HOME is supported by accepted authority and an exact reviewed member mapping.

The coverage validator has no `post_count`, popularity, co-occurrence, or candidate-root evidence field. Frequency can select the order of work, but is not evidence. Source reuse is exact-member only. A partial roster may support listed members and cannot classify absent members.

## Frozen inputs and outputs

`freeze_authority_coverage_cohort.py` reads the immutable #180 `character_home_master_v3.csv`, checks its SHA-256 (`135463a5…77071`), the 35,890-row population, and the 13,983 unresolved count, then emits a canonical-identity-sorted cohort and hash manifest. It refuses to overwrite frozen output. The existing Top500 remains an immutable calibration subset and is cross-check context only.

The coverage data contract is:

- `AUTHORITY_COVERAGE_COHORT_V1.csv`: frozen `cohort_id`, canonical Character, baseline state and baseline HOME.
- `COPYRIGHT_ROOTS_V1.csv`: existing HOME roots observed in the frozen confirmed master; newly confirmed roots must be present here, proving zero missing-root references within the baseline-supported authority set.
- `COPYRIGHT_AUTHORITY_REGISTRY_V1.csv`: deterministic `src-` ID plus source owner, URL, authority type, status, exact scope/roster availability, review date, claim, provenance, reuse flag and notes.
- `AUTHORITY_SOURCE_MEMBERS_V1.csv`: one reviewed exact member mapping per covered Character and source. Only exact canonical identity, validated alias, reviewed name mapping, or documented identity mapping are accepted.
- `AUTHORITY_COVERAGE_DECISIONS_V1.csv`: exactly one terminal or `UNRESEARCHED` decision per cohort row, with source IDs, claim, provenance and explicit reason.

The validator rejects confirmed HOME without an accepted source, exact member mapping, source claim, and matching canonical root. It rejects no-safe-evidence without an actual researched source and finding; conflicts without two validated roots; and any attempt to place a baseline-confirmed Character in the unresolved cohort. A complete run requires exactly 13,983 accounted rows and zero `UNRESEARCHED`.

## Execution order

1. Calibrate all frozen Top500 rows and reach zero `UNRESEARCHED` there.
2. Expand the frozen post-count ranking through rank 2,000. Counts affect priority only.
3. Batch by candidate Copyright root and reuse official rosters/directories. Record exact member mappings, not roster-wide assumptions.
4. Research remaining long-tail identity, policy, variant, avatar and ambiguous cases individually where batching does not cover them.
5. Reconcile all 13,983 rows and stop only when the validator reports `complete: true`.

Each checkpoint is a deterministic snapshot of cohort size, state counts, source count/reuse, and the cohort hash. A checkpoint never changes the completion rule.

## Initial coverage checkpoint

The full 13,983-row cohort was frozen from the local ignored #180 master after verifying its exact expected SHA-256. The generated `AUTHORITY_COVERAGE_COHORT_V1.json` records that provenance. The initial decision ledger was seeded with 13,983 `UNRESEARCHED` rows. Independent revalidation of the 19 previously source-checked Top500 proposals added 19 `HOME_CONFIRMED` decisions across 13 official sources and 19 exact member mappings. The other 481 Top500 members and 13,483 remaining cohort members are still `UNRESEARCHED`; this is an incomplete checkpoint, not a completion claim.

The root catalog currently contains 1,672 canonical Copyright roots already used by the 21,907 confirmed #180 rows. It is intentionally a HOME-root existence set, not the entire 8,536-tag Copyright catalog.

The source master remains a protected ignored artifact and is not copied into this branch. Reproducing the freeze from a clean checkout requires the exact #180 master artifact to be made available as a read-only input. The Top500 snapshot is not a substitute.
