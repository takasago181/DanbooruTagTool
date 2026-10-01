# Reviewed Browse HOME runtime integration

Base: `1f4a3fa0a908b9a1cbcd947930cd5460fdf4caf1`.
Branch: `codex/issue216-unresolved-coverage-7073`.

## Contract

`CatalogEntry.FormalHomeCopyright ?? CatalogEntry.ReviewedBrowseHome` supplies the
single Browse HOME. `BrowseHomeSource` distinguishes `FORMAL_HOME`,
`REVIEWED_BROWSE_FALLBACK`, and `UNRESOLVED`. Reviewed data is never written into
formal decisions. Legacy `RelatedCopyright` is retained for compatibility and is
never consulted by the new product path.

`Issue216BrowseHomeImporter` applies the hash-pinned projection during explicit
Full catalog builds. Normal startup reads the persisted catalog JSON. Ordinary
builds continue to exclude Character/Copyright/Artist. No research reconstruction,
Web requests, or CSV import runs during normal startup.

The dedicated `RelatedByBrowseHome` index supports both directions. Dictionary
cards show the work and a work/character button. Search inside a work intersects
ordinary search results with that work's HOME members. Character-target searches
also join matching Copyright search results to HOME members, with ID deduplication.
Ordinary all-category search ranking is unchanged.

## Counts

| Projection | Count |
| --- | ---: |
| Formal HOME available in runtime | 25,533 |
| Additional reviewed fallback available | 7,409 |
| Runtime Characters without usable HOME | 2,336 |
| Character catalog | 35,278 |
| Copyright catalog | 7,616 |
| Full catalog | 124,895 |

The research catalog is wider than the accepted product catalog. Of 7,746
reviewed assignments, 239 Characters are outside the product catalog and 98 have
roots outside that catalog. Also, 47 present Characters have formal roots outside
the product catalog. They receive no alternate fallback. These exclusions do not
change any research decision or add new catalog identities.

## Reproduction

Run `python scripts/issue216/build_browse_home_runtime.py --master <read-only frozen master> --check`.
The script requires the exact final #180 master SHA256
`135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`.
Projection and input fingerprints are in `BROWSE_HOME_RUNTIME_MANIFEST_V1.json`.
The frozen master stays ignored/local; the compact projection is tracked.

## Initial branch validation (historical)

- Python #216/#180 regression: 121 passed.
- Standard Windows/WPF solution regression: 213 passed, 16 protected-input tests skipped.
- Local full staged catalog: 124,895 entries; Character/Copyright unchanged.
- Protected-data focused regression: 8 passed (projection, database provenance,
  precedence, unresolved exclusion, Browse/search, source integrity, Ordinary isolation).
- Deterministic projection reconstruction: byte-for-byte PASS.
- Formal authority accounting: 13,983 accounted, UNRESEARCHED 0, missing roots 0;
  formal decision/source/member files unchanged.
- Windows UI: `chen` displayed 東方Project; work navigation returned exactly one
  Copyright; inverse navigation returned 318 HOME Characters; scoped `chen`
  search returned only Touhou members. Isolated verification window closed.
- `git diff --check`: PASS.

An exploratory all-protected test run also exposed the older
`ProductionGeneralBrowseAddSearchUndoCopyAndRestart` fixture's obsolete
`general:` navigation expectation. It is outside this HOME integration; the
current standard WPF composition/navigation tests pass. The initial branch used an Ordinary-profile workaround. Integration with latest main
restored the current Full source-isolation test and included the new projection input;
the obsolete General navigation fixture was already corrected on main.

All builds and UI checks used new ignored staging directories in this worktree.
No main merge, production promotion, UserData copy, protected data movement, or
formal authority mutation was performed. CI includes a Windows solution test job
alongside existing Python authority checks.

## User-authorized main integration and deployment — 2026-10-01

PR #217/#218 merged; final runtime source main `cbfab29134ed41e15c25ba24e1426c8411d65207`. Latest main fixes were preserved. Repeated HOME strings now reuse canonical Copyright strings, keeping the dedicated HOME index within the managed-memory Gate without changing semantics.

Clean canonical publisher and bounded promoter deployed to `C:\Codex\DanbooruTagTool-App`. Formal authority files remain immutable. Real UserData was not copied and remained byte-identical. The final candidate and installed-catalog suites each passed 249 tests / 3 explicit opt-in skips; dedicated performance and main CI passed. Full catalog identities and non-HOME metadata changed 0.

Installed launch and saved 13-tag Prompt accessibility passed. Screenshot capture showed a white client area on both old and new runtimes; final visual appearance is not verified. Exact release hashes and limitation: `PRODUCTION_PROMOTION_2026-10-01.json`.
