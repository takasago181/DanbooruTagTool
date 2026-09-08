# Issue #41 effective-risk amendment

Status: frozen quarantine-only amendment for the fresh100 pilot.

## Defect

The audited R3 selector stores `risk_class` from a lexical classifier. That classifier underclassifies semantically compound canonicals such as `all_fours`, `loli`, and `fellatio`. The blind30 builder then groups directly by that stored value, so blind quotas can be numerically satisfied while under-covering the intended high-risk semantic classes.

## Constraint

The fixed fresh100 membership, ordinals, selection seed, and original `selection_risk_class` MUST NOT change. This amendment changes only the risk label used for downstream review requirements and blind30 stratification.

## Required behavior

1. Preserve the original pilot value as `selection_risk_class`.
2. Load the frozen `issue41_effective_risk_overrides.jsonl` keyed by canonical.
3. Derive `effective_risk_class` as the highest applicable risk between the preserved selection class and a valid frozen override. An override MUST NOT downgrade risk.
4. Use `effective_risk_class` for:
   - HIGH/CRITICAL exact-scope fail-closed requirements;
   - `pilot_rows.jsonl` downstream review reporting;
   - blind30 grouping and quota selection.
5. Keep fixed sample membership and `pilot_ordinal` unchanged.
6. Record both selection and effective classes in generated artifacts so the amendment is auditable.
7. Reject duplicate canonicals, unknown risk values, non-frozen override rows, canonical/ordinal mismatches, and downgrade attempts.
8. Deterministic replay MUST include the override manifest content hash.

## Risk order

`LOW < MEDIUM < HIGH_POSE_ACTION < HIGH_ANATOMY_ADULT < CRITICAL`

The two HIGH classes are different semantic lanes rather than a universal scalar severity ordering. For downgrade prevention, an override may replace LOW/MEDIUM with either HIGH lane, while CRITICAL remains the conservative maximum. A pre-existing HIGH lane may only remain the same lane or become CRITICAL unless an explicit future spec amendment defines cross-lane conversion.

## Blind30

`r3_build_blind_audit.py` must group by `effective_risk_class`, never by the stale lexical/selection class. `blind30_key.json` must expose both classes for auditability while the masked reviewer input must continue hiding automation state/reasons/risk.

## Tests required before blind30

- `all_fours`: LOW -> HIGH_POSE_ACTION
- `fellatio`: LOW -> HIGH_ANATOMY_ADULT
- `loli`: LOW -> CRITICAL
- downgrade attempt is rejected
- duplicate override is rejected
- unknown risk is rejected
- missing/non-frozen override metadata is rejected
- fixed 100 membership/ordinals unchanged
- blind selection groups on effective risk
- deterministic replay changes if the override manifest changes

No production `data/**`, #32 verdicts, #35 UI, search ranking, `CURRENT_DEV_TASK.md`, main, or Stage10 production A/B is modified by this amendment.
