# Issue #180 authority batch schema v2

Forward output is source-level, not Character-level.

Each file under `docs/issue180/parallel/proposals-v2/fwd-N/` contains one object or an array of objects.

## AUTHORITY_BATCH

Required fields:

```json
{
  "schema_version": 2,
  "proposal_id": "ab2-unique-id",
  "campaign_key": "authority:example | base:example | direct:example",
  "campaign_fingerprint": "<sha256 from current campaign queue>",
  "worker_slot": 0,
  "batch_type": "AUTHORITY_BATCH",
  "source_url": "https://...",
  "source_claim": "What the checked page explicitly establishes.",
  "authority_type": "FIRST_PARTY_CHARACTER_ROSTER",
  "evidence_basis": "EXTERNAL_AUTHORITY",
  "relations": [],
  "terminal_reviews": [],
  "notes": ""
}
```

`relations` contains every exact relation safely proved by this source:

```json
{
  "subject_type": "Character",
  "subject_key": "example_character",
  "relation_type": "DIRECT_HOME",
  "object_type": "Copyright",
  "object_key": "example_work"
}
```

Allowed relation contracts:
- Character / DIRECT_HOME / Copyright
- Family / FAMILY_HOME / Copyright
- Character / MEMBER_OF / Family
- Character / VARIANT_OF / Character

A source batch may include exact covered Issue #180 Characters outside the original campaign when the same checked source explicitly proves them. QA handles deduplication/current-state applicability. An optional `source_review_id_hint` may name an ACCEPTED `SOURCE_REVIEW_LEDGER_V2.csv` row when Forward reused an approved source/mapping rule.

AUTHORITY_BATCH does **not** depend on canonical SHA, epoch ID, assignment ID or Research Unit fingerprint. `campaign_fingerprint` records which research lead produced the batch, but QA must not reject valid positive relations merely because that campaign fingerprint is no longer current. A real checked relation does not become false because another lane advanced canonical.

## TERMINAL_BATCH

Use only for a Forward-owned residual that was actually reviewed and remains unresolved.

```json
{
  "schema_version": 2,
  "proposal_id": "tb2-unique-id",
  "campaign_key": "direct:example",
  "campaign_fingerprint": "<sha256 from current campaign queue>",
  "worker_slot": 0,
  "batch_type": "TERMINAL_BATCH",
  "source_url": "",
  "source_claim": "",
  "authority_type": "",
  "evidence_basis": "",
  "relations": [],
  "terminal_reviews": [
    {
      "unit_id": "ru3-...",
      "member_ids_sha256": "<sha256>",
      "terminal_status": "NO_SAFE_EVIDENCE",
      "authority_source": "https://... or docs/issue180/...",
      "review_provenance": "What was checked and why no safe positive relation was established."
    }
  ],
  "notes": ""
}
```

Forward terminal statuses are limited to:
- PARTIALLY_RESOLVED
- NO_SAFE_EVIDENCE

POLICY_BLOCKED, IDENTITY_BLOCKED, STRUCTURAL_NO_SAFE_PATH and CONFLICT_REVIEW are QA-owned.

Terminal conclusions are valid only for the exact current unit fingerprint. QA rejects stale terminal items without invalidating unrelated positive evidence batches.

## RESEARCH_OUTCOME

Use this when one authority campaign was actually researched but produced no safe positive relation and the worker is **not** entitled to terminalize the whole source Research Unit.

```json
{
  "schema_version": 2,
  "proposal_id": "ro2-unique-id",
  "campaign_key": "direct:example",
  "campaign_fingerprint": "<sha256 from current campaign queue>",
  "worker_slot": 0,
  "batch_type": "RESEARCH_OUTCOME",
  "source_url": "",
  "source_claim": "",
  "authority_type": "",
  "evidence_basis": "",
  "relations": [],
  "terminal_reviews": [],
  "outcome_scope": "PARTIAL",
  "checked_routes": [{"route_type":"OFFICIAL_ROSTER","url_or_query":"https://...","result":"No exact safe identity match."}],
  "notes": "Why this campaign produced no safe exact relation."
}
```

`checked_routes` is required for RESEARCH_OUTCOME and must record the distinct routes actually checked under `RESEARCH_STOP_PROTOCOL_V2.md`. `outcome_scope` is also required:
- `PARTIAL`: the checked routes are useful progress, but they do **not** exhaust the campaign. QA records `ACCEPT_PROGRESS` plus `research_routes_json`; the campaign remains open as `OPEN_WITH_PROGRESS`, and future dispatch carries the prior routes so Codex does not repeat them.
- `EXHAUSTIVE`: use only when the exact campaign is genuinely bounded/exhausted (normally a direct singleton or an explicitly exhaustive authoritative roster/profile scope). QA may record `ACCEPT_OUTCOME` only after independently confirming that scope.

RESEARCH_OUTCOME is research accounting only. It is not negative evidence and is not a canonical terminal decision.

The scheduler reads accepted exhaustive outcomes from `QA_REVIEW_LEDGER_V2.csv` and marks that exact campaign `EXHAUSTED_REVIEWED`, preventing repeated research. If the campaign target changes, its fingerprint changes and it automatically reopens. Structure-free `direct:<tag>` fingerprints depend only on that tag campaign, so resolving a sibling tag does not unnecessarily reopen already-reviewed direct work.

`parallel_terminal_candidates_v2.csv` reports exact current Research Units for which every current Forward campaign is `EXHAUSTED_REVIEWED`. This is accounting only; QA still applies the normal v3 terminal rules and exact unit fingerprint before writing a canonical terminal review.

## TECHNICAL_ESCALATION

May contain no relations/reviews. `notes` must state the concrete reproducible technical failure. It is not evidence.
