# Issue #180 parallel proposal schema v1

Forward Worktrees write append-only JSON only under their own `docs/issue180/parallel/proposals/fwd-N/` directory.

Top-level required fields for every proposal:

```json
{
  "proposal_id": "pp1-unique-id",
  "assignment_id": "pa1-...",
  "epoch_id": "ep1-...",
  "canonical_base_sha": "<40-hex>",
  "unit_id": "ru3-...",
  "source_member_ids_sha256": "<sha256>",
  "assignment_member_ids_sha256": "<sha256>",
  "ownership_key": "family:... | base:... | direct:...",
  "work_bucket": "FAMILY_ROSTER_HIGH_YIELD",
  "worker_slot": 0,
  "proposal_type": "EVIDENCE_DIRECT_HOME",
  "source_url": "https://...",
  "source_claim": "Exact claim actually checked on the source page.",
  "payload": {}
}
```

Evidence payloads:

- `EVIDENCE_DIRECT_HOME`: Character / DIRECT_HOME / Copyright
- `EVIDENCE_FAMILY_HOME`: Family / FAMILY_HOME / Copyright
- `EVIDENCE_MEMBER_OF`: Character / MEMBER_OF / Family
- `EVIDENCE_VARIANT_OF`: Character / VARIANT_OF / Character

Each evidence payload must contain:
`subject_type`, `subject_key`, `relation_type`, `object_type`, `object_key`, `authority_type`, `evidence_basis`.

Example:

```json
{
  "subject_type": "Character",
  "subject_key": "example_character",
  "relation_type": "DIRECT_HOME",
  "object_type": "Copyright",
  "object_key": "example_work",
  "authority_type": "FIRST_PARTY_CHARACTER_ROSTER",
  "evidence_basis": "EXTERNAL_AUTHORITY"
}
```

Terminal payload:

```json
{
  "terminal_status": "NO_SAFE_EVIDENCE",
  "authority_source": "https://... or docs/issue180/...",
  "review_provenance": "What was checked and why positive HOME evidence was not established."
}
```

Forward may propose only `PARTIALLY_RESOLVED`, `NO_SAFE_EVIDENCE`, `POLICY_BLOCKED`, or `IDENTITY_BLOCKED`; QA decides whether the proposal becomes canonical.

Supersession payload must contain `"terminal_status": "SUPERSEDED_BY_NEW_UNIT"` and enough provenance for QA to bind the old fingerprint to the regenerated unit.

Technical escalation payload:

```json
{
  "failure_class": "HARNESS_OR_NETWORK",
  "details": "Concrete reproducible failure."
}
```

A proposal is never authority by itself. QA/Integrator must independently accept it before writing canonical v3 evidence/decision/terminal-review rows.
