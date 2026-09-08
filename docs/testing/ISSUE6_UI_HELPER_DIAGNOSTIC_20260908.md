# Issue #6 Windows UI helper read-only diagnostic (2026-09-08)

## Scope and safety boundary

This checkpoint records read-only diagnostics for the Issue #6 Windows UI helper blocker. No Forge Neo files, extensions, models, generation settings, Codex settings, ACLs, installations, updates, or repairs were changed. The Luna premise is preserved: this is an environment/helper diagnosis only; no model-family prompt or configuration conclusion is inferred.

Repository branch at diagnostic start: `codex/issue6-preflight-check`\
Repository HEAD at diagnostic start: `8daef4354113f42bf0fb74e890d693a8418ee5f9`

## Codex configuration

Read-only inspection of `C:\Users\takas\.codex\config.toml` found:

- top-level `sandbox_mode = "workspace-write"`;
- `[windows] sandbox = "elevated"` (not `unelevated`);
- `node_repl` configured to use `C:\Users\takas\AppData\Local\OpenAI\Codex\runtimes\cua_node\b474a88d5d105afa\bin\node_repl.exe`;
- `NODE_REPL_NATIVE_PIPE_CONNECT_TIMEOUT_MS = "1000"`.

No configuration value was edited.

## Versions

- Codex CLI executable: `C:\Users\takas\AppData\Local\OpenAI\Codex\bin\8e5b6932251c2c1c\codex.exe`.
- `codex --version`: `codex-cli 0.153.4` (exit code 0).
- Codex Desktop doctor check: `26.901.6511.0`, running.

## `codex doctor --json`

The command was available and executed read-only. It exited with code 1 and reported `overallStatus: fail`. Captured doctor stderr was empty (the stderr capture contained no bytes).

Relevant structured results:

- `sandbox.helpers`: **fail**. Summary: elevated Windows sandbox provisioning recorded a structured failure. Backend: `elevated`; provisioning: `failed`; error code: `helper_unknown_error`; approval policy: `OnRequest`; filesystem/network sandbox: `restricted`.
- The doctor issue cause is the same `helper_unknown_error`.
- `security.endpoint`: **warning**. Microsoft Defender was detected, but Codex exclusions were unverified. The report listed the signed Codex app, `codex.exe`, `codex-windows-sandbox-setup.exe`, `codex-command-runner.exe`, and `codex-code-mode-host.exe` as exclusion targets to verify. No security setting was changed.
- `terminal.env`: **fail**. `TERM=dumb`; stdin/stdout/stderr were non-terminal; code page 932; effective locale `C.UTF-8`.
- Desktop/app-server handshake and installation checks were otherwise reported as OK.

Doctor's remediation text suggested repairing or reinstalling the Codex CLI. That remediation was **not** performed because this task is read-only and forbids installation/update/repair.

## Node/UI helper stderr and log evidence

The complete direct CUA helper failure returned to the session was:

```text
trusted Node process exited unexpectedly; kernel reset, rerun your request
```

This occurred on both initialization attempts. The prior Issue #6 checkpoint also recorded the exact helper summary:

```text
windows sandbox failed: helper_unknown_error: setup refresh had errors
```

Existing Codex Desktop logs contain these complete `node_repl` startup failures:

- `C:\Users\takas\AppData\Local\Codex\Logs\2026\09\07\codex-desktop-40e57541-853d-491b-becc-5ae9b5382149-6104-t0-i1-022908-0.log:146` — `MCP client for \`node_repl\` failed to start: MCP startup failed: 指定されたパスが見つかりません。 (os error 3)`.
- `C:\Users\takas\AppData\Local\Codex\Logs\2026\09\08\codex-desktop-e536f8ac-a30b-4b69-8f2d-f85fbfa72363-976-t0-i1-021218-0.log:667` — `MCP client for \`node_repl\` failed to start: MCP startup failed: ディレクトリ名が無効です。 (os error 267)`.

The targeted log search found no separate literal `ACL`, `アクセス拒否`, or `access denied` diagnostic. The available setup-related evidence is the structured `helper_unknown_error` / `setup refresh had errors`; doctor did not expose a more specific ACL errno. Therefore an ACL root cause is not established by this checkpoint.

## Verdict

Issue #6's Windows UI helper preflight remains **BLOCKED**. The observed blocker is consistent across the direct trusted-Node failure, two `node_repl` startup path errors, and doctor’s elevated sandbox provisioning failure. This checkpoint makes no repair or configuration recommendation beyond recording doctor’s unexecuted remediation text. Forge Neo, extensions, model files, generation settings, and Codex configuration remain unchanged.

