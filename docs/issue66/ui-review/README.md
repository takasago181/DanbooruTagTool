# Issue #66 — UX Refinement review screenshots

These screenshots show the Windows Release WPF application after DEV review and UX Refinement Pass 2. They were captured from an isolated copy of the current branch's Release output; the user's current portable `UserData` was not used.

- Source branch: `codex/issue66-dictionary-selection-usability`
- Source commit: `261525e378bb81df1d4613d411eb7ae4421d9217` (`fix(wpf): polish prompt find and browse navigation`)
- Screenshot commit: `3387f66357cf9d515bd40af8bffddd427f358404`
- Executable: isolated copy of `src/DanbooruTagTool.App/bin/Release/net10.0-windows/DanbooruTagTool.exe`
- Target: `net10.0-windows`; SDK `10.0.401`
- Windows display scaling: 150% (`LogPixels=144`, `Win8DpiScaling=1`)
- Window state and captured size: maximized, 1707 × 912 pixels

## Images

| File | Visible state |
| --- | --- |
| `dictionary.png` | Dictionary/Search workspace; `blue hair` query, three results, first result selected, Tag Details visible, Prompt history controls separated from search. |
| `current-prompt.png` | Dictionary/Search workspace; Current Prompt tab with normal, weighted, LoRA, `BREAK`, and unresolved raw items; per-item delete and copy controls visible. |
| `prompt-editor.png` | Prompt Edit workspace; six mixed items, local-find count and previous/next controls, edit toolbar, and actual English preview visible. |

The isolated review Prompt was:

```text
blue_hair, red_hair, (looking_at_viewer:1.2), <lora:sample_lora:0.7>, BREAK, custom_trigger
```

No tooltip, popup, or error dialog is open. All images show the full maximized window at 1707 × 912.

## Validation

- Debug build: PASS
- Debug tests with production catalog: PASS (75 passed, 0 failed, 0 skipped)
- Release build: PASS
- Release tests with production catalog: PASS (75 passed, 0 failed, 0 skipped)
- Windows launch from an isolated Release copy: PASS
- Prompt local find `hair`: 2 matches; next/previous updates `1/2` and `2/2` and scrolls to each match.
- Browse Back: tree selection follows navigation to General and back to Special; Back disables at the root.
- Drag reorder: PASS; moving `blue_hair` after the weighted item changed the English preview order; Undo restored the initial order and Redo reapplied it.
- Prompt edits and persistence during screenshot setup used only the isolated Release-copy `UserData`.

No Core/Data/Search, #64 taxonomy, canonical/source assets, protected catalog, or user's current portable data were changed for this pass. The production catalog contains 33,417 entries; the General taxonomy remains unintegrated pending #64 acceptance.
