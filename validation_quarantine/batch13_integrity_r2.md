# Batch 13 R2 integrity — Specials 1201-1300

- Result blocks: 1201-1220 / 1221-1240 / 1241-1260 / 1261-1280 / 1281-1300
- Reconciled coverage: 100 / 100
- Sequence range: exactly 1201-1300
- Duplicate sequences: 0
- Missing sequences: 0
- Batch distribution: PASS 73 / FIX 1 / REVIEW 26 / IMAGE_TEST_REQUIRED 0
- New FIX candidate: ID1241 `clitoral stimulation` -> `BodypartRequirementOverride=true` (quarantine only)
- Revalidation queue delta: 0
- Deterministic PASS re-audit: 15 / 73 (20.55%), including all A-risk PASS rows
- New false-PASS: 0
- Batch13 R2 acceptance gate: PASS
- Semantic-support durable coverage: 55 / 58; unchanged in this range
- Production/main modified: NO

PROVISIONAL / REVIEW_REQUIRED rows without exact frozen source authority were kept fail-closed as REVIEW. Identity-only alias rows preserve prompt identity and do not assert canonical/model-response equivalence. No Stage10 generation hypothesis was promoted to production truth.
