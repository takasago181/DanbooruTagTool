# DanbooruTagTool ローカル起動・フォルダ案内

この案内はローカルworkspace内の起動方法を説明します。Issueの状態や実装範囲の正本ではありません。開発を再開するときは `AGENTS.md` とGitHubのlive Issueを確認してください。

## 現在の起動方法

rootにある `START_DANBOORU_TAG_TOOL.bat` は、現在もlegacy Python/Tk版を起動します。WPF版は別のアプリです。

現在の#66 sourceに対応するWPF UI確認用buildは次の場所にあります。

```text
.worktrees/issue66-wpf/artifacts/current/DanbooruTagTool.exe
```

このbuildの `Data/catalog.db` はruntime catalogです。`artifacts/current/UserData/` は今回新しく作った独立領域で、初回起動時に `user.db` が作られます。以前のWPF stateは移行していません。従来のstateを含むportableは `.worktrees/issue66-wpf/archive/artifacts/portable/dictionary-selection-usability-v6/` に保全してあり、その `UserData/user.db` は旧build用として保持しています。旧buildと現在source buildを混同せず、どちらの `UserData` も移動・削除・置換しないでください。

## WPFのsourceと検証出力

- `src/` — clean C#/.NET/WPF implementation
- `.worktrees/issue66-wpf/` — Issue #66 usability refinement用worktree
- `artifacts/current/` — 現在の#66 sourceを使ったlocal validation output
- `artifacts/screenshots/` — 現行UI screenshotの固定先
- `artifacts/publish/` — distribution publishを明示的に行う場合だけ使う
- `archive/artifacts/` — 保持する旧portable / screenshot検証記録

通常のUI修正ではportable publishを繰り返さず、build・tests・Windows launchを行います。portable outputが必要な場合は `src/publish-portable.ps1` を使い、出力先は `current` または明示指定した `publish` に固定します。`*-vN` や `screenshots-vN` の新規folderは作りません。

## その他の主なroot folder

- `data/` — canonical/source/runtime data。整理作業では移動しません。
- `danbooru_tag_tool/` — legacy Python/Tk implementation。WPF runtimeの依存先ではありません。
- `docs/` — product、architecture、Issue、実装と監査の記録
- `tests/` — legacy Python側の回帰・履歴tests
- `tools/` — 開発・検証用script
- `references/` — 過去のprototypeと参考資産
- `.worktrees/` — IssueごとのGit worktree。Git worktree metadataを保ち、手動で移動しません。
