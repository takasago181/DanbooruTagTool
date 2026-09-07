# Codex Request — Stage8C Phase1 Pilot001 only

Implement the frozen Stage8C Phase1 Pilot001 in the current DanbooruTagTool repository.

## Scope

Apply only the 21-Special / 2-FamilyRuleId Pilot001 curation described in `00_START_HERE.md` using the existing Stage8C Phase0 architecture and validators.

Do not redesign Phase0. If a real architecture defect prevents correct Pilot001 application, stop and report it instead of broad refactoring.

## Required implementation behavior

1. Apply the SELF_ACTION family proposal `FRP_P1_SELF_ACTION_SOLO_V1` for all 15 current family members using the frozen metadata.
2. Preserve explicit-over-Family resolver precedence, especially ID88 `masturbation` where explicit `solo=CORE_SUPPORT` must win over the Family `solo=OPTIONAL_VARIATION` relation.
3. Record MACHINE_STRUCTURED as `NO_COMMON_RULE` for all 6 pilot members. Do not create a generic family support rule.
4. Apply/retain only the frozen Special-specific machine relations:
   - 310: 2 rows
   - 311: UNRESOLVED, 0 rows
   - 312: existing 5 rows unchanged
   - 313: 4 rows
   - 314: 3 rows
   - 1159: 2 rows
5. No changes outside the 21 Pilot001 review identities except deterministic derived artifacts/counts required by these rows.
6. Do not alter Ruleset2 dictionary/search/model-aux authorities.
7. Do not start Stage9 or Stage10.

## Acceptance checks

After applying the pilot, independently compute—not hard-code—the resulting state and require:
- SUPPORT_DEFINED = 28
- UNRESOLVED = 1
- NO_SUGGESTION = 0
- UNREVIEWED = 2759
- Special Support rows = 50 (baseline 39)
- Family Support rows = 1 (baseline 0)
- total review ledger identity remains 2788 unique Specials
- target family membership remains SELF_ACTION 15 + MACHINE_STRUCTURED 6
- SELF_ACTION result = RULES_DEFINED 15/15
- MACHINE_STRUCTURED result = NO_COMMON_RULE 6/6
- ID88 effective `solo` = explicit CORE_SUPPORT, not Family OPTIONAL_VARIATION
- ID311 support relation count = 0 and status = UNRESOLVED
- ID312 support relation content/count = existing five unchanged

If any expected count fails, do not change unrelated data to force the result. Report FAIL with the exact rows responsible.

## Regression / validation required

Run and report:
1. Stage8C targeted tests, including new Pilot001 acceptance tests.
2. Stage7A/7B/8A/8B/8C regression suite.
3. Full pytest.
4. Stage6 parity.
5. deterministic build/output comparison (two builds; byte-identical where current tooling supports it).
6. Stage8B protected hash check.
7. Ruleset2 protected/current authority hashes.
8. source Special ID+Tag identity equality.
9. runtime external/network calls = 0.
10. explicit diff proving only intended Pilot001 production/review artifacts changed.

Add focused regression tests for every frozen Pilot001 invariant above, especially resolver precedence, ID311 unresolved, ID312 unchanged, and no unrelated review-state drift.

## Handoff

Return a self-contained `CHATGPT_HANDOFF.zip` containing:
- exact changed-file list
- Pilot001 production/review artifacts
- relevant implementation and tests
- commands executed
- test results/counts
- before/after Pilot001 counts
- hashes of protected artifacts
- diff/ledger proving 21-member scope
- unresolved issues
- explicit state lines:
  - `Stage8C Phase1 Pilot001 implementation: COMPLETE` only if every acceptance check passes
  - `Pilot001 acceptance: NOT COMPLETE` (ChatGPT performs the independent acceptance audit after your handoff)
  - `Stage8C overall: NOT FINAL`
  - `Stage9: NOT STARTED`
  - `Stage10: NOT STARTED`

Stop after producing the handoff. Do not continue to Pilot002 or any later stage.
