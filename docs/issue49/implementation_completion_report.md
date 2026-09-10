# Issue #49 implementation completion report

## Verdict

`READY_FOR_POST_WRITE_AUDIT`

This branch applies only the effective audited Issue #32 candidate assignments to
`data/generation/special2788_generation_profile.csv`. Main merge, Stage 10, and
Issue #36 Japanese-overlay promotion remain prohibited.

## Source and base

- Issue: #49
- Production base: `origin/main` at `0be096644086101772340ee7ccf519de63139743`
- Read-only quarantine ref: `origin/dict-validation/quarantine` at `f476ce5578afa77bf754541d29efa6f55a048d12`
- Candidate inputs: 36 files consisting of `validation_quarantine/candidate_fixes.csv` and the singular `validation_quarantine/candidate_fix_blocks/*.csv`
- No protected raw dataset was added to Git

## Candidate accounting

| Check | Result |
|---|---:|
| Special source rows | 2,788 |
| Production profile rows / unique identities | 2,788 / 2,788 |
| Candidate source active rows | 228 |
| Candidate source active field assignments | 259 |
| Candidate source excluded rows / fields | 4 / 4 |
| Non-effective field assignments parked | 13 |
| Effective field assignments | 246 |
| Affected Specials | 171 |
| Conflicting effective assignments | 0 |
| Target Specials exactly once | 171 |

The 13 parked assignments are Special IDs 779 (provisional/audit-only), 738
(staged family/rule mismatch), and 1007 (staged family/rule mismatch). The four
withdrawn candidate rows and all superseded/history/non-effective statuses are
excluded. The five rejected completeness candidates are not present.

## Production result

- Changed production file: `data/generation/special2788_generation_profile.csv`
- Production diff: 171 rows changed, 246 cells changed
- Before SHA-256: `3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835`
- After SHA-256: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`
- Identity, row count, and fixed order are unchanged
- Every changed cell is recorded in `applied_diff_report.json` with candidate source path/line, reason, and evidence references
- No non-candidate field changed; Special-level application was built and validated atomically before the single file replacement

The implementation does not modify canonical/alias/Japanese/search/ranking/
Prompt composer code or data, Japanese overlay data, semantic data, or model
observations. Semantic parked items remain untouched and model-scoped claims
are not flattened into global truth.

## Durable evidence

- `effective_candidate_manifest.json`: deterministic source, filtering, conflict, and pre-write accounting
- `applied_diff_report.json`: exact applied cells and post-write invariants
- `protected_data_integrity.json`: before/after hashes for integrity-coupled protected files
- `test_results.md`: commands and results
- `ROLLBACK.md`: rollback procedure

The implementation intentionally stops before the separate post-write audit.
