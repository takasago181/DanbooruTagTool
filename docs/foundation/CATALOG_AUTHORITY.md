# Current semantic authority and catalog compilation

Production input is `authority/catalog/current/manifest.json` and the five
compressed JSONL semantic assets it names. Historical Issue evidence is preserved
in place; `provenance.json` locates the exact migration sources and installed LKG.
Provenance is not an executable build recipe.

The snapshot is **accepted domain data**, not a SQLite dump. Each row has a stable
ordinal and a `CatalogEntry` with writable domain fields. Computed runtime getters
are omitted from authority. SQLite indexes, connection settings, metadata tables
and runtime query indexes remain compiler/backend concerns. Keeping the existing
domain shape avoids an unrelated CatalogEntry redesign.

The resolved semantic projection includes canonical/stable Special identity,
membership, raw English surface, Japanese display/search, aliases, eligibility,
Special v2 classifications, SexualIntent, Unified routes/facets, HOME/BrowseGroup
and reviewed quality fields. There is no generation-profile membership dependency
or Issue-order overlay in production compilation.

## Schema v1

- Manifest `Schema`: `dtt.catalog-authority-v1`.
- `Snapshot`: human-readable accepted snapshot identity.
- `Assets`: relative gzip JSONL paths, SHA256, row count and category.
- `CategoryCounts`: exact accepted population per category.
- `IdentitySha256` / `SpecialIdentitySha256`: SHA256 of sorted identity tuples
  (`Id`, `Canonical`, `English`, `IsSpecial`, `EffectiveCategory`), serialized as
  compact JSON and joined with LF without a final LF.
- JSONL rows: `{ "Ordinal": integer, "Entry": CatalogEntry }`.
- Enums use .NET domain names; unknown fields/enums/schema and missing required
  constructor fields are refused. Global ordinals are unique/contiguous.
- Assets and populations are validated before writing; IDs, stable Special shape,
  known route/body/theme vocabulary and runtime indexes are validated as well.

`CatalogAuthorityReader` owns this input contract; `CatalogCompiler` owns the
SQLite build adapter. WPF reads only `Data/catalog.db` and runtime semantics.

## Maintenance commands

```powershell
dotnet run --project src/DanbooruTagTool.Maintenance -c Release -- verify authority/catalog/current/manifest.json
dotnet run --project src/DanbooruTagTool.Maintenance -c Release -- compile authority/catalog/current/manifest.json "$env:TEMP/DTT-new-catalog"
```

The output must be fresh/empty, separate from authority and UserData, and cannot
traverse filesystem links. It is never installed automatically. `--profile
ordinary` is retained for isolated validation; standard compilation retains Artist
and all five accepted categories.

For a newly accepted snapshot of the same schema, edit the semantic rows and
manifest hashes/counts/identity signatures, run `verify`, then `compile` and the
relevant semantic review/regressions. No C# hash/count/path edit is needed. The
snapshot acceptance decision still belongs to the user/DEV; merely updating a
manifest does not approve a semantic change. A domain schema/vocabulary change may
require code and a new schema version.

## Migration oracle and recovery

`src/DanbooruTagTool.Tests/LegacyCatalogBuild` contains the old build and evidence
resources. Only the test project compiles it; Data/App/Maintenance do not depend on
it. Original Issue-named tests remain provenance/regression evidence. The one-time
export test requires `DTT_EXPORT_AUTHORITY`, refuses an existing target, and first
compares the complete old output against the installed LKG. Normal tests cannot
regenerate authority.

The migration compared every serialized field and ordinal of all 124,895 rows,
then compared the new snapshot and rebuilt database. This protects accepted adult
and hard/niche vocabulary, stable IDs, Special discovery, SexualIntent, Unified
routes/facets and HOME/group, without genericizing the catalog.

Rollback is the pre-cutover main/installed LKG plus retained legacy oracle and
source provenance. This batch does not promote any runtime, touch real UserData,
or move/delete legacy Python, protected source data or research evidence.
