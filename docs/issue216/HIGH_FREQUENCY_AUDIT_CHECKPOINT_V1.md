# Issue #216 High-frequency HOME_UNRESOLVED audit checkpoint

## Scope and immutable baseline

This is a separate, additive audit of the highest-frequency unresolved Characters. It does not edit or supersede Issue #180 evidence, source ledgers, HOME decisions, or production behavior.

- Issue #180 authority commit: `9c0db59c0f1dc56402c955e718a37d9de1849d7e`
- Issue #180 Character HOME master SHA256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`
- Baseline: 35,890 Characters; 21,907 HOME_CONFIRMED; 13,983 HOME_UNRESOLVED; OPEN Research Units 0; missing roots 0; HOME cardinality 0..1.
- Frequency source: Issue #70 extraction snapshot dated 2026-09-02. `character_post_count` is used only to rank review effort and is never HOME evidence.
- Joined 13,881 of 13,983 unresolved Characters; 102 had no count in the snapshot. Cohort order is post count descending, then canonical Character ascending. Rank 100 cutoff: 3,253 posts. Rank 500 cutoff: 1,007 posts.

## Audit method

The frozen 500-member cohort is `TOP500_COHORT_V1.csv`. `TOP500_RESEARCH_UNIT_LINKAGE_V1.csv` records the exact Issue #180 Research Unit IDs, `member_ids_sha256`, and terminal states as frozen review context. Candidate roots and source-review IDs remain hints; they do not by themselves establish HOME.

All 500 rows received a deterministic review of their baseline state/reason, candidate hints, existing relation/source-review pointers, and linked Research Unit terminal record. Bounded first-party source checks were then made for 19 high-frequency Characters: 17 from ranks 1–100 and two additional obvious cases at ranks 117 and 200. The other 481 were not externally researched in this pass and remain explicitly marked unresolved in the audit ledger. No proposal in this report changes the Issue #180 master.

## Results

- 19 exact-member first-party source checks support proposed HOME values under existing Issue #180 criteria.
- 481/500 have no proposed HOME and remain HOME_UNRESOLVED in this audit layer.
- Proposed HOME counts: `limbus_company` 7; `bang_dream!` 3; `resident_evil` 2; `neon_genesis_evangelion`, `sousou_no_frieren`, `spy_x_family`, `metroid`, `spice_and_wolf`, `urusei_yatsura`, and `persona` 1 each.
- Examples in the top 100 include Asuka Langley (rank 5), Frieren (6), Yor Briar (10), Samus Aran (22), and seven exact Limbus Company Sinners (ranks 27–83). Official roster/profile pages were checked for exact members.
- Additional checked rows: Aigis (rank 117) and Ada Wong (rank 200).
- Important safe unresolved cases remain: Chen (rank 1) has no accessible exact member text in the checked official roster, and Kasane Teto (rank 3) is presented by her official source across multiple voice-synthesis products without an established unique Copyright HOME. Neither was assigned from a candidate hint or popularity.

The useful finding is that the top-frequency tail does contain well-known Characters with exact first-party evidence that was not present in the frozen #180 result. This supports a small, source-reviewed additive rescue pass before production. It does not justify reopening all 13,983 unresolved Characters. Searchability for the rest remains an appropriate Picker behavior.

## Files and checks

- `TOP500_COHORT_V1.csv` and `.json`: deterministic cohort and source provenance.
- `TOP500_RESEARCH_UNIT_LINKAGE_V1.csv`: exact v3 Research Unit linkage and member fingerprints.
- `HIGH_FREQUENCY_RESCUE_LEDGER_V1.csv`: 500 per-Character outcomes, source claims, and explicit researched/unresearched distinction.
- `scripts/issue216/freeze_top500_cohort_v1.py`: reproducible cohort freezer/checker.
- `scripts/issue216/build_review_ledger_v1.py`: writes the independent review ledger from frozen cohort/linkage inputs.
- `tests/issue216/test_review_ledger.py`: schema, cohort cardinality/order, exact fingerprint formatting, and researched/unresearched coverage checks.

Validation run:

- `python scripts/issue216/freeze_top500_cohort_v1.py --check` — PASS.
- `python scripts/issue216/build_review_ledger_v1.py` — PASS (deterministic rebuild matches frozen ledger).
- `python -m unittest tests.issue216.test_review_ledger -v` — PASS (4 tests).
- `git diff --check` — PASS.
- Baseline master SHA256 rechecked against the requested value — PASS.

No Issue #180 source, evidence, migration, or production file was changed. No HOME semantics or evidence thresholds were changed. This is not a claim that all 500 were externally researched or approved for Issue #180 integration; the 19 proposals need ordinary source-review/evidence-ledger acceptance before any future integration.
