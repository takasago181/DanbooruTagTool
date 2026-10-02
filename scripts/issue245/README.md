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

## Independent native #223 geometry probe

Run native probes and WPF tests sequentially in the same session. This probe keeps
the Window ancestor, does not use UiAudit or product Application startup, and has
memory-only UserData/clipboard. It neither changes OS geometry nor patches tests.
The second explicit-content snapshot is a supplementary layout experiment, not a
claim that native chrome resized. The first native snapshot is the primary evidence.

```powershell
dotnet run --project scripts/issue245/GeometryProbe.csproj -c Release --disable-build-servers -- <authority-root> <new-output.json> <revision>
```

To reference the detached clean-main checkout without adding files there:

```powershell
dotnet run --project scripts/issue245/GeometryProbe.csproj -c Release --disable-build-servers -p:AuditProductRoot=C:/Codex/DanbooruTagTool/.worktree-issue245-clean-main -- C:\Codex\DanbooruTagTool\.worktree-issue245-clean-main <new-output.json> a96dcd10d77e85d629e0169669ea26028f88c835
```

The source revision argument labels the product assembly baseline, not the helper
commit. Existing output is refused. Requested native cases: 1200x900, 1500x900,
900x560, 1280x720 DIP; all use Normal state and reviewed Three Houses group.


## After B-lite / normal portable runtime smoke

Updated UiAudit supports `[source-revision]`, 900x560/1280x720/1600x900/2560x1440, working conditions/quick LoRA/Negative, selected group results and comparison. The 36 after renders are detached client viewports, not physical-display pointer acceptance. Do not overlap native WPF helper/test/runtime processes.

`NormalRuntimeSmoke.ps1 -Candidate <clean-published-folder> -FixtureUserDb <owned-schema2-fixture-db> -Output <new-workspace-directory>` copies a candidate to a fresh disposable folder, transactionally seeds only owned fixture UI state and a nonempty all8 Recipe preset, starts the real executable twice, waits up to30 seconds for MainWindow, closes its own process gracefully and compares P/N/preset/UI state. Existing UserData and production are not edited. Process lifecycle is not a pointer audit. Use the after manifest source.
