# Issue #70 translation automation

Status: active design/automation authority for the long-running Character/Copyright/Artist Japanese overlay work.

## Scope

Target population from the fixed 2026-09-02 canonical dictionary:

- Character: 35,890
- Copyright: 8,536
- Artist: 48,313
- Total: 92,739

Batch 001 (`I70-000001`..`I70-001000`) has already been manually piloted in ChatGPT. The remaining work should be processed in roughly 2,000 rows per automation run while keeping smaller source/result files for reliable GitHub I/O.

## Source identity

The local bootstrap pack must preserve these fixed source identities:

- `data/source/danbooru-2026-09-02.csv`
  - SHA-256 `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`
- `data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv`
  - SHA-256 `3f942704a10bb342ae7368024337849d392d54745061cf9259e51b9f6080a394`
- fixed post snapshot used only to derive Character/Copyright evidence:
  - `data/runtime_source/posts-snapshot-ebb02a630201c7b51487e45fb90b3fcf4cbedc20.parquet`
  - SHA-256 `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd`

The multi-GB Parquet/runtime index stays local. Compact #70 inputs/evidence derived from it are preserved in GitHub.

## GitHub data layout

Bootstrap should populate:

- `docs/issue70/data/source/issue70_translation_source_with_relations.csv`
- `docs/issue70/data/source/character_copyright_top5.csv`
- `docs/issue70/data/source/character_copyright_extraction_summary.json`
- `docs/issue70/data/source/character_copyright_unresolved_source_tags.csv`
- `docs/issue70/data/source/character_copyright_evidence_full.csv.gz`
- `docs/issue70/data/source_chunks/` — deterministic 500-row slices of the translation source for automation reads
- `docs/issue70/data/results/` — compact accepted/review translation results
- `docs/issue70/data/progress.json` — resumable progress authority

Large source/evidence files are provenance/recovery assets. Automation should read the 500-row chunks rather than the whole 20+ MB master CSV.

## Translation policy

The task is dictionary curation, not blind machine translation.

- Preserve `canonical_tag` exactly.
- Character: prefer the established Japanese character name. Use Copyright context and verified aliases as evidence. Do not adopt Chinese-only/fan translation candidates merely because they exist.
- Copyright: prefer the established official/common Japanese series/title name. Keep useful romanization/abbreviation in search terms where appropriate.
- Artist: do not meaning-translate handles. Prefer the creator's actual Japanese/native name when reliable; otherwise keep the original handle as display and add only reliable Japanese reading/search terms.
- Existing Japanese `search`/`candidate` terms are evidence, not authority.
- Character/Copyright post co-occurrence is evidence, not semantic identity. It may help disambiguation but must not silently become an official relation.
- Ambiguous/uncertain rows become `REVIEW_REQUIRED`; do not invent a confident answer.
- Accepted rows are immutable unless a later explicit correction is recorded.
- Runtime remains local/non-LLM.

## Automation unit

Each scheduled run should process at most 2,000 next-unfinished rows. It may read four 500-row source chunks and write compact 500-row result files so GitHub connector/file operations remain manageable.

Result rows should contain only the compact canonical overlay fields needed for the final merge, e.g.:

- `row_id`
- `canonical_tag`
- `category`
- `display_ja`
- `search_ja`
- `translation_status`
- `translation_note`

Do not duplicate `post_count`, verified alias data, or full relation evidence into the final Japanese master; those remain separate authorities.

## Checkpoint rules

After each successful run:

1. validate that source row IDs/canonicals match the expected chunk(s);
2. write result file(s);
3. update `docs/issue70/data/progress.json` atomically in the same GitHub work unit;
4. commit the result/checkpoint;
5. never overwrite previously accepted rows simply because model behavior changes later.

If a source chunk is missing, hashes/row identity disagree, or progress is inconsistent, stop that run instead of guessing.
