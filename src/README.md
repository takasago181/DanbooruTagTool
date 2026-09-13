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

The importer consumes the accepted Special/Japanese/Alias/usage assets, Issue #56 browse taxonomy, and Issue #63 product-fit sidecar. General browsing remains a provider boundary with a pending state until Issue #64 is accepted.

## Portable publish

Portable publish is optional and is not required for each UI iteration. Routine UI work should use the Debug/Release build, tests, and Windows launch. When a local portable output is explicitly needed, `publish-portable.ps1` reuses one of the fixed repository-root paths below:

- `../artifacts/current/` for the current local validation output (default);
- `../artifacts/publish/` only when explicitly requested with `-Destination publish`.

The script stages a fresh Windows x64 self-contained publish, synchronizes runtime files into the selected fixed directory, refreshes `Data/catalog.db`, and preserves any existing `UserData/` directory. Close the application before updating an output that is currently running. The temporary staging directory is removed after the command finishes.

```powershell
./publish-portable.ps1 `
  -Catalog <path-to-catalog.db> `
  -Destination current `
  -Dotnet dotnet
```

For an explicitly requested distribution publish, use `-Destination publish`. The output contains the executable and runtime files, `Data/catalog.db`, and `UserData/`. No Python/Tk runtime or separate .NET Desktop Runtime is required for the self-contained output. `UserData/user.db` is created on first launch and is kept when that fixed output is updated.

Windows UI screenshots belong in the repository-root `artifacts/screenshots/`. Keep current screenshots there and move retained older validation captures under `archive/artifacts/screenshots/`; do not add numbered screenshot folders for ordinary UI work.
