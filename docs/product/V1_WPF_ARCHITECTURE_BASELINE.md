# V1 WPF / PORTABLE ARCHITECTURE — FIRST IMPLEMENTATION BASELINE

最終更新: 2026-09-13

> **USER-ACCEPTED / FIRST IMPLEMENTATION ARCHITECTURE BASELINE**
>
> 本書は Issue #66 の第一実装におけるアプリ形式・移行・配布構成の正本である。
> 製品目的は `docs/PRODUCT_GOAL_LOCK.md`、UI/interaction は `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md` を優先する。
> 既存 Python/Tk 実装を無理に改造せず、新しい WPF アプリを同一 repository 内へ新設する。

## 1. Architecture decision

v1 first implementation は以下を標準とする。

- C#
- .NET
- WPF
- SQLite
- CommunityToolkit.Mvvm 等の軽量 MVVM 補助
- Windows x64
- local / non-LLM runtime

既存アプリは Python + Tkinter であり、Stage7A/8/9 系UI・recommendation・composer等を含む歴史的実装である。
新v1は情報設計・UI・runtime形式が大きく異なるため、Tk UIを継ぎ足して完成形へ変形することを標準方針にしない。

## 2. New app is a clean implementation, not a Python wrapper

新WPFアプリは新規実装とする。

禁止:
- WPF から Python runtime を必須呼出しする構成
- Python/Tcl/Tkのインストールを新アプリ利用条件にすること
- 旧Stage UIをそのままWPFへ移植すること
- 旧recommendation / automatic support / Generation Profile等を「既にある」という理由だけで移植すること

再利用対象は主に **data / identity / taxonomy / search rules / regression evidence / accepted behavior** であり、Pythonコードそのものをruntime dependencyにはしない。

旧Pythonコードは第一実装中:
- reference
- regression comparison
- accepted behaviorの確認元
- historical implementation

として保持する。

## 3. Repository coexistence during migration

第一実装では既存ファイルを大規模移動しない。

推奨構成:

```text
DanbooruTagTool/
  src/
    DanbooruTagTool.App/        # WPF executable / Views / ViewModels
    DanbooruTagTool.Core/       # Prompt model, search contracts, application logic
    DanbooruTagTool.Data/       # SQLite, Data Pack import/read layer
    DanbooruTagTool.Tests/      # new .NET tests

  data/                         # existing source-of-truth / accepted data assets
  docs/                         # project/product authority

  danbooru_tag_tool/            # existing Python/Tk legacy/reference; keep intact first
  tests/                        # existing Python regression/evidence tests
  START_DANBOORU_TAG_TOOL.bat   # old Python launcher during coexistence
```

実装上必要なら solution/project名は調整してよいが、以下の境界は保持する:
- new WPF code と legacy Python code を混在させない
- source-of-truth data を不必要に複製しない
- #64 の進行中データを UI rewrite のために移動・改変しない

## 4. Do not reorganize existing data before the WPF baseline

`data/` は第一実装開始時点では現位置を維持する。

理由:
- #64 General 30,629 taxonomy が進行中
- existing Python tests / workflows / docs / scripts が相対pathを参照している
- 大規模moveは新アプリ実装とは独立のmigration riskを増やす
- protected / ignored local data がGitHubだけでは完全復元できない

したがって第一実装では:

`existing GitHub/local data -> import/build step -> catalog.db -> WPF app`

とする。

WPF baselineが実Windowsでacceptされた後、必要なら別のcleanup/migration taskとして legacy/source treeの整理を行う。

## 5. Data/runtime separation

標準runtime境界:

### catalog.db

再生成可能なcatalog knowledge。

候補:
- Special canonical identity
- Special Japanese presentation
- #56 taxonomy
- #63 product-fit sidecar
- General 30,629 Japanese overlay
- accepted #64 taxonomy
- approved Alias / search support
- usage count
- 必要なsearch index

`catalog.db` は通常利用時 read-mostly とする。

### user.db

ユーザー固有・再生成して失ってはいけない状態。

第一実装候補:
- current Prompt/session
- one-generation recovery snapshot
- unresolved review queue
- window/workspace state
- splitter widths
- settings

将来のfavorite/history/saved Promptは、実使用で必要性が確認されてから追加する。

### Data Pack / importer

GitHub上のCSV/JSON/sidecar等をsource-of-truthとして保持し、build/importで `catalog.db` へ変換する。
通常アプリ起動時に分類・監査・CSV全再構築を走らせない。

## 6. Portable distribution is the standard user format

標準配布形式:

> **Windows x64 / self-contained / portable folder**

別PCへフォルダごとコピーし、そのまま起動できることを目標とする。

標準要件:
- target PCへのPython installation不要
- target PCへの.NET Desktop Runtime installation不要（self-contained publish）
- installer必須にしない
- registryを通常状態保存の必須先にしない
- machine-specific absolute pathを通常データに保存しない
- executable folderからのrelative pathを基本にする
- network/cloud serviceを通常起動の必須条件にしない

想定配布例:

```text
DanbooruTagTool/
  DanbooruTagTool.exe
  *.dll / runtime files
  Data/
    catalog.db
  UserData/
    user.db
    settings.json   # 必要なら。DBへ統合してもよい
```

`UserData` を一緒にコピーすれば、別PCでもcurrent Prompt・設定・recovery state等を継続できる構成を目指す。

## 7. Portable does not mean single-file executable

`.exe` 1個へ全資産を埋め込むことはv1要件にしない。

優先するもの:
- copyしやすい1フォルダ
- catalog更新のしやすさ
- user data保護
- troubleshootingのしやすさ
- DB/data境界の明確さ

Self-containedにより配布サイズが増えることは許容する。
目標は「最小バイト数」ではなく「数百MB以内程度の実用的な軽量portable Windows tool」。

## 8. Legacy Python lifecycle

### Before WPF baseline acceptance

旧Python/Tk一式を削除・legacyフォルダ移動しない。

理由:
- regression referenceとして価値がある
- path churnを避ける
- source/protected dataとの関係を壊さない
- WPF完成前にcleanup作業を主目的化しない

### After WPF baseline acceptance

別taskとして初めて以下を検討する:
- `legacy/python/` 等への移動
- old launcherの明確なlegacy化
- obsolete runtime code削除
- Python-specific dependencies/testsのhistorical/archive扱い

削除はaccepted data/evidence/provenanceを失わないことを確認してから行う。

## 9. First implementation dependency rule

新WPFは既存Pythonアプリのmodule import/APIを前提にしない。

引き継ぐべきもの:
- canonical identity
- Japanese overlay
- Alias/search synonyms
- #56 Special taxonomy
- #63 product fit
- usage count
- accepted search behavior
- search regression cases
- Prompt preservation rules
- visible-state = copied-Prompt invariant
- #64 accepted output after acceptance

原則移植しないもの:
- Stage-number oriented UI
- recommendation-first UI
- hidden automatic support insertion
- automatic Prompt optimizer
- Generation Profile dashboard
- evaluator UI
- full statistics runtime dependency

## 10. First WPF build route

Issue #66 Phase B first implementation:

1. create new .NET/WPF solution under `src/`
2. establish App / Core / Data / Tests boundaries
3. define catalog import/read contract from existing data assets
4. implement lightweight Prompt workspace shell
5. conservative Prompt import / raw preservation
6. Special browse + usage count
7. Japanese/English/mixed search + known-noise regression fixes
8. explicit add/edit/reorder + English copy
9. autosave/recovery in user storage
10. General provider boundary while #64 continues
11. publish `win-x64` self-contained portable folder
12. Windows acceptance including folder-copy launch test

After #64 acceptance:
- consume accepted General taxonomy
- rebuild catalog
- final search/browse acceptance

## 11. Acceptance checks specific to architecture/distribution

First practical v1 baseline must verify:
- new app launches without Python/Tk
- self-contained publish launches on a Windows x64 machine without separate .NET runtime install
- app can be copied as one folder to another PC/location and start there
- no essential state depends on original absolute path
- catalog and user data are separated
- copying UserData carries user state as designed
- missing legacy Python runtime does not block normal v1 operation
- normal startup does not rebuild taxonomy/audit data
- #64/protected/canonical source data were not weakened by migration

## 12. Source-of-truth relationship

- Product goal: `docs/PRODUCT_GOAL_LOCK.md`
- UI/interaction: `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
- Architecture/migration/portable distribution: **this file**
- Routing: `docs/project/CURRENT_STATE.md`
- Implementation owner: Issue #66
- General taxonomy owner: Issue #64

Implementation details may evolve after real use, but the first build must not silently revert to Python/Tk runtime dependency or destructive legacy/data migration without a new explicit DEV decision.
