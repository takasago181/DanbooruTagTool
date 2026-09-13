# Issue #66 — Windows UI review screenshots

These full-window screenshots were captured from the current #66 usability branch on the actual Windows desktop. They are intended for visual review; no UI or application code was changed for this capture.

- Capture commit (branch HEAD at capture): `766652d56e0669bf079360b11a61d3a273d8db6d`
- Source branch: `codex/issue66-dictionary-selection-usability`
- Latest WPF source commit: `82844336197f1a0430e86b7b1ed285f8c0ed91bb`
- Executable launched: `artifacts/current/DanbooruTagTool.exe`
- Windows display scaling: 150% (`LogPixels=144`, `Win8DpiScaling=1`)
- Window state and captured size: maximized, 1707 × 912 pixels

## Images

| File | Visible state |
| --- | --- |
| `dictionary.png` | Dictionary/Search workspace; `blue_hair` query, three result rows, first row selected, and Tag Details tab. |
| `current-prompt.png` | Dictionary/Search workspace; Current Prompt tab with five mixed item types, per-item delete controls, and copy action. |
| `prompt-editor.png` | Prompt Edit workspace; five visible items, Undo/Redo controls, Prompt-local find, and the actual English preview/copy area. |

The review Prompt was temporary and contained a normal tag, a weighted tag, a LoRA, `BREAK`, and an unresolved raw trigger:

```text
blue_hair, (looking_at_viewer:1.2), <lora:sample_lora:0.7>, BREAK, custom_trigger
```

The screenshots have no open tooltip, popup, or error dialog. The maximized window shows all five Prompt items in the editor. At the smaller restored window size, the Current Prompt pane may need internal scrolling.

## Validation note

The WPF executable launched and all three workspaces/states displayed normally. A fresh Release build was attempted with `dotnet build .\src\DanbooruTagTool.sln -c Release`, but this environment has no installed .NET SDK, so that command could not run. The current artifact was the already-built `artifacts/current` executable from this branch. The pre-capture `UserData` directory was backed up outside the repository and restored byte-for-byte after capture.
