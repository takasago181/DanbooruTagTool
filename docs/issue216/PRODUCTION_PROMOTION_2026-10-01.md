# Issue #216 production checkpoint — 2026-10-01

## Result

PR #217 and #218 merged. Clean Release runtime built from merged main `cbfab29134ed41e15c25ba24e1426c8411d65207` and deployed to `C:\Codex\DanbooruTagTool-App` using the canonical publisher and bounded promoter. The existing continuation branch is retained. Exact hashes, counts and measured performance are in `PRODUCTION_PROMOTION_2026-10-01.json`.

Formal HOME is preferred; reviewed HOME is a separately identified Browse/search fallback. Additional usable Characters: 7,409. Formal authority mutation, catalog identity changes and non-HOME payload changes: 0. Character/Copyright counts remain 35,278 / 7,616; missing HOME roots 0.

## Evidence

Python #216/#180 121 PASS; standard Windows 233 PASS / 19 opt-in SKIP. Final clean candidate and actual installed catalog each 249 PASS / 3 opt-in SKIP / 252 total. Dedicated final performance PASS, retained managed memory delta 518,392 bytes. Main CI run 36831518328 PASS. Source-contract, SQLite integrity, runtime manifest, shape and installed launch PASS.

Real UserData was excluded from promotion and remains byte-identical after installed read-only startup. The saved 13-tag Prompt restored. No protected artifact was moved or deleted. The previous runtime managed payload backup and logs remain in ignored `.tmp-issue216-work/promotion-20261001/`.

## Limitation and next Gate

The UI automation capture returns a white client area for both prior production and new candidates, although accessibility is populated and query/Browse paths were checked. Later coordinate input reported geometry unavailable. Final visual appearance is NOT VERIFIED; no rendering-policy change was attempted. Remaining Gate is human visual confirmation. Deployment and programmatic regressions are complete; no new HOME research is needed.

Subsequent documentation-only merge updates project routing and LKG; it does not change the deployed runtime source revision or hashes.
