# Batch 6 R2 integrity check — sequences 501-600

Rule: R2
Range: 501-600
Result blocks: five append-only 20-row checkpoints (`0501_0520.csv` through `0581_0600.csv`)

## Reconciliation
- rows present: 100 / 100
- duplicate sequence IDs: 0
- gaps: 0
- first-pass distribution: PASS 92 / FIX 6 / REVIEW 2 / IMAGE_TEST_REQUIRED 0
- revalidation queue delta: none
- semantic-support source-row delta: none (remaining frozen rows attach to later Special IDs)
- production/main modified: NO

## Non-PASS review
- REVIEW: ID503 `unbirthing`; ID570 `cunt busting`
- FIX: ID535 pose; ID545 implement; ID569 bodypart; ID571 bodypart; ID573 bodypart+spatial; ID600 implement

All FIX findings are quarantine-only structural candidates. REVIEW rows remain unresolved rather than being guessed to PASS/FIX.

## PASS false-positive audit
`pass_sampling_batch6_r2.csv` deterministically rechecks 18 / 92 PASS rows, including every A-risk PASS plus six spread B controls.

- sampled PASS: 18
- false-PASS found: 0
- R2 escalation triggered: NO

## Gate
Batch 6 R2 acceptance gate: PASS, contingent on candidate-fix aggregate synchronization before advancing the durable restart pointer to 601.
