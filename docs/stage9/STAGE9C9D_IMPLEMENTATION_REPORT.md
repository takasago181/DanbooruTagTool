# Stage9C/9D DEV correction implementation report

Current DEV: Issue #17; CURRENT_STATE and CURRENT_DEV_TASK Source agree.
Date: 2026-09-08. Branch: `codex/stage9c9d-completion`.
Latest main incorporated: `9c85f9f160a5549153d8c0cff232dba44ccc06f2`.
This corrects the pre-gate return against `99b4f4a80c12f15dfcc3e62f608af6a2c1cccf88`.
Status: corrections prepared for DEV verification, NOT Issue #17 completion or #22 handoff.

## Stage9C candidate correction

- Recommendation receipt atomically registers common and rare before rendering either bucket. Rendering no longer replaces session candidates.
- Empty results clear candidates; single/empty buckets do not erase the other bucket. Duplicate canonical across buckets is represented once (common first).
- Existing semantic and true-AND adapters remain separate, with original statistics and snapshot evidence. No combined score or rank-based selection key.
- Add registers INCLUDE before refreshing preview. Semantic-only additions do not try to select a missing co-occurrence ID.
- Core changes clear stale candidates, late results for another core are ignored, stable user decisions survive. Removing an explicitly included auxiliary also excludes its statistical lane.

## Stage9D reversible contract (spec Section 10)

- Special position: existing model-scoped ComposerProfile.special_slot_position.
- Broad generic: caller supplies ordered canonical inputs and selects count 0, 1, or 2. No support vocabulary or preferred count is fixed.
- Role density: named, explicitly classified input sets; no text-to-role inference or automatic density threshold.
- Weight: explicit canonical, finite positive metadata, and caller-supplied rendering under a non-GENERIC model-family profile. Neutral default has no weight. No shared weight grammar is generated.
- LoRA: separately addressable LORA inputs; contraction removes only explicitly named non-LoRA input IDs for that variant. Enabling LoRA alone removes nothing.
- Comparison metadata: immutable variant carries frontend/runtime metadata; comparison_snapshot returns the variant together with the actual ComposeResult, blocks and flattened Prompt/provenance. Switching back restores baseline without mutating manual selections.
- Weighted final atoms, blocks, flattened output and provenance use the same explicit render text. Candidate evidence remains unchanged; invalid or colliding weight targets fail rather than cache a partial result.

## Changed files in this correction

1. `danbooru_tag_tool/ui.py`
2. `danbooru_tag_tool/stage9c_session.py`
3. `tests/test_stage9c_session.py`
4. `tests/test_stage0_integrity.py`
5. `tests/test_stage8c_phase0.py`
6. `docs/stages/STAGE_10_PREP.md`
7. `docs/stage9/STAGE9C9D_IMPLEMENTATION_REPORT.md`

No new files in this correction. Earlier Stage9C/9D implementation remains in branch history.
Management mirror changes came from main, not reconstructed Issue text.
Recovery/review uses remote branch history; no protected local data was moved or copied into Git.

## Protected surfaces / Issue #26

- FILE_HASHES.json and PACKAGE_MANIFEST.json unchanged. All direct source files retain mandatory SHA256 and size verification.
- Only the known Special2788 prompt_reference directory is allowed. Exact manifest path-set equality also detects missing protected files; arbitrary directories/files are rejected.
- Added fixture-based rejection tests for missing files, changed size, same-size changed hash, unknown directory and unknown file, plus valid reference-directory acceptance.
- Source dictionaries, Special2788 originals, derived/runtime data, Stage8C authority CSVs, family rules, Ruleset2, SupportKnowledgeStore, recommendation metrics/index and Stage9A/B implementation are unchanged by this correction.
- UI is the intentional changed integration surface. Its explicit SHA256 is updated to `db061307f3029f6e4216804db9d03f23ce3cc74b4764d235084f6959347870f7` (Windows CRLF checkout). All other protected hash assertions remain intact.

## Verification

- `python -m pytest -q tests/test_stage9a_prompt_composer.py tests/test_stage9b_runtime.py tests/test_stage9c_session.py tests/test_stage0_integrity.py --basetemp .pytest-blockers-focused-0908-b`: 67 passed.
- Stage7A/B UI + Stage8A/B/C + Ruleset2 explicit regression selection: 99 passed.
- `python -m pytest -q --basetemp .pytest-blockers-final-0908-d`: **275 passed in 47.72s**, exit 0. Includes Stage0–8C, Stage9A/B/C/D and protected/hash checks; no skip or failure reported. Basetemp is workspace-local because the default temporary-directory permissions are unsuitable in this environment.
- `git diff --check`: PASS. No protected manifest/source/authority changes in this correction; the UI integration hash is the sole intentionally updated surface hash.
- The earlier report did not capture an exact full-suite completion result; it is superseded by this run, not treated as evidence.

## Limitations and DEV review points

- Tests invoke real UI result/add callbacks with mocked Tk rendering; no interactive desktop visual test or image generation was performed.
- Knobs are local Python/session comparison inputs, not a Stage10 experiment manager, persistence format, auto-runner, or added comparison-control UI.
- Contraction addresses explicit inputs, not automatic curated support or the Special core; it does not silently delete other lanes. Weight targets are canonical support atoms, not Special-owned render tokens. These guardrails preserve Special identity.
- Broad count measures requested explicit additions; canonical dedup may reduce final token count if callers choose overlapping tags.
- DEV should verify both bucket selection callbacks, decision persistence, exact variant restoration and rendered provenance, model-family isolation, and the deliberately changed UI hash versus unchanged authority/source hashes.
- Local full-suite evidence uses existing ignored protected data; a fresh GitHub checkout alone may not reproduce that environment.

## Exact stop

Stop after correction commit and remote push. DEV must inspect remote code/report/test evidence and record Issue #17 completion evidence before any #22 handoff. No audit request, Stage9 overall PASS, Stage10 A/B, winner/scoring logic, CFG change, or production Prompt-knowledge fixation has been performed.
