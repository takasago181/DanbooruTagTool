# Legacy Label Migration Map

Old research documents are not bulk-rewritten. This map tells a new reader how to interpret older mixed labels under the current Claim Registry schema.

| Old label / framing | New SOURCE_CLASS interpretation | New STATUS interpretation | New VALIDATION interpretation | Important note |
|---|---|---|---|---|
| `FACT_EXACT_MODEL` | usually `OFFICIAL_MODEL` or `AUTHOR_GUIDE` | often `ACCEPTED` for the narrow sourced fact | often `SOURCE_RECHECK_REQUIRED` | author recommendation is not automatically project optimum |
| `FACT_GENERAL` | `RESEARCH` or `OFFICIAL_RUNTIME` | usually `ACCEPTED` for the stated mechanism | `NOT_REQUIRED` or source recheck | exact checkpoint effect still needs a separate scoped claim |
| `CONTROLLED_PRACTICAL` | `CONTROLLED_PRACTICAL` | `ACCEPTED` only for demonstrated narrow result; otherwise `CANDIDATE` | often `CONTROLLED_TEST_REQUIRED` for generalization | one controlled case is not E3 |
| `PRACTICAL` | `COMMUNITY` or `CONTROLLED_PRACTICAL` depending controls | usually `CANDIDATE` | `CONTROLLED_TEST_REQUIRED` | exact settings/version completeness matters |
| `COMMUNITY` / `COMMUNITY_JA` | `COMMUNITY` | usually `CANDIDATE`; can support `HOLD`/failure discovery | `CONTROLLED_TEST_REQUIRED` or `SOURCE_RECHECK_REQUIRED` | language does not change evidence rank |
| `COMMUNITY_VALIDATED` | usually `CONTROLLED_PRACTICAL` if actual controls exist; otherwise `COMMUNITY` | claim-specific | claim-specific | do not infer validation from label text alone |
| `OFFICIAL_FACT` | `OFFICIAL_MODEL`, `AUTHOR_GUIDE`, `OFFICIAL_RUNTIME`, or `SEMANTIC_AUTHORITY` | claim-specific `ACCEPTED/CANDIDATE` | often `SOURCE_RECHECK_REQUIRED` | split “what source says” from “project optimality” |
| `PROJECT_HYPOTHESIS` | `PROJECT_FACT` only if it describes the existence of the hypothesis; evidence class may otherwise be research/practical | `CANDIDATE` or `HOLD` | `CONTROLLED_TEST_REQUIRED` / `STAGE10_REQUIRED` | never promote because it is project-relevant |
| `KEEP_CORE` | source class determined from original evidence | usually `ACCEPTED` | may still require source/local recheck | priority/adoption label, not evidence type |
| `MODEL_ONLY` | source class determined from original evidence | often `ACCEPTED` | source/local recheck as needed | must carry `FAMILY/MODEL_VERSION/PROFILE` scope |
| `DOWNGRADE` | often `LEGACY`, `COMMUNITY`, or lower-priority `PROJECT_FACT` | `HISTORICAL` or `CANDIDATE` | claim-specific | “lower priority” does not mean false |
| `TEST_REQUIRED` / `IMAGE_TEST_REQUIRED` | source class remains whatever evidence exists | `HOLD` or `CANDIDATE` | `CONTROLLED_TEST_REQUIRED` / `STAGE10_REQUIRED` | do not treat as an evidence source class |
| `HOLD` | source class remains claim-specific | `HOLD` | claim-specific | current unknown, not failure |
| `CONFLICT` | source class must be recorded per competing evidence | `CONFLICT` | source recheck and/or controlled test | preserve both sides |
| `REJECT` | usually `LEGACY` for the rejected formulation | `REJECTED` | `NOT_REQUIRED` unless re-opened | rejected statement stays visible |
| `OBSOLETE_AS_GOAL` | `LEGACY` | `HISTORICAL` | `NOT_REQUIRED` | historical fact may remain true but no longer leads current work |
| `MISSING` | no single source class | usually represented as a HOLD/CANDIDATE claim or HOLD-register entry | appropriate recheck/test | gap label, not a factual verdict |

## Non-1:1 rule

Never map one old label to one new STATUS without reading the claim.

Example:
`OFFICIAL_FACT`
- “author recommends Steps 15–30” -> `AUTHOR_GUIDE / ACCEPTED`
- “therefore Steps 25 is production-optimal” -> separate claim; not established by the same source

Current interpretation always comes from `CLAIM_REGISTRY.csv`.
