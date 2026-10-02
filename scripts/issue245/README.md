# #245 baseline audit helpers

Development-only tools; no product startup/command changes. The baseline is
`a96dcd10d77e85d629e0169669ea26028f88c835`. Do not describe their output as native
window/pointer acceptance or as a successful #245 merge gate.

From this checkout:

```powershell
python -B scripts/issue245/inventory.py
dotnet run --project scripts/issue245/UiAudit.csproj -c Release --disable-build-servers -- C:\Codex\DanbooruTagTool\.staging-issue245-audit-NEW C:\Codex\DanbooruTagTool-App\Data\catalog.db
```

The output must be a new empty directory with a `.staging-issue245-audit-` prefix.
The catalog is opened read-only. All user DBs, image/LoRA fixtures and scans stay
inside the disposable output. No clipboard, Forge request, extension install,
production UserData migration, model download or production apply occurs.

Each PNG is an explicitly arranged 96 DPI client viewport. Native dimensions and
screen geometry are recorded separately. The content is detached temporarily to
avoid native ancestor clipping on a reduced display. Window resources, inherited
fonts, DataContext and layout settings are retained. Ancestor Window command
bindings may be unavailable during capture; use the declarative inventory and
source/tests for semantics. Offscreen scroll descendants are not automatically
UI defects. No render mode override is used.

The tiny PNG fixture reuses the existing private runtime-validation fixture writer
by reflection; if that writer changes, fail and update this audit helper explicitly.
This is not a new metadata codec or runtime dependency.
