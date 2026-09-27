# Issue #132 Pass B/C reconciliation summary

- Research semantic HEAD: `d74352be827c52a24888fbfc8bf71b8982627130`
- Live main HEAD: `e5d0f7d954ff491c1a5661a0652e6142f2b0d08d`
- Pass B population: **31,003 / 31,003**
- Product candidate gate: already-browseable identities only; existing route IDs only; no quota.
- Sexual lens uses #118 SEXUAL + CONTEXTUAL, matching current app behavior. GeneralPurpose uses NON_SEXUAL + CONTEXTUAL.

## Pass B flags

Counts are nonexclusive identity flags; a row can carry several flags.

| Flag | Identities |
|---|---:|
| COVERED | 15,632 |
| CURRENT_ROUTE_NOT_REPRODUCED | 7,720 |
| MISSING_BODY_FACET | 382 |
| MISSING_CORE_ROUTE | 6,306 |
| MISSING_LOCAL_REFINEMENT | 6,250 |
| MISSING_SUPPORTING_ROUTE | 2,713 |
| MISSING_THEME_FACET | 127 |
| ROUTE_VOCABULARY_GAP | 26 |
| SEARCH_ORIENTED | 3,187 |
| SEMANTIC_UNRESOLVED | 378 |

## Pass C dispositions

| Disposition | Identities |
|---|---:|
| ADD_SECONDARY_CANDIDATE | 273 |
| SEARCH_ONLY | 17,145 |
| SEMANTIC_UNRESOLVED | 378 |
| UPSTREAM_REVIEW | 13,207 |

ADD_SECONDARY candidate pairs: **274** across **273** identities.
- CORE: 148; SUPPORTING: 126.
- Sexual-lens: 154; GeneralPurpose-lens: 179.
- UPSTREAM_REVIEW: 13,207 identities; SEARCH_ONLY: 17,145; SEMANTIC_UNRESOLVED: 378.
- General-only missing facets: body 252 identities/257 assignments; theme 113 identities/113 assignments.
- These facet findings are a separate architecture report. Candidate rows contain only existing route membership pairs; independent identity overlap is body 27, theme 2. Missing facets never enter candidate route decisions.

The systemic report and all 19 route before/after counts are in this directory. Runtime cost estimate: 274 static route memberships (about 0.81% of 33,688 catalog backing rows) through the existing index, with no query-time work. Actual build, memory, and latency cost remains unmeasured and is a pre-promotion gate.
