# Issue #117 local runtime validation runbook

Status: PREPARED / DO NOT RUN WITHOUT WORKSTATION ACCESS

Authority anchor:
- live main: `1dad93c0bc1ae62ad7f5b97d880c4f206ab46ced`
- PR #125 merge commit: `2ada80b4611b64ac5717924ae634ba917e3d0b95`
- validated product/test source: `5c08cb442804b8c49166b7d6055c29b54c693382`
- final CI run: `35314061974`
- #117 merge checkpoint: `5726106277`

This runbook is intentionally conservative. It does not authorize deleting, resetting, or recreating `UserData/user.db`, and it does not use `git clean`.

## 1. Read-only baseline first

From the repository root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\issue117_local_runtime_preflight.ps1
```

If the protected source root is separate from the repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\issue117_local_runtime_preflight.ps1 `
  -ProtectedSourceRoot "<protected-source-root>" `
  -AuthorityRoot "<repository-root>"
```

Record before any mutation:
- checkout HEAD / branch / status;
- running DanbooruTagTool processes;
- `artifacts/current/` inventory;
- `artifacts/current/DanbooruTagTool.exe`;
- `artifacts/current/Data/catalog.db` size + SHA-256;
- `artifacts/current/UserData/user.db` size + SHA-256;
- root `DanbooruTagTool.lnk` target;
- all six protected production inputs.

If DanbooruTagTool is running, do not replace runtime files yet. Stop the app normally before the apply step.

## 2. Update tracked source safely

Do not clean ignored files.

Required source state before build:
- live `main` at `1dad93c0bc1ae62ad7f5b97d880c4f206ab46ced` or a later explicitly accepted checkpoint;
- no unexpected tracked local modifications.

Use normal fetch / fast-forward only. Never use:
- `git clean -fdx`
- `git clean -fdX`
- destructive reset of protected local data.

## 3. Release build

From repository root:

```powershell
dotnet restore .\src\DanbooruTagTool.sln
dotnet build .\src\DanbooruTagTool.sln -c Release --no-restore
```

Do not continue if Release build fails.

Expected build executable:

```text
src\DanbooruTagTool.App\bin\Release\net10.0-windows\DanbooruTagTool.exe
```

## 4. Build catalog into a fresh staging directory

Never point catalog build directly at protected source data or `artifacts/current/Data`.

Example:

```powershell
$repo = (Resolve-Path ".").Path
$source = $repo   # replace only if protected-source-root is separate
$catalogStage = Join-Path $repo "artifacts\issue117-catalog-staging"

if (Test-Path $catalogStage) {
    throw "Staging directory already exists. Inspect it manually; do not auto-delete."
}

New-Item -ItemType Directory -Path $catalogStage | Out-Null

& ".\src\DanbooruTagTool.App\bin\Release\net10.0-windows\DanbooruTagTool.exe" `
  --build-catalog $source $repo $catalogStage

if ($LASTEXITCODE -ne 0) {
    throw "Catalog build failed."
}
```

The product guard rejects output inside protected `data/` and authority `docs/issue56/`.

Expected staged outputs:
- `catalog.db`
- `import-report.json`

Do not modify `artifacts/current/` yet.

## 5. Validate import-report before runtime apply

Expected production backing-row counts:

| Category | Expected |
| --- | ---: |
| General | 30,629 |
| Special | 3,059 |
| Character | 35,890 |
| Copyright | 8,536 |
| Artist | 48,313 |
| Total catalog rows | 126,427 |

Expected #118 identity authority:

| Intent authority | Expected |
| --- | ---: |
| Identities | 31,752 |
| SEXUAL | 2,037 |
| CONTEXTUAL | 1,951 |
| NON_SEXUAL | 27,759 |
| UNCLASSIFIED | 5 |

Also expected:
- #118 metadata is baked at explicit catalog-build time;
- normal startup must not parse the #118 research corpus;
- #64 UNRESOLVED General is searchable but not browseable;
- #76 reference-only / non-direct Special does not become browseable;
- deep-only requires accepted direct-browse Special evidence.

If counts or build authority drift, stop before runtime apply.

## 6. Publish new runtime into another fresh staging directory

Use the repository publish script and the newly built catalog.

```powershell
$runtimeStage = Join-Path $repo "artifacts\issue117-runtime-staging"

if (Test-Path $runtimeStage) {
    throw "Runtime staging directory already exists. Inspect it manually; do not auto-delete."
}

.\src\publish-portable.ps1 `
  -Catalog (Join-Path $catalogStage "catalog.db") `
  -Output $runtimeStage `
  -Dotnet dotnet
```

The staging runtime has its own empty `UserData/`. Do not launch it as the user's real runtime and do not use its user.db as a replacement for the existing one.

## 7. Apply to artifacts/current without touching UserData

Only after all previous checks pass and DanbooruTagTool is not running.

Before apply, record the existing `artifacts/current/UserData/user.db` hash again.

Apply the staged runtime as an overwrite-only overlay while explicitly excluding `UserData`.

Do not use `/MIR`, broad cleanup, or deletion during this gate.

One conservative PowerShell approach:

```powershell
$current = Join-Path $repo "artifacts\current"

Get-ChildItem -LiteralPath $runtimeStage -Force |
    Where-Object { $_.Name -ne "UserData" } |
    ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $current -Recurse -Force
    }
```

This intentionally leaves unrelated stale files alone. Cleanup is a separate task, not part of runtime validation.

After apply:
- verify `artifacts/current/Data/catalog.db` matches staged catalog SHA-256;
- verify the existing `artifacts/current/UserData/user.db` SHA-256 is unchanged;
- verify the root shortcut target resolves to the updated `artifacts/current/DanbooruTagTool.exe`.

## 8. Practical WPF smoke

Launch through the normal root shortcut and verify the #117/#118 checklist.

At minimum:
- startup succeeds;
- old visible General / ◆ Special roots absent;
- three presentation headings visible;
- 19 ordinary routes available;
- Character / Copyright / Artist dedicated scopes work;
- neutral state does not enumerate the full ordinary identity population;
- Japanese and English search work;
- query survives route changes;
- content `すべて / 一般向け / 性的` works;
- CONTEXTUAL appears in both narrow filters;
- UNCLASSIFIED 5 only appears under All;
- `◆ 深掘りのみ` works;
- #76 reference-only/non-direct rows do not re-enter browse;
- `全解除` preserves query;
- neutral state clears stale left highlight;
- overlap canonical is not duplicated;
- two-column display remains intact;
- Prompt add/remove/copy has no obvious regression.

## 9. Final user.db integrity gate

After smoke, calculate SHA-256 of the real `artifacts/current/UserData/user.db` again.

For this #117 runtime gate, the requested acceptance condition is:

```text
before SHA-256 == after SHA-256
```

If it differs, stop and report before closing #117.

## 10. Close condition

Close #117 only when:
- production catalog rebuild passed;
- runtime was refreshed from accepted merged main;
- practical WPF smoke passed;
- the real user.db hash remained unchanged;
- no protected source or membership authority was mutated.
