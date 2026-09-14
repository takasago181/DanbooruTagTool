# Issue #70 translation automation

Status: active design/automation authority for the long-running Character/Copyright/Artist Japanese overlay work.

## Scope

Target population from the fixed 2026-09-02 canonical dictionary:

- Character: 35,890
- Copyright: 8,536
- Artist: 48,313
- Total: 92,739

Batch 001 (`I70-000001`..`I70-001000`) has already been manually piloted in ChatGPT. The remaining work is processed by four independent automation lanes. Each lane may process at most four assigned 500-row chunks (2,000 rows) per run.

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
- `docs/issue70/data/source_chunks/` — deterministic 500-row slices of the translation source
- `docs/issue70/data/results/lane1/` .. `lane4/` — compact result files
- `docs/issue70/data/progress_lane1.json` .. `progress_lane4.json` — independent lane checkpoints
- `docs/issue70/data/final_completion.json` — written only after all four lanes are complete and coverage audit passes

`docs/issue70/data/progress.json` is the bootstrap/pilot checkpoint only. After the four-lane mode starts, scheduled lanes must not modify it.

Large source/evidence files are provenance/recovery assets. Automation reads the 500-row chunks rather than the whole master CSV.

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

## Four-lane assignment

Source chunks are numbered starting at 1. Chunks 1 and 2 are already covered by the manual Batch 001 pilot. Scheduled work starts at chunk 3.

A source chunk belongs to exactly one lane by this rule:

- Lane 1: `chunk_index % 4 == 3`  → 3, 7, 11, 15, ...
- Lane 2: `chunk_index % 4 == 0`  → 4, 8, 12, 16, ...
- Lane 3: `chunk_index % 4 == 1`  → 5, 9, 13, 17, ...
- Lane 4: `chunk_index % 4 == 2`  → 6, 10, 14, 18, ...

The rule is immutable for this run. A lane must never process a chunk assigned to another lane.

Each lane may process at most four of its own unfinished chunks in one scheduled run, so each lane handles at most 2,000 rows per run. The four lanes together can therefore process at most 8,000 rows per hourly cycle.

## Non-interference rules

The four lanes must remain independent:

1. each lane writes only under its own `results/laneN/` directory;
2. each lane writes only its own `progress_laneN.json`;
3. no lane modifies another lane's result or progress files;
4. no scheduled lane modifies the bootstrap `progress.json`;
5. result filenames include lane and source chunk index, so paths cannot collide;
6. every run restores live main before work and re-checks its assigned source chunk hashes/row identities;
7. commits go directly to main only after re-reading current main; if a non-fast-forward/write conflict occurs, the lane must stop and retry on its next scheduled run rather than force-push or overwrite;
8. scheduled lanes are intentionally time-staggered within the hour to reduce GitHub main push races while still providing four runs per hour.

## Result shape

Result rows contain only the compact canonical overlay fields needed for the final merge:

- `row_id`
- `canonical_tag`
- `category`
- `display_ja`
- `search_ja`
- `translation_status`
- `translation_note`

Do not duplicate `post_count`, verified alias data, or full relation evidence into the final Japanese master; those remain separate authorities.

## Lane checkpoint rules

For each successful lane run:

1. validate the source chunk manifest SHA and expected row IDs/canonicals;
2. validate that every chunk belongs to that lane;
3. skip any chunk that already has a valid accepted result for that lane;
4. write one compact result CSV per source chunk;
5. update only `progress_laneN.json` with completed chunk indices, processed rows, status totals, review queue, result paths, and source/result hashes;
6. commit the lane result/checkpoint together;
7. never overwrite previously accepted rows because model behavior changes later.

If a source chunk is missing, hashes/row identity disagree, GitHub main changes underneath the write, or lane progress is inconsistent, stop that run instead of guessing.

## Completion audit

Lane 4 additionally checks completion state after its normal lane work. Only when all four lane progress files report no remaining assigned chunks may it perform the final coverage audit.

The final audit must verify:

- manual Batch 001 covers rows 1..1,000 exactly;
- the four lanes together cover every source chunk from 3 through the final chunk exactly once;
- no duplicate `row_id` or `canonical_tag` result identity exists;
- result canonical identities match the source chunks;
- total result coverage equals 92,739 rows;
- unresolved rows exist only as explicit `REVIEW_REQUIRED` (or another explicitly documented non-accepted status), never as silently missing rows.

If all checks pass, write `docs/issue70/data/final_completion.json` and report completion. If any check fails, do not mark completion; report the exact gap/conflict for repair.
