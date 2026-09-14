# DanbooruTagTool WPF v1

This directory contains the clean WPF implementation for Issue #66. The application is split into `App`, `Core`, `Data`, and `Tests` projects. `Core` contains the prompt and search rules and does not depend on WPF or SQLite. `Data` owns the SQLite boundaries and portable persistence. `App` is the WPF composition root and UI.

The checked-in solution targets .NET 10.0 (`net10.0-windows` for WPF) and is pinned to SDK `10.0.401` by `global.json`. The normal runtime path opens an existing `Data/catalog.db` and autosaves user state to `UserData/user.db`; it does not rebuild a catalog on startup.

## Build and test

From this directory, with the .NET SDK available:

```powershell
dotnet restore DanbooruTagTool.sln
dotnet build DanbooruTagTool.sln -c Release --no-restore
dotnet test DanbooruTagTool.sln -c Release --no-build
```

## Explicit catalog build

Catalog import is an explicit operation. It reads the existing protected source assets and writes a new SQLite catalog to the requested output directory. It does not modify the source assets and does not import the unaccepted Issue #64 General taxonomy.

```powershell
DanbooruTagTool.exe --build-catalog <repository-root> <authority-root> <output-directory>
```

The importer consumes the accepted Special/Japanese/Alias/usage assets, Issue #56 browse taxonomy, Issue #63 product-fit sidecar, and the hash-pinned Issue #64 production candidate files under `docs/issue64/production_candidate/`. It places only `PROPOSED` General taxonomy paths into the rebuildable catalog; the 2,403 `UNRESOLVED` rows retain an explicit status and no browse paths. Primary and accepted secondary paths share the existing `IGeneralBrowseProvider` contract. The existing #63 product-fit gate remains active: six proposed entries retain their taxonomy paths but remain excluded from browse, search, and Prompt addition under their existing `OUT_OF_SCOPE_PRODUCT` status. Source files and the Japanese overlay remain separate and unchanged.

The taxonomy is loaded only by the explicit `--build-catalog` operation. Normal application startup reads the resulting `Data/catalog.db` and selects the General browse provider from catalog metadata; it does not re-read CSV/JSON sources or rebuild indexes.

## Portable publish

`publish-portable.ps1` creates a new folder (it refuses to overwrite an existing folder), publishes a Windows x64 self-contained application, and places the supplied catalog at `Data/catalog.db`.

```powershell
./publish-portable.ps1 `
  -Catalog <path-to-catalog.db> `
  -Output ./artifacts/portable `
  -Dotnet dotnet
```

The output is a copyable folder containing the executable and runtime files, `Data/catalog.db`, and `UserData/`. No Python/Tk runtime or separate .NET Desktop Runtime is required for the self-contained output. `UserData/user.db` is created on first launch and is portable with the folder.
