# Issue #6 extension install and verification (2026-09-08)

## Scope and lock

- Luna前提。Forge Neo本体、checkpoint/model、既存拡張、生成設定の更新は行わない。
- 承認済みの2拡張だけを、Issue #6 execution lockの固定SHAで導入した。
- 導入前の repository HEAD: `ad6beb6c0afbdfdf8db4d8006adaee0d67675bb5`。
- remote HEADを導入直前に再確認し、両方とも固定SHAと一致した。

| extension | remote `refs/heads/main` | local `git rev-parse HEAD` | install path |
|---|---|---|---|
| Multi Prompt Slots | `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe` | `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe` | `.../extensions/sd-webui-forge-multi-prompt-slots` |
| Forge Neo Infinite Image Browsing | `ced039479c2e1463c9bdb136d355e01b3dfc9279` | `ced039479c2e1463c9bdb136d355e01b3dfc9279` | `.../extensions/sd-forge_neo-infinite-image-browsing-xl` |

Both extension working trees were clean after checkout. No other extension was installed or updated.

## UI and generation checks

After a clean Forge restart on the existing launch arguments:

- Extensions UI listed and checked both new extension directories.
- `Script` dropdown showed `Multi Prompt Slots`.
- Multi Prompt Slots was executed with main prompt `1girl, portrait, simple background, soft lighting`, slot A `blue shirt`, slot B `red shirt`, fixed Seed mode, generation order `1,2`, Seed `5072`.
- Exactly two slot images were produced:
  - `00006-5072.png`: metadata prompt ends in `blue shirt`, Seed `5072`.
  - `00007-5072.png`: metadata prompt ends in `red shirt`, Seed `5072`.
  - Both: 1024x1024, 24 steps, Euler a, CFG 4.5, `waiIllustriousSDXL_v170`, model hash `f116b0c78f`, Neo 2.29.
- Infinite Image Browsing tab appeared. Its UI was opened directly to `00007-5072.png`; the grid showed the generated files and the structured metadata pane displayed prompt, negative prompt, Seed `5072`, model, size, sampler, and Neo version.
- Existing baseline regular txt2img was run once with Script `None`, the baseline prompt/negative prompt, and Seed `5072`. Result: `00008-5072.png`; the UI and PNG metadata matched the baseline parameters.

## Integrity observations

- Existing extension HEADs remained unchanged:
  - ADetailer-Neo `67e973e1c5019c16dcf838364ae391a2752bfa7b`
  - sd-dynamic-prompts `3e62452776f52e2c641c2c52d3cd908140c3743e`
  - sd-forge-couple `c7884e81623d7fcbf4c92e3aea14ced8b5b6aa74`
  - sd-webui-language-diffusion `00cde72ea9203ddd55b14b908d7339ee9075014a`
  - sd-webui-tagcomplete-neo `21ed5859113120bdad6132c438b341a098b7d40a`
  - stable-diffusion-webui-wd14-tagger `ce1b3e31e89e93880407f9bfdfa0e2446b79d83b`
- Forge `config.json` remained SHA256 `1FCD5EACA58DABF87A62C9317A257D9A765CC5E168329453FC7C937BA319E3C4`.
- The pre-install observed `ui-config.json` hash was `2EC310C66BC8C7F3863E0DBAAFB7A6FC59C9254BDF8C051FD64479D5AF568FFC`; after extension UI use it was `3C8443B8D938909A0455D9B512206C09B2AB9FE2D7695D27188ED82211F313C`. The current file includes Multi Prompt Slots component-state keys. This was not manually reverted because the user prohibited additional configuration changes.
- During the first post-install launch, the Infinite Image Browsing extension's own `install.py` automatically ran its `imageio-ffmpeg` dependency bootstrap. No separate package install/update command was issued, but this is an observed dependency-side effect requiring review under the execution lock.
- An initial restart helper command hit a PowerShell reserved-variable (`$PID`) error; it was followed by cleanup and one final normal parent/child Forge process pair. No generated data was deleted or overwritten.

## Verdict

`REVIEW_REQUIRED` (not PASS): the locked commits and functional UI/generation checks passed, but the observed `ui-config.json` mutation and automatic `imageio-ffmpeg` bootstrap cannot be declared compliant with the “設定・依存関係を勝手に更新しない” condition without DEV/AUDIT review. No additional fix, uninstall, rollback, or dependency change was performed.
