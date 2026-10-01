# Issue #179 production checkpoint — 2026-10-01

## Result

Existing `audit/issue179-refresh-20261001` retained. PR #220 merged the reviewed quality overlay; PR #221 added its missing input to the Full source-isolation test fixture. Final clean runtime source main: `a317efdc831b45b2a088fb9d4cdeb7873472253e`. Canonical publisher and bounded promoter deployed to `C:\Codex\DanbooruTagTool-App`.

- 1,215 corrected rows; 1,221 audited fields: display 221 / search 1,000. This continuation added only Enterprise's already-reviewed cleanup row to the old projection.
- Label changes 221 are derived from the same display corrections, not additional audit decisions.
- Stage A 44,426 / Stage B 500/500 review paths validated.
- HOLD display candidates 17; Stage B subjects with REVIEW dimensions 373; regex residuals 12 (overlapping sets). Ambiguous/collision/regex-only signals remain unchanged.
- Mari-only Illustrious search removal retained. Azur Lane Illustrious keeps its valid identity search surface.

## Validation

Census/projection reconstruction PASS; tracked/generated CSV and manifest byte-identical. .NET #179/#70/#216 focused 12 PASS; standard suite 236 PASS / 19 opt-in SKIP. Final candidate and actual installed catalog each 252 PASS / 3 opt-in SKIP / 255 total. Python #216/#180 121 PASS. #179 census/composition CI, #216 authority CI, test-fixture follow-up CI and merged-main CI PASS.

Dedicated performance passed against a catalog byte-identical to the final runtime catalog: retained managed memory delta -128,040 bytes; all Search/Browse/memory blocker flags false. Runtime source integrity, shape, manifest, SQLite checks, isolated/installed startup and UserData health PASS.

## Protected invariants

Full catalog 124,895; Character 35,278 / Copyright 7,616 / Artist 48,313 unchanged. Formal HOME 25,533 / reviewed fallback 7,409 / unresolved 2,336 unchanged. Actual all-row comparison: identity/category/HOME/Artist changes 0; only reviewed display/search and derived Labels changed. Issue70 source and #180/#216 authority files unchanged.

Real UserData excluded from managed deployment; complete inventory/hash byte-identical after promotion and final read-only startup. Saved 13-tag Prompt restored. No protected artifact was moved/deleted. Prior audits, commits and generated evidence retained.

## Workstation limitation

Jahy and Illustrious search/display verified in actual candidate WPF accessibility. Installed startup and saved Prompt restored. Windows capture still returns a white client area as on prior production, so final visual appearance is NOT_VERIFIED; rendering policy unchanged. This does not replace the retained review/HOLD policy.

Exact release hashes and results: `PRODUCTION_CHECKPOINT_2026-10-01.json`. Later documentation-only main merge does not change runtime build provenance. #179 remains open for retained REVIEW/HOLD follow-up; this reviewed overlay deployment is complete.
