# Issue #232 — Positive / Negative Prompt intelligence

Negative reuses existing PromptWorkspace, PromptParser, PromptEditorViewModel and PromptEditorView, as a side tab inside Prompt editing. Independent raw direct editing, chips/order/weight, copy/import/New, Undo/Redo/Recovery. Both snapshots persist atomically in existing user.db. No second Prompt engine/new workspace DB.

Schema/payload version 2 adds an optional Negative snapshot. Version 1 is backed up consistently with SQLite before transactional migration; original JSON payload remains byte-for-byte unchanged during migration. Prompt IDs/order/raw surfaces/Recovery, UI and presets survive. Missing Separator JSON fields use legacy comma defaults. Newer schema/payload versions refuse opening/saving, no reset. Exercised on disposable UserData only, production untouched. Reversal: close DTT, restore the retained whole pre-migration user.db backup with the matching old app; version 1 software must not open a live version 2 DB.

Existing parsing gains top-level inline BREAK/AND lexical controls and lossless separators. Existing single-tag weight/LoRA nodes remain editable. Unsupported nested emphasis, schedules, alternation, wildcards and malformed groups remain raw and byte-round-trip. Lexical controls describe structure; Forge owns attention/scheduling. Unknown diagnostics mean DTT did not resolve a fragment, not that Forge rejects it. Canonical duplicate/alias/weight warnings within each side and intersections across sides never delete/move/rewrite. Optional opposite-rule configuration is deferred.

Library/PNG/preset Negative restore is a separate explicit replacement with Negative Undo/Recovery. Positive append/restore does not change Negative. LoRA recipe Negative has a separate explicit append. Existing Forge send/current-settings generation retains its Negative-unchanged contract. A new explicit pair-send replaces both fields, including intentionally empty Negative. API recipe generation still uses its saved/image recipe's two prompts.

## Token / chunk contract

Only an explicit button calls loopback `/dtt-bridge/token-count`, no startup traffic. Companion upgrade/restart uses the existing explicit installer; this work does not automatically install/restart production's Forge extension.

The independently written read-only adapter calls installed `modules.ui.update_token_counter` with submitted side, Steps and no styles under a nonblocking Forge queue lock. No generation, model loading, options mutation, queued UI delivery, DOM automation or assumed 75-token behavior. Returns loaded checkpoint/hash, engine/tokenizer, original text/side/Steps. **Forge Neo's pre-load FakeInitialModel heuristic counter is explicitly rejected.** Unsupported/busy/unloaded engines return unavailable. Chunk length comes only from the actual engine; C# checks capacity/divisibility. UI count can be maximum scheduled/AND branch, not a universal sum. BREAK/AND lexical boundaries remain visible without tokenizer.

C# refuses remote/HTTPS/credentials/subpaths/query/fragment, proxy and redirects. Bounded response; source/model/request/chunk checked. Edits/output-profile changes invalidate counts; changes during a request or different models between sides reject results. Production's existing Forge companion lacks the new endpoint, so returns unavailable. Loaded-model exact counts against a live upgraded Forge are **not verified**; protocol/model-owned delegation and refusal gates are tested. UI describes contextual Forge UI counter results, no universal exactness claim.

## External review — no copied or ported source

| Project / exact revision / license | Reviewed files/functions | Usage |
|---|---|---|
| [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui/tree/82a973c04367123ae98bd9abdf80d9eda9b910e2), `82a973c04367123ae98bd9abdf80d9eda9b910e2`, AGPL-3.0 | `modules/prompt_parser.py`: `get_learned_conditioning_prompt_schedules`, `get_multicond_prompt_list`, `parse_prompt_attention`, BREAK/AND | Behavior reference, independently implemented incremental C# lexical/raw preservation. |
| [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/0b1783c79b397e73818c3d8432b25cc3cbb5ca50), `0b1783c79b397e73818c3d8432b25cc3cbb5ca50`, AGPL-3.0 | `modules/ui.py:update_token_counter`; `modules/sd_models.py:FakeInitialModel/SdModelData`; API routes; `backend/diffusion_engine/sdxl.py`/`sd15.py:get_prompt_lengths_on_ui`; `backend/text_processing/sd_engine.py:process_texts/get_target_prompt_token_count` | Protocol/behavior reference and independent adapter calling existing runtime functions. No Gradio DOM path. |

## Acceptance / limits

Focused syntax/history/migration/PNG/Library/preset/Forge/source-security/count-staleness tests, full protected-source regression, independent Python adapter tests, bridge Python/JS syntax, CI, clean publish and actual executable `--validate-prompt-intelligence <new-empty-directory>` are checkpointed in PR/Issue. Actual WPF 900x600 / 1400x900 uses isolated schema2 and verifies reusable Negative view/commands/persistence. No authority/research/legacy/data/production changes. Native pointer acceptance is limited by unrelated Windows Python firewall/security prompt, left untouched. Whole UI consolidation is deferred to the #225 STOP POINT inventory.
