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
- `COPYRIGHT_ROOTS_V1.csv`: the complete 8,536-row canonical Copyright inventory from the exact Issue #70 catalog used by the #180 validator. This is the target tag universe for root-existence validation; use as authority that a name is a catalog root only, never as evidence that a Character belongs to it.
- `COPYRIGHT_AUTHORITY_REGISTRY_V1.csv`: deterministic `src-` ID plus source owner, URL, authority type, status, exact scope/roster availability, review date, claim, provenance, reuse flag and notes.
- `AUTHORITY_SOURCE_MEMBERS_V1.csv`: one reviewed exact member mapping per covered Character and source. Only exact canonical identity, validated alias, reviewed name mapping, or documented identity mapping are accepted.
- `AUTHORITY_COVERAGE_DECISIONS_V1.csv`: exactly one terminal or `UNRESEARCHED` decision per cohort row, with source IDs, claim, provenance and explicit reason.

The validator rejects confirmed HOME without an accepted source, exact member mapping, source claim, and matching canonical root. It rejects no-safe-evidence without an actual researched source and finding; conflicts without two validated roots; and any attempt to place a baseline-confirmed Character in the unresolved cohort. A complete run requires exactly 13,983 accounted rows and zero `UNRESEARCHED`.

## Execution order

1. Re-audit accepted source scopes against all currently `UNRESEARCHED` cohort rows; generate exact roster/catalog mapping candidates and accept only reviewed unique mappings.
2. Rebuild the full-cohort Copyright-root priority queue from candidate-root/family hints, existing hints, reviewed source-scope inventories, and frozen frequency ranks. `expected_safe_yield` counts only open `AUTO_MAPPING_CANDIDATE` rows in a retained inventory whose accepted source ID, URL, and exact scope still match the registry. Merely having a source under the same root never makes all root members expected yield. Queue fields are work-priority metadata only; they never enter HOME evidence.
3. Review high expected-safe-yield official rosters/directories first. Record one authority source with an explicit exact scope and a batch of exact/reviewed member mappings. Reuse the same URL/scope and member table instead of repeating Character-level lookups.
4. Use Top500 and Top2000 as progress cross-checks of root/source batches, not as a sequential Character work queue. Counts affect priority only.
5. Send authority-reviewed no-safe-evidence, policy-ineligible, identity-unresolved and conflicting cases to their explicit terminal states. Continue long-tail root/source batches and individual research only where no safe roster batch covers the identity.
6. Reconcile all 13,983 rows and stop only when the validator reports `complete: true`.

The source-yield queue records each root's unresolved and Top500/Top2000 counts, post-count sum/max, known official and reusable accepted sources, reviewed source counts, existing exact mappings, exact open candidates, review-required candidates, remaining unmapped rows, and `expected_safe_yield`. The estimate is bounded to unique exact candidates from reviewed scopes; it is not guaranteed coverage and is never evidence. A source can cover only exact listed members inside its recorded scope. Candidate generation uses exact normalized catalog names and accepted exact member mappings; qualifier-bearing alias head matches remain `REVIEW_REQUIRED`, while collisions and missing matches require manual identity disposition and missing matches remain `NO_MATCH`.

Each checkpoint is a deterministic snapshot of cohort size, state counts, source count/reuse, and the cohort hash. A checkpoint never changes the completion rule.

## Initial coverage checkpoint

The full 13,983-row cohort was frozen from the local ignored #180 master after verifying its exact expected SHA-256. The generated `AUTHORITY_COVERAGE_COHORT_V1.json` records that provenance. The initial decision ledger was seeded with 13,983 `UNRESEARCHED` rows. Independent source revalidation and exact official-source review have added 52 `HOME_CONFIRMED` decisions across 20 official sources and 52 exact member mappings. The other 448 Top500 members and 13,483 remaining cohort members are still `UNRESEARCHED`; this is an incomplete checkpoint, not a completion claim.

The root catalog was corrected from the 1,672 roots used by confirmed #180 HOME rows to the complete 8,536 canonical Copyright rows in `docs/issue70/data/runtime/issue70_catalog_overlay.csv`. The complete source file SHA-256 is `1d346ad75655ea6091f9bce9a4cf58b1cf6f8fac18c7eb441f8edd009ee81433`. `freeze_copyright_root_catalog.py --check` verifies its hash, 92,739-row population, unique category-3 roots, and deterministic output. Candidate roots still do not constitute authority evidence.

The source master remains a protected ignored artifact and is not copied into this branch. Reproducing the freeze from a clean checkout requires the exact #180 master artifact to be made available as a read-only input. The Top500 snapshot is not a substitute.
