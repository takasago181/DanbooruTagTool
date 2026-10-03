## #264 merged / #254 COMPLETE

User-authorized merge main: `76269b8c69f772cae25435b460928da4f1745f90`.
PR #264 head `0069714a0bdec523d6bad1b99ef9c904cb74f1d4` and merge main have identical trees. Clean checkout; PR CI PASS and automatic merge CI PASS: https://github.com/takasago181/DanbooruTagTool/actions/runs/37108563768 . No manual benchmark/full-suite/CI rerun.

Accepted measured changes: query/term allocation reduction with unchanged global ranking/order; ordinal index only on newly built catalogs. Search ~49–54% faster with 72–86% less allocation; catalog Open 1.45→1.07s, WPF startup 3.44→2.96s. Detailed evidence: `docs/foundation/PERFORMANCE_STORAGE_2026-10-03.md` / `PERFORMANCE_RESULTS_2026-10-03.json`. Local final regression 360 PASS / 25 opt-in SKIP / 0 FAIL and clean build retained.

Product owners remain RuntimeCatalogIndex / CatalogDatabase; no persistent cache, dependency, existing-DB migration, accepted semantic change or UserData modification. Test-only opt-in measurement harness/current parity tests remain; normal CI skips workstation benchmarks. Production remains #245 LKG. Branch retained reachable from merged main; no branch/worktree deletion. Temporary measurement artifacts are dispositioned during final Foundation closeout; durable evidence remains in main. Rollback is the code revert; old/new catalogs remain compatible and UserData rollback is unnecessary.

#254 is complete. Continue only the user's explicitly authorized #255 decision and Foundation validation/uninstalled LKG closeout; no #230/#256 feature work.
