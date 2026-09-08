# Issue #6 Windows UI helper unelevated smoke checkpoint (2026-09-08)

## Scope and safety

This was a controlled, read-only helper diagnosis with one temporary Codex configuration change. Forge Neo, extensions, model files, model selection, generation settings, and Forge configuration were not inspected or modified. The Luna premise was preserved; the active Codex config continued to specify `gpt-5.6-luna`.

Latest checkpoint used: `docs/testing/ISSUE6_UI_HELPER_DIAGNOSTIC_20260908.md`.

## Backup and temporary config change

Before editing, the original file was copied to:

`C:\Users\takas\.codex\config.toml.issue6-before-unelevated-20260908.bak`

Backup SHA-256: `49041EF6560E45D2F317BFA8C82F79DF9E65A26BC8CBBBD52B9A398B7303470E`

The only requested setting change was:

```toml
[windows]
sandbox = "unelevated"
```

The original value was `elevated`. After restart, Codex regenerated the runtime-only `SKY_CUA_NATIVE_PIPE_DIRECTORY` value (the pipe identifier changed); no other user setting differed from the backup. The config remains intentionally at `unelevated` because the helper smoke test passed. Current config SHA-256: `E02D6C64F9181E0D81EE2FC11A42D78C0BF0C607D09114941B49FF422B8613FC`.

## Restart

Codex Desktop/app-server was completely stopped and relaunched using the existing installed Desktop executable (`26.901.6511.0`). The post-restart process inventory showed a new `codex.exe` app-server (PID `30980`) and new Desktop processes; no installation or update was performed.

## Doctor result after restart

`codex doctor --json` was available and executed read-only:

- exit code: `1`;
- `overallStatus`: `fail` (unrelated failures remain in `terminal.env`, and endpoint exclusions remain unverified);
- CLI version: `0.153.4`;
- Desktop version: `26.901.6511.0`;
- `sandbox.helpers`: **ok** — `sandbox configuration is readable`;
- helper details: approval policy `OnRequest`, filesystem/network sandbox `restricted`, no Linux or execve helper, backend redacted by doctor;
- doctor stderr: **empty** (0 bytes).

This is a material improvement over the prior `helper_unknown_error` / provisioning failure under `elevated`.

## Minimal node_repl / browser-control smoke

After a fresh `cua_repl` kernel reset, `cua.getState()` succeeded and enumerated the browser-control surfaces. A temporary hidden Codex In-app Browser tab at `about:blank` was created and its AX state was read successfully (`AXWebArea about:blank`), then the temporary tab was closed. No external site, login, upload, or data transmission was performed.

## Verdict

The Issue #6 Windows UI helper blocker is **RESOLVED FOR THIS CONFIGURATION** with `[windows] sandbox = "unelevated"`: doctor reports `sandbox.helpers: ok`, and the minimal node_repl/browser-control smoke passed. The config was not restored because the user’s conditional restore instruction applies when the helper remains broken. The backup remains available at the path above for manual rollback if needed.

