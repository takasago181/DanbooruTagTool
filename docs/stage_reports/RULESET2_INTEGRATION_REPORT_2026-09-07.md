# Ruleset2 Dictionary/Search/Model-Aux Integration Handoff — 2026-09-07

## Result

The accepted Ruleset2 checkpoint was integrated as an audited derived overlay. The
historical source under `data/source/` and `data/special2788/` was not overwritten.

- Ruleset2 loader/integrity gate: PASS
- relevant Stage3/4/6/7/8 tests: 175 passed
- full pytest suite: 204 passed
- package validators 90/91: PASS
- Stage8C deterministic rebuild comparison: PASS, 16/16 byte-identical
- runtime external/network calls: 0
- model-aux FINAL evidence sub-gate: NOT COMPLETE (required local source exports absent)
- Pilot001 acceptance: NOT COMPLETE
- Stage9: NOT STARTED
- Stage10: NOT STARTED
- production applied: false

## 1. Changed files

Modified:

- `PACKAGE_MANIFEST.json`
- `requirements-dev.txt`
- `danbooru_tag_tool/knowledge.py`
- `danbooru_tag_tool/models.py`
- `danbooru_tag_tool/prompt_session.py`
- `danbooru_tag_tool/search.py`
- `danbooru_tag_tool/stage7a_session.py`
- `danbooru_tag_tool/stage7a_warnings.py`
- `tests/test_generation_profile.py`

New implementation/test files:

- `danbooru_tag_tool/ruleset2.py`
- `tools/model_aux_crossmatch.py`
- `tests/test_ruleset2_integration.py`
- `data/derived/ruleset2/RULESET2_MANIFEST.json`
- seven accepted CSV authorities under `data/derived/ruleset2/`
- ten authority/reference documents under `docs/ruleset2/`
- this report

Generated handoff copies and ZIP are listed in `HANDOFF_MANIFEST.md`; they are not
runtime inputs.

## 2. Implementation

### Source-preserving Ruleset2 overlay

`TagKnowledgeCore.load()` first validates the protected historical Special/linkage
pair, then loads Ruleset2. Startup rejects a changed candidate hash, changed source
ID+Tag identity, invalid search derivation, incomplete Alias/Semantic coverage,
invalid migration provenance, or a stage-gate change.

The active candidate is exactly 2,788 rows with SHA-256
`12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02`.
Its source ID+Tag identity SHA-256 is
`b2f126ae9d49493034245fe006aad8eceb12eb2bf08a45160995b8da10b07763`.

Ruleset2 Japanese gloss, curated category/scope metadata, dictionary count display
metadata, and deterministic search keys are exposed on `SpecialTag`. Dictionary
counts remain display/search metadata and do not replace Stage6 runtime counts.

### Alias two-axis authority

All 778 Alias rows load from separate semantic and statistics authorities:

- full default semantic statistics: 496
- non-default/related/context/manual/disallowed: 282

The 282 non-default rows no longer enter the default AND statistics core. Their
curated target remains inspectable related evidence. Prompt output continues to use
the original Special term; every Alias policy has automatic replacement `NEVER`.
Legacy 04/05 files were not copied into the active overlay and are not runtime
authorities.

The previous test for ID1578 (`descensored`) was updated because Ruleset2 explicitly
classifies its `uncensored` target as curated/ambiguous and not eligible for default
full-semantic statistics. The test still freezes original Prompt output.

### Semantic336 typed routing

All 336 typed routes are loaded separately from the existing semantic bridge.
Search results expose subtype, anchor kind/value, and Prompt mode as audit metadata.
An auxiliary/search anchor is not written into `candidate_canonical`, so no fake
canonical, count, co-occurrence, or silent Prompt owner is created.

### Model-aux source handling

The supplied canonical local/offline crossmatch implementation was copied byte-for-
byte as `tools/model_aux_crossmatch.py`. It enforces same-date canonical e621 raw
filenames, e621 provenance URLs, published/local SHA equality, alias status safety,
the frozen Gelbooru hash/row gate, deterministic output, and blank model
recommendation fields when evidence is only source-vocabulary presence.

## 3. Tests executed

Python used:
`C:/Users/takas/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`

Commands:

```text
python -m pytest -q -p no:cacheprovider tests/test_ruleset2_integration.py tests/test_stage3_knowledge.py tests/test_stage4_search.py tests/test_generation_profile.py tests/test_stage6_recommendations.py tests/test_stage7a_ui.py tests/test_stage7b_recommendations.py tests/test_stage8a_semantics.py tests/test_stage8b_support.py tests/test_stage8c_phase0.py
python -m pytest -q -p no:cacheprovider
python _handoff/.../TOOLS/90_validate_current_snapshot.py
python _handoff/.../TOOLS/91_independent_snapshot_check.py
python _handoff/.../TOOLS/18_test_model_aux_crossmatch.py
python tools/verify_stage8c_determinism.py
```

The supplied model-aux fixture initially failed because it expects the 2811-term CSV
beside the script although the ZIP stores it under `WORKING_TREE`. After copying that
input inside the extracted temporary package only, the unmodified fixture passed.
The integrated pytest uses the repository authority path directly.

## 4. PASS / FAIL

- Relevant suite final: PASS — 175 passed
- Full suite final: PASS — 204 passed in 29.44s
- Validator 90: PASS_CURRENT_SNAPSHOT_STRUCTURAL_AND_POLICY_VALIDATION
- Validator 91: PASS
- Model-aux canonical fixture: PASS after the ZIP-local path workaround above
- Determinism: PASS — two runs, 16 files, all byte-identical
- Protected Stage8B hashes: PASS
- Source ID+Tag equality: PASS
- Candidate/Alias/Semantic row counts: PASS — 2788/778/336
- Model-aux FINAL source-evidence gate: NOT RUN / NOT COMPLETE, not reported as PASS

## 5. Unresolved matters

No required code/test failure remains. The model-aux FINAL sub-gate cannot run until
all canonical evidence is locally available:

- same-date `tags-YYYY-MM-DD.csv.gz`
- same-date `tag_aliases-YYYY-MM-DD.csv.gz`
- their published SHA-256 values and absolute e621 provenance URLs
- frozen `gelbooru_tags_2026-06-11.parquet` with expected SHA/row count

No network retrieval was attempted and no success was fabricated.

The extracted staging copy remains at
`C:/Codex/DanbooruTagTool/_handoff/RULESET2_INCOMING_TMP/`. An attempted cleanup was
rejected by the safety reviewer because the directory contains the supplied handoff
source material. It is excluded from runtime inputs and from the audit ZIP.

## 6. Working tree state

This supplied repository directory contains no `.git` metadata. Consequently,
`git status` returns “not a git repository”; status is reported by the explicit
modified/new lists above and comparisons against the backup copies.
The working directory additionally contains the excluded staging copy named above.

Protected hashes after integration:

- `data/source/danbooru-2026-09-02.csv`: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`
- historical Special CSV: `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
- Stage8B Special support: `c243bc4bd7549d70548283865c5c9b5e3484f1835bfc1b05f740c7e9ca845910`
- Stage8B family rules: `07b1cd98195316bf8b2b6eec53e0bef19a7437cbb7ee54d8e68f6016a389d80b`
- Stage8B support code: `83f5617a36d48dfb730e21e2ac2957c8e4f6c00857b0971f6af6724f4e105dd2`
- UI: `5c83f6ca7dae2f164403cb13d3112a8ad85a8f201de351354c980daf31f98450`

## 7. Independently audit next

ChatGPT should independently verify:

1. `data/special2788/` and source ID+Tag identity stayed unchanged.
2. Alias semantic and statistics authorities remain independent and legacy 04/05
   do not control runtime behavior.
3. Non-default Alias statistics are blocked from default AND while original Special
   Prompt ownership is preserved.
4. Semantic typed anchors remain metadata and are not fake canonicals.
5. Stage6 raw artifacts/results and all Stage7/8/Pilot-related frozen files remain
   unchanged except the explicitly updated obsolete ID1578 test expectation.
6. The missing external-source evidence remains an open FINAL sub-gate.
7. Pilot001, Stage9, Stage10, and production flags remain unopened.

## 8. Explicitly unchanged

- Ruleset2 Candidate contents
- `data/source/` and `data/special2788/`
- protected Stage3 linkage and semantic bridge snapshots
- Stage6 raw evidence and recommendation implementation
- Stage7 UI implementation
- Stage8B production relations
- Stage8C Phase0/Pilot001 ledgers and acceptance expectations
- LoRA/Practical/model-form semantic ownership
- runtime offline/non-LLM policy

Backup location: `C:/Codex/DanbooruTagTool/backups/ruleset2_integration_20260907_2005/`
