# Issue #36 full accepted-quality + fallback reconciliation

- Handoff: `5599963638`; execution start HEAD: `bd111c5052203aacd74753c4a057893d2f5e79a8`.
- Fixed source: `1f069d050909425dbcc5c2965951fd0c920a2205`; contract: `translation_quarantine/r3/ISSUE36_FULL_ACCEPTED_AND_FALLBACK_RECONCILIATION_CONTRACT.md` at `0f0cdd8657aeb03ee13cf1968fb86980fe4f604e`.
- Accepted rows screened: **27743**; repaired **22**, demoted **4549**, revalidated **23172**.
- Fallback rows revisited: **2886**; phrase-semantic homework revisited: **1677**, resolved: **0**.
- Final table: **30629 unique canonicals**; accepted **23194**; fallback **7435**.
- Japanese display coverage: **23194/30629 (75.73%)**; search: **23194/30629 (75.73%)**.
- Fallback reasons: `{'CODE_OR_PRODUCT_IDENTIFIER': 98, 'MALFORMED_LABEL': 2, 'NON_JAPANESE_LABEL': 444, 'OPAQUE_SOURCE_STRING': 70, 'PHRASE_SEMANTICS_UNRESOLVED': 1677, 'PRODUCT_OR_SERVICE_NAME': 68, 'PROPER_NAME_OR_QUALIFIED_LABEL': 897, 'RAW_ENGLISH_SEMANTIC_CORE': 4103, 'SYMBOL_OR_EMOTICON': 76}`.
- Accepted-quality gate: PASS; Chinese/non-Japanese, raw semantic English, malformed labels, and known semantic-scope fixtures are repaired or explicit fallback.
- Language screen uses strong simplified-only characters and canonical-aware token checks; it does not blanket-reject CJK or ASCII.
- Multiword token composition: NOT USED; unresolved phrase semantics remain explicit homework fallbacks.
- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`; promotion: `NOT_AUTHORIZED`.

## Artifacts

- All required evidence is under `translation_quarantine/full_accepted_quality_sweep_20260909/`.
- `candidate_screen.jsonl` covers every accepted source row; `accepted_revalidation.jsonl` covers every accepted decision; `fallback_reconciliation.jsonl` covers every fallback.
- `final_translation_table.csv` and `.md` contain the merged 30,629-row result.

## Boundaries

Only `translation_quarantine/**` and the focused test are in scope. Production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B remain untouched.
