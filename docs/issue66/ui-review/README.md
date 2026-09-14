# Issue #66 — UX Refinement Pass 1 review screenshots

These full-window screenshots were captured from the Release WPF build of the current #66 branch on Windows after the UX Refinement Pass 1 changes.

- Source branch: `codex/issue66-dictionary-selection-usability`
- Source commit: `e3284e12604b9dc253fb455ef88ca0ccb177e520`
- Screenshot commit: `0ff23cb573ee01c865cabc694cb3007ff996f36e`
- Executable launched: Release build output from `src/DanbooruTagTool.App/bin/Release/net10.0-windows/`
- Target: `.NET 10.0-windows`; SDK `10.0.401`
- Windows display scaling: 150% (`LogPixels=144`, `Win8DpiScaling=1`)
- Window state and captured size: maximized, 1707 × 912 pixels

## Images

| File | Visible state |
| --- | --- |
| `dictionary.png` | Dictionary/Search workspace; `blue hair` query, three result rows, the first row selected, and Tag Details. |
| `current-prompt.png` | Dictionary/Search workspace; Current Prompt tab with normal, weighted, LoRA, `BREAK`, and unresolved raw items; per-item `×` and copy actions are visible. |
| `prompt-editor.png` | Prompt Edit workspace; the five mixed items are selected, showing `5件選択中`, the edit toolbar, and the actual English preview/copy area. |

The temporary review Prompt was:

```text
blue_hair, (looking_at_viewer:1.2), <lora:sample_lora:0.7>, BREAK, custom_trigger
```

No tooltip, popup, or error dialog is open. All images show the entire maximized window at 1707 × 912.

## Validation

- Debug build: PASS
- Debug tests: PASS (74 passed, 0 failed)
- Release build: PASS
- Release tests: PASS (74 passed, 0 failed)
- `git diff --check`: PASS
- Windows launch: PASS from the branch's Release output
- Manually confirmed: search and selected-result details; Prompt-chip inspection opens Tag Details; mixed English direct-edit Apply and Cancel; conflicting actions are disabled during direct edit; dictionary add then Prompt Undo; restart and saved mixed Prompt restoration; multi-select `Ctrl+A` shows five selected items.
- Exercised through automated tests, but not manually confirmed in this capture: empty-clipboard no-op and Prompt-item delete/Undo. A drag attempt did not visibly reorder the items, so drag reorder remains unconfirmed on this Windows interaction pass.

Search inspection showed distinct `sex` identities in the production catalog rather than duplicate canonical results emitted by SearchEngine: General `G:sex` plus Special IDs `S:54`, `S:66`, and `S:67`. Search results remain canonical-deduped; no Search/Core change was made.

No #64 classification, canonical/source asset, or protected catalog data was changed for this pass. The screenshot Prompt was stored in the isolated Release-output UserData copy, not the current portable UserData.
