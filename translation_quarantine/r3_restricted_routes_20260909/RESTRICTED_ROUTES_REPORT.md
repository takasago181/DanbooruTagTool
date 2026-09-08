# Issue #36 R3 restricted-route audit

Campaign: `issue36-r3-restricted-routes-20260909-v1`

Input is the frozen 556-row REVIEW remainder from `714029f4596169e82c4dbec2bb81ce525177792c`.
The previous READY48 was not used as a teacher. All outputs are quarantine-only.

## Final state

- READY / REVIEW / CONTRADICTION: **47 / 557 / 0**
- Evaluated 556-row batch: **0 / 556 / 0**
- New READY canonicals: **none**
- Risk READY: `CRITICAL=1`, `MEDIUM=1`, `LOW=45`
- false READY: **0**
- deterministic replay: **PASS**
- verifier: **PASS**
- production_modified: **false**

The focused re-audit parks the prior `uncensored` READY row because `無修正を示す語` is an explanatory phrase rather than a safe display wording. Its exact semantic scope remains valid; wording/search readiness does not.

## Route counts

| Route | Processed | Result |
|---|---:|---|
| semantic-scope acquisition | 556 | 105 prior frozen scopes; 121 exact-title wiki captures parked for proposition review; 330 unavailable/rate-limited |
| wording-only | 556 | 105 eligible; 0 safe; 75 without candidate; 24 multiple candidates; 6 narrowing/broadening/ambiguous |
| minimal search-term | 556 | 0 accepted; 556 parked before search because display wording was not established |

The exact-canonical external evidence is frozen in `wiki_evidence.jsonl` with URL, page ID/update revision, and content identity. The 121 captured pages are not treated as READY until actor/target/body-site/direction/count/relation/action-state propositions are independently reviewed. HTTP 429 captures are retained as acquisition failures, not semantic evidence.

## Evidence source counts

- `pinned_candidate_queue`: 556
- `danbooru_exact_canonical_wiki`: 556 route records (148 HTTP 200 exact-title; 408 HTTP 429)
- `prior_frozen_semantic_scope`: 105
- `local_overlay_wording_candidate`: 78 candidate terms; none accepted

## Residual REVIEW / park reasons

- `NO_SAFE_SEARCH_CANDIDATE`: 556
- `SEMANTIC_SCOPE_NOT_ESTABLISHED`: 451
- `SEMANTIC_PROPOSITION_REVIEW_REQUIRED`: 121
- `AUTHORITATIVE_SCOPE_UNAVAILABLE`: 330
- `NO_SUPPORTED_DISPLAY_CANDIDATE`: 75
- `MULTIPLE_CANDIDATES`: 24
- `NARROWING_OR_BROADENING_OR_AMBIGUOUS`: 6
- focused `uncensored`: `UNNATURAL_EXPLANATORY_WORDING`, `DISPLAY_WORDING_NOT_ESTABLISHED`

## Bridge and boundaries

- #32 v2 bridge: **READY 7/7**, content identity `sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5`
- contradiction guard: **0**
- protected boundary changed: **false**
- promotion: **NOT_AUTHORIZED**
- Stage10 production A/B: **not started**

Per-row route decisions and frozen sources are in `route_rows.jsonl`, `semantic_scope_routes.jsonl`, `wording_routes.jsonl`, `search_term_routes.jsonl`, `route_evidence.jsonl`, and `wiki_evidence.jsonl`.
