# Stage 7A Special-first UI Report

## Inventory and framework

The Stage 6.5 production package had no UI entry point, launcher, screen, or
clipboard utility. It already provided `TagSearchEngine.search_one()`,
`PromptSession`/`CoreTagSet`, `PromptFormatter`, `GenerationProfileStore`, and the
Stage 6 `RecommendationEngine`. Two reference prototypes use Tkinter, but their
old data and pair-cooccurrence code were not reused.

Stage 7A adds one production Tkinter window, `python -m danbooru_tag_tool`, and
`START_DANBOORU_TAG_TOOL.bat`. Tkinter is part of standard Windows Python; no
package or UI framework dependency was added. The Stage 6 recommendation API was
inspected but is not connected.

## Implemented UI contract

The screen has one Japanese/English search field, Special-first and secondary
Danbooru result areas, ordered “選んだSpecial” and “補助タグ” areas, warnings that
collapse when empty, a hidden Stage 7B recommendation boundary, and a read-only
Prompt preview with “Promptをコピー”. Up/Down, Enter/Tab, Escape, and mouse click
paths are wired. Both result Listboxes have explicit standard vertical
Scrollbars connected in both directions (`yscrollcommand` and `yview`). Mouse
wheel and keyboard behavior remain the standard Listbox behavior. Copy feedback
is non-modal.

The production result row is a single Listbox line in the form
`日本語 / English`. Stage 7A does not implement a two-level card layout.
Both Listboxes use `height=1` only as their requested minimum and expand through
Tk grid weights. The supported minimum window size is 900x540; Prompt preview is
kept in its own bottom grid row at the normal, minimum, and maximized sizes.

`SpecialSearchPresenter` keeps the Stage 4 parent result order and expands each
canonical result's `special_ids` into distinct cards. It deduplicates only the
same Special ID reached through multiple paths. Within one parent result, exact
Special term/Japanese matches and prefixes are presentation-only tie-breaks.
Stage 4 search results and ranking are not modified.

Selection stores ordered Special IDs. Prompt output uses the corresponding
original `SpecialTag.term` through `PromptFormatter`; Alias and semantic-unmapped
Specials are not rewritten to statistics canonicals. Ordered Manual Auxiliary
state stores canonical identity separately and appends prompt-friendly canonical
text after all selected Specials. Duplicate IDs/canonicals are ignored and no tag
is injected automatically.

General cards use only `JapaneseOverlay.display_by_canonical` as a formal
Japanese display. Search-only Japanese remains a search key and falls back to
English canonical display. When no General result exists, the entire General
LabelFrame is removed and its row weight becomes zero. Existing General search
and selection behavior is restored unchanged when one or more results exist.
The unconnected Stage 7B related-candidate controls are hidden and consume no
Stage 7A height.

## Warning mapping

Physical notices are emitted only when the matching tag-level override is
explicitly `true`:

|Metadata|UI message|
|---|---|
|ActorRequirementOverride|誰が行うかを決める必要があります|
|BodypartRequirementOverride|対象の身体部位を決める必要があります|
|ImplementRequirementOverride|使う器具・物体を決める必要があります|
|PoseRequirementOverride|姿勢・体位を決める必要があります|
|CameraRequirementOverride|見せ方・カメラ位置を決める必要があります|
|SpatialAssignmentOverride|どこに何を配置するか決める必要があります|
|ACTOR_SEPARATION_REQUIRED|複数の人物を描き分ける必要があります|
|MODEL_DEPENDENT|モデルによって出方が変わりやすいタグです|
|PROVISIONAL / PROVISIONAL_CORRECTION / REVIEW_REQUIRED|このタグは意味・構造情報の一部が未確定です。タグ自体は使用できます|
|No unique statistics canonical|このSpecialは関連候補の統計計算には使えません。Promptにはそのまま入ります|
|Same statistics canonical|このSpecial同士は統計上、同じタグに対応しています。どちらも自動では削除しません|

Family membership, blank/None fields, ShapeConflictGroup, composition-owner
inference, content category, and statistical compatibility do not produce
warnings. Notices never block, alter, inject, reorder, or delete selection.

## UX smoke and visual evidence

`benchmarks/stage7a/ui_smoke.json` records deterministic production-data cases:

- 拘束 → Special ID 1897 → original term `bondage` → preview/copy equality
- 断面 → Special ID 2003 → explicit `needs_camera` only → `cross-section`
- 機械 → 22 Special-ID cards → selected ID 1847 remains `mechanical tentacles`
- semantic-unmapped ID 4 → no canonical → statistics notice → `bare anus`
- Alias ID 66 → original Alias term `fuck`
- 青い空 → no Special selection → Manual Auxiliary `blue_sky` → `blue sky`

For the normal path, search input is followed by one click to add a Special and
one click to copy: two clicks after typing. Warnings require no modal or extra
confirmation click.

Windows実機へPython.org配布のPython Install Manager 26.3と、64bit Python
3.12.10 runtimeを導入した。Codex runtimeと同じ3.12系を選び、ユーザー既定を
`PYTHON_MANAGER_DEFAULT=3.12`へ固定した。`py --version`と`python --version`は
どちらも3.12.10を返し、`where py`はPython Manager alias、`where python`は
`%LocalAppData%\Python\bin\python.exe`を先頭に返す。Tkinterは8.6、実際の
`tk.Tk()`生成・update・destroyはTk patchlevel 8.6.15で成功した。

Python Manager同梱の3.14.7が存在するため、曖昧な`py -3`は3.14を選択する。
launcherは検証済み環境を使うよう`py -3.12 -m danbooru_tag_tool`へ固定した。
fallbackの`python -m danbooru_tag_tool`は維持している。launcherから実Tk
windowが表示され、新規Microsoft Store windowは0件、通常のwindow closeで
終了した。

`tools/stage7a_real_tk_smoke.py`はproduction windowを実際に生成し、「拘束」
検索65件、General 0件でGeneral frame非表示、Scrollbar commandによる末尾への
移動、先頭Specialの1クリック、「選んだSpecial」反映、Prompt previewの
`bondage`更新を検証した。通常1120x760、最小900x540、最大化2560x1334の
全geometryでPrompt bar、Prompt text、copy buttonがmapped/viewableかつrootの
visible bounds内であることを座標検査した。最小と最大化の両方で、画面上の
copy buttonへButtonPress/ButtonRelease eventを送り、Prompt copy payload一致と
copy feedbackを確認した。最後は`root.destroy()`で正常終了した。結果は
`benchmarks/stage7a/real_tk_smoke.json`、実画面は
`STAGE7A_REAL_TK_SCREENSHOT.png`へ保存した。DPI-aware processとWin32
`PrintWindow`でwindow単体をcaptureしている。スクリーンショットにはproduction
の検索欄、1行Listbox、縦Scrollbar、選択済みSpecial、Prompt preview、
Promptをコピー、copy feedbackが同時に表示され、巨大な空General欄や個人情報は
含まない。
既存の`STAGE7A_UI_LAYOUT_EVIDENCE.png`は構造再現図として区別して保持する。

## Files

New production files:

- `danbooru_tag_tool/ui.py`
- `danbooru_tag_tool/__main__.py`
- `danbooru_tag_tool/stage7a_presenter.py`
- `danbooru_tag_tool/stage7a_session.py`
- `danbooru_tag_tool/stage7a_warnings.py`
- `START_DANBOORU_TAG_TOOL.bat`

New validation and documentation:

- `tests/test_stage7a_ui.py`
- `tools/stage7a_smoke.py`
- `tools/stage7a_real_tk_smoke.py`
- `benchmarks/stage7a/ui_smoke.json`
- `benchmarks/stage7a/real_tk_smoke.json`
- `docs/decisions/STAGE7A_SPECIAL_FIRST_UI_DESIGN.md`
- `docs/stage_reports/STAGE7A_UI_LAYOUT_EVIDENCE.png`
- `docs/stage_reports/STAGE7A_REAL_TK_SCREENSHOT.png`
- this report

`README_最初に読む.txt` was updated only with the Stage 7A launcher instructions.

## Validation

- Windows Python: 3.12.10 64bit via Python.org Python Install Manager 26.3
- packages: pytest 8.4.2, NumPy 2.5.2, PyArrow 25.0.1
- Stage 7A targeted: 21 passed (Windows Python 3.12で実行済み)
- Stage 7A + Stage 6.5 + Generation Profile + Stage 6 recommendation: 64 passed
- final full regression: **134 passed in 23.76 seconds**
- real Tk smoke: PASS (normal/minimum/maximized visibility, 65 results,
  General hidden, scroll/select/visible copy click/normal exit)
- launcher smoke: PASS (real Tk window, no new Store window, normal exit)
- runtime external calls in smoke: zero
- RecommendationEngine connection: disabled
- Special2788 SHA-256 unchanged:
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
- canonical source, Alias index, Special linkage, Generation Profile, family
  rules, model observations, and Japanese runtime overlay are byte-identical to
  the preimplementation backup

Environment pre-install record:
`backups/python_env_preinstall_20260906_0830/environment.txt`.

Stage 7A real-Tk change backup: `backups/stage7a_real_tk_pre_20260906_0840`.

Stage 7A vertical-layout backup:
`backups/stage7a_vertical_layout_pre_20260906_0910`.

Stage 7B recommendation aggregation, Stage 8 semantic refinement, Stage 9 Prompt
Composer, persistence, automatic support, weights, LoRA, Negative Prompt, and
advanced Prompt editing were not implemented.
