# V1 WPF ARCHITECTURE — FIRST IMPLEMENTATION BASELINE

最終更新: 2026-09-14

> **USER-ACCEPTED / CURRENT ARCHITECTURE BASELINE**
>
> 本書は Issue #66 のWPFアプリ形式・runtime境界・data分離・移行方針の正本である。
> 製品目的は `docs/PRODUCT_GOAL_LOCK.md`、UI/interaction は `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md` を優先する。
> Portable/self-contained配布は2026-09-14のユーザー決定により practical v1 completion Gate から外れ、optional/post-v1へ変更された。

## 1. Architecture decision

WPF v1は以下を標準とする。

- C#
- .NET
- WPF
- SQLite
- Windows x64
- local / non-LLM runtime

既存Python + Tkinter実装はlegacy/referenceであり、新WPF runtimeの必須依存にしない。

## 2. New app is a clean implementation, not a Python wrapper

禁止:
- WPFからPython runtimeを必須呼出しする構成
- Python/Tcl/Tk installationを新WPFアプリ利用条件にすること
- 旧Stage-number UI / recommendation-first UIを実装済みという理由だけで移植すること
- hidden automatic support / automatic Prompt optimizer / evaluator UIをv1 defaultへ戻すこと

再利用対象:
- accepted data
- canonical identity
- Japanese overlay
- Alias/search support
- #56 Special taxonomy
- #63 product-fit sidecar
- usage count
- accepted search rules/regression evidence
- Prompt preservation rules
- accepted #64 output after acceptance

## 3. Repository coexistence during active migration

Current structure:

```text
DanbooruTagTool/
  src/
    DanbooruTagTool.App/
    DanbooruTagTool.Core/
    DanbooruTagTool.Data/
    DanbooruTagTool.Tests/

  data/
  docs/

  tools/legacy/python/danbooru_tag_tool/  # legacy/reference
  tests/                # historical/regression evidence
```

Active rules:
- WPF codeとlegacy Python codeをruntime上で混在させない
- source-of-truth dataを不必要に複製しない
- #64進行中dataをUI作業の都合で移動・改変しない
- protected/ignored local dataをGitHubだけで復元できると仮定しない

Broad legacy/data tree cleanup is separate from current #66 completion.

## 4. Data/runtime separation

### catalog.db

再生成可能なread-mostly catalog knowledge。

主対象:
- Special identity/Japanese presentation
- #56 taxonomy
- #63 product fit
- General 30,629 Japanese overlay
- accepted #64 taxonomy after acceptance
- approved Alias/search support
- usage count
- required lightweight search index

### user.db / UserData

ユーザー固有・失いたくない状態。

対象:
- current Prompt/session
- recovery snapshot
- window/workspace state
- splitter widths
- settings
- unresolved/user-state items where applicable

Favorite/history/saved Prompt等は実利用で必要性が確認されてから追加する。

### Data Pack / importer

GitHub/local source assetsをbuild/importで `catalog.db` へ変換する。
通常起動時にtaxonomy classification / audit / large CSV rebuildを行わない。

## 5. Practical v1 runtime requirements

Practical v1で必須:
- current user Windows環境でWPF appが正常起動する
- Python/Tcl/Tkが通常WPF runtimeの必須依存ではない
- catalog knowledgeとuser-specific stateが分離される
- normal startupがaudit/taxonomy rebuildを要求しない
- machine-specific absolute pathへの不要な固定依存を増やさない
- protected/canonical dataを移行都合で弱めない

`.NET self-contained` 自体は既に動作確認済みの能力として保持してよいが、practical v1の必須配布条件ではない。

## 6. Portable/self-contained distribution is optional

2026-09-14のユーザー決定:

> Portable化は実用v1の完成条件から外す。必要になったら最後またはpost-v1で扱う。

したがって以下は**practical v1 Gateではない**:
- self-contained publishを毎iteration実行すること
- portable folderを標準user formatに固定すること
- separate .NET Desktop RuntimeなしPCでの検証
- second Windows PCへのfolder-copy起動検証
- UserDataを別PCへcopyして継続できることのacceptance test
- installer/portable配布方式の最終決定

既存のself-contained publish能力は削除する必要はない。
将来必要ならoptional distribution taskとして再利用する。

## 7. Artifact policy for development

Routine UI work:
- Debug/Release build
- relevant tests
- real Windows launch/manual interaction

を優先する。

**明示要求がない限りportable publishを毎回行わない。**

Local disposable artifactsは固定pathを使う:

```text
artifacts/current/
artifacts/screenshots/
artifacts/publish/    # publishが明示要求された場合のみ
```

禁止/非推奨:
- `dictionary-...-v1`, `v2`, `v3` のようなversioned publish directory増殖
- `screenshots-v4`, `screenshots-v5` 等を毎回追加
- artifactsをGit commit対象にすること
- cleanup目的の `git clean -fdx` / `git clean -fdX`

Cleanupはtracked/protectedでないことを確認したうえで、既知のdisposable artifact pathだけを個別削除する。

## 8. Legacy Python lifecycle

Current active #64/#66中は旧Python/Tk一式を大規模移動・削除しない。

理由:
- regression/reference価値
- existing scripts/tests/docsのpath churn回避
- protected/source dataとの関係保護

Practical WPF baseline acceptance後、必要なら別taskとして:
- `legacy/python/` 移動
- obsolete launcher整理
- obsolete runtime code削除/archive
- Python-specific historical tests整理

を検討する。

## 9. Phase B implementation status

Issue #66 clean WPF Phase B baselineはlive mainへmerge済み。

Implemented baseline:
1. App/Core/Data/Tests separation
2. catalog import/read
3. Prompt workspace
4. conservative Prompt import/raw preservation
5. Special browse + usage count
6. Japanese/English/mixed search
7. known-noise regression fixes
8. explicit add/edit/reorder/Undo/Redo
9. English visible-state copy
10. autosave/recovery
11. General provider boundary

Self-contained publishは過去にvalidation済みだが、今後のroutine Gateではない。

## 10. Current #66 completion route

Before #64 acceptance:
- practical UX/functionality refinement may continue on the dedicated #66 usability branch
- do not reclassify #64 data
- do not clean-merge the current usability branch until user-facing UX review is accepted

After #64 acceptance:
- consume accepted General taxonomy
- rebuild/refresh catalog
- final search/browse regression
- real Windows practical interaction acceptance
- Prompt round-trip / visible-state copy verification
- practical v1 baseline

Portable/second-PC validation does not block this route.

## 11. Practical-v1 architecture acceptance

Must verify:
- WPF app starts and functions on the actual user Windows environment
- WPF normal runtime does not require Python/Tk
- catalog/user-state separation is intact
- Prompt state and output invariants are preserved
- normal startup does not rebuild taxonomy/audit data
- #64/protected/canonical source data are not weakened
- current UI workflow is practically usable

Optional/post-v1:
- self-contained distribution packaging
- second-PC copy
- .NET-runtime-absent target validation
- portable UserData migration acceptance

## 12. Source-of-truth relationship

- Product goal: `docs/PRODUCT_GOAL_LOCK.md`
- UI/interaction: `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
- Architecture/runtime/data/distribution boundary: **this file**
- Routing: `docs/project/CURRENT_STATE.md`
- Permanent workflow/safety: `docs/project/PERMANENT_RULES.md`
- Implementation owner: Issue #66
- General taxonomy owner: Issue #64

Historical portable-first language is superseded where it conflicts with this 2026-09-14 update.
