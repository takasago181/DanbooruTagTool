# Stage8C Finalization — Test-Only Correction Request

Current fixed state:
- Pilot001: ACCEPTED
- Exit Pilot: PASS
- Pilot003: NOT REQUIRED
- Stage8C: NOT FINAL
- Stage9 implementation: NOT STARTED
- Stage6 parity: PASS
- Full pytest: FAIL (18 failed / 194 passed)

Do NOT reopen Pilot001, Exit Pilot semantics, Ruleset2, or Stages 0–8B.
Do NOT change production semantics merely to satisfy tests.
Do NOT start Stage9.

The 18 failures are already diagnosed as test/fixture drift after the accepted Exit Pilot state.

Allowed scope: tests and test-only fixtures/assertions required to reconcile the suite with the accepted canonical state.

Required corrections:
1. Update stale Pilot001-only global count/hash assertions to the accepted Exit Pilot totals.
   - Preserve separate assertions that Pilot001's original scope and previously accepted rows remain unchanged.
   - Do not weaken invariants.

2. Make CSV-reading test fixtures BOM-safe.
   - The accepted CSV is UTF-8 with BOM.
   - Test helpers must not leak `\ufeff` into the first DictReader key.
   - Prefer explicit `utf-8-sig` or equivalent BOM-safe handling in test code.

3. Remove row-order dependence from the synthetic resolver fixture.
   - Do not assume `support.special_rows[0]` is a specific row.
   - Select the intended row explicitly by stable identity/key.
   - Preserve semantic assertions.

4. Do not modify:
   - Ruleset2 authority
   - source dictionaries / Special2788 identity
   - Stage8B runtime source unless a real production defect is proven
   - accepted Exit Pilot decisions/data merely to make tests pass
   - Stage6 behavior
   - Stage9 code

After correction, run exactly:
- full pytest: `python -m pytest -q -p no:cacheprovider`
- Stage6 parity using the existing Stage8A and Stage7B verification procedures
- targeted Stage6/Stage7B/Stage8A/Ruleset2 regression if already part of the canonical finalization procedure
- protected hash checks

PASS gate:
- full pytest PASS
- Stage6 parity PASS
- protected hashes PASS
- Ruleset2 authority unchanged
- source identity unchanged
- Pilot001 remains ACCEPTED
- Exit Pilot remains PASS
- Pilot003 remains NOT REQUIRED

If all pass:
- mark Stage8C FINAL
- update finalization summary / current handoff / handoff manifest
- set next stage = Stage9
- keep Stage9 implementation NOT STARTED
- return CHATGPT_HANDOFF.zip

If any failure reveals a real runtime/architecture/semantic defect, do not mask it by changing tests; report it and keep Stage8C NOT FINAL.
