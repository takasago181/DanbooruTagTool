# DanbooruTagTool WPF v1

This directory contains the clean WPF implementation for Issue #66. The application is split into `App`, `Core`, `Data`, `Maintenance`, and `Tests` projects. `Core` contains the prompt and search rules and does not depend on WPF or SQLite. `Data` owns the SQLite boundaries and portable persistence. `App` is the WPF composition root and UI.

The checked-in solution targets .NET 10.0 (`net10.0-windows` for WPF) and is pinned to SDK `10.0.401` by `global.json`. The normal runtime path opens an existing `Data/catalog.db` and autosaves user state to `UserData/user.db`; it does not rebuild a catalog on startup.

## Build and test

From this directory, with the .NET SDK available:

```powershell
dotnet restore DanbooruTagTool.sln
dotnet build DanbooruTagTool.sln -c Release --no-restore
dotnet test DanbooruTagTool.sln -c Release --no-build
```

## Explicit catalog build

Catalog compilation is an explicit Maintenance operation. It reads only the accepted semantic snapshot and manifest under `authority/catalog/current/`, validates hashes/population/identity/classifications, and writes a new SQLite catalog to a fresh output. The command below is run from the repository root:

```powershell
dotnet run --project src/DanbooruTagTool.Maintenance -c Release -- compile authority/catalog/current/manifest.json <new-empty-output-directory>
```

The snapshot preserves every accepted domain field, stable Special ID, Japanese/English/mixed discovery, SexualIntent, Unified route/facet and HOME/group. Production code no longer imports historical Issue overlays or generation-profile membership. The old build remains test-only for parity and provenance; see [catalog authority](../docs/foundation/CATALOG_AUTHORITY.md).

Normal WPF startup opens only `Data/catalog.db`. It never compiles authority or owns build sequencing.

## Portable publish

`scripts/maintenance/publish_portable_runtime.ps1` is the canonical publisher. `publish-portable.ps1` is a compatibility wrapper. The pipeline requires an explicit clean source revision, the accepted semantic authority manifest (`SourceRoot` is now optional compatibility input), builds and validates a full catalog, and publishes a self-contained single-file Windows x64 runtime into a fresh output folder. Candidate `UserData` contains only disposable data; real UserData is never a publish input. See `docs/maintenance/PORTABLE_RUNTIME_PIPELINE.md` for the candidate, manifest, runtime-shape, promotion, and rollback sequence.

```powershell
../scripts/maintenance/publish_portable_runtime.ps1 `
  -SourceRevision <exact-clean-HEAD> `
  -OutputRoot <fresh-output-outside-checkout> `
  -SourceRoot <protected-source-root> `
  -AuthorityRoot <accepted-authority-root>
```

The output is a copyable folder containing the executable and runtime files, `Data/catalog.db`, and `UserData/`. No Python/Tk runtime or separate .NET Desktop Runtime is required for the self-contained output. `UserData/user.db` is created on first launch and is portable with the folder.
