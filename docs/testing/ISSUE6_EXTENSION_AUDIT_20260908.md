# Issue #6 extension verification audit (2026-09-08)

## Audit scope

Read-only audit of `ISSUE6_EXTENSION_INSTALL_AND_VERIFICATION_20260908.md`, the Issue #6 preflight/execution checkpoints, and the two installed fixed commits. No install, update, rollback, uninstall, or configuration edit was performed.

## Multi Prompt Slots / `ui-config.json`

The installed commit is `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`. Its script registers its own Gradio controls (`ポジティブ・モード`, `ネガティブ・モード`, `シード・モード`, slot textboxes, and utility buttons). Forge's normal UI-state persistence consequently added `customscript/multi_prompt_slots.py/...` entries to `ui-config.json`.

The observed entries are extension-namespaced component visibility/default values. They are the script defaults (`追加`, `画像ごとランダム`, blank order/slot values, and default booleans). The existing main UI values remain baseline values (`txt2img/Prompt/value` and `Negative Prompt/value` blank in the persisted file; base Seed value `-1`), and no checkpoint/model or existing-extension setting was changed. Therefore this hash change is a standard UI component-registration side effect of installing/using the approved extension, not an unrelated settings update.

## Infinite Image Browsing / dependency bootstrap

The installed commit is `ced039479c2e1463c9bdb136d355e01b3dfc9279`. Its fixed-commit `install.py` reads that commit's `requirements.txt`, maps distribution names, checks `launch.is_installed(...)`, and calls `launch.run_pip` only when a declared package is missing. There is no `--upgrade` flag and no repository update operation in this code path.

`imageio-ffmpeg` is explicitly declared in that fixed commit's requirements and the recorded launch observed the extension's own `install.py` invoking the missing-package bootstrap. The installed package is `imageio-ffmpeg 0.6.0` in the existing Forge Neo virtual environment. This is a standard dependency bootstrap for the explicitly approved extension, not an unscoped dependency update; no separate pip command was issued.

## Lock interpretation and verdict

Issue #6's prohibition is read as prohibiting unrelated Forge/extension/model/config changes and unapproved dependency upgrades. It does not prohibit the approved extension's own declared, missing-runtime dependency bootstrap or the normal persistence of that extension's namespaced UI controls. The fixed SHA, remote HEAD, local SHA, clean extension trees, functional tests, and baseline regression are already recorded in the verification report.

**判定: `PASS_WITH_NOTE`**

Note: retain the two observed side effects in the audit trail. They are acceptable standard-install effects under this fixed-commit lock, but future runs must still recheck the locked SHA and must not treat them as authorization for unrelated package upgrades or pre-existing Forge setting changes.
