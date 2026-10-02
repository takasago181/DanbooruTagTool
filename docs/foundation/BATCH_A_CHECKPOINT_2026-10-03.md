# #247 Foundation P0 + Batch A — review checkpoint

状態: **実装・検証完了 / PR REVIEW STOP**。mainへのself-merge、production適用、
Batch B、新機能は実施していない。#247 Epic全体やpost-Foundation LKGの完了宣言ではない。

## 結局何が良くなったか

以前は「過去Issueの成果を順番に重ねる」C#コードをWPFが実行してcatalogを作っていた。
現在は、accepted semanticsを明示したsnapshot + manifestをMaintenance CLIが検証・コンパイルする。
Appは完成したcatalogを読むだけ。同schemaのaccepted snapshotなら、data・path・hash・countを
更新してcompileでき、固定値更新のためC#を編集する必要がない。

SQLite dumpではなく、backend-neutralな既存domain fieldを5カテゴリのgzip JSONLに保存した。
余分なontology/frameworkやCatalogEntry全面分割を作らず、現行意味と順序をそのまま維持するための設計。
入力合計約6.9MB、124,895行。Artist 48,313行も維持している。

## Git / evidence

- 開始live main: `0d76ee2d6df2af6831f88dbfc56436b7bc7daf66`
- branch: `foundation/batch-a`
- workspace/P0 checkpoint: `7d8ed2e2`
- compiler implementation / candidate source: `77899c9a5f4de22d4f5a4a8fba89bcd15eee3e43`
- PRはこのbranchからmainに向けて作成する。最終docs/checkpoint commitはbranch HEADで確認。
- 実production source/LKG: `b3f48c359a8473c8bbf02347487cba5d8dacf96c` のまま。

詳細:
- `CATALOG_AUTHORITY.md`: schema・compile・snapshot差替・rollback。
- `SEMANTIC_PARITY_2026-10-03.json`: installed/新buildのordered all-field比較。
- `WINDOWS_VALIDATION_2026-10-03.json`: candidate publish/startup・UserData SHA。
- `TEST_RESULTS_2026-10-03.json`: full/opt-in/tooling検証。
- `WORKSPACE_AUDIT_2026-10-03.md` と全worktree JSON: dirty原因と恒久対策。
- `P0_WORKFLOWS_2026-10-03.json`: live Actions無効状態。

## 変更と旧buildの関係

- REWRITE: `CatalogAuthorityReader` / `CatalogCompiler`。current manifestがsemantic authorityを所有。
- 新設: `DanbooruTagTool.Maintenance`（WPF依存なし）。`verify` / `compile`。
- Appから旧build sequenceを除去。旧`--build-catalog`は移行先を示して安全に拒否。
- publish/production-contract toolingは新CLIとsnapshot hashesを使用。
- ARCHIVE: DataのIssue-named build owner等15ファイルとresourceを
  `Tests/LegacyCatalogBuild`へ移し、test-only oracleとした。過去test/evidenceは維持。
- DELETE: XAML/current resultsから未参照のSpecial-only facet options/commands/filter/historyとVM。
- KEEP: SpecialBrowseV2/UnifiedBrowse runtime semantics、関連表示、Prompt/Negative、UserStateStore、
  Generation Library、LoRA、RuntimeCatalogIndex、Forge/Recipe boundary、canonical/identity。
- P0: 指定Issue70 workflows 2本をlive Actionsで`disabled_manually`にし、YAMLを
  `.disabled`として100%同一bytesでarchive。明白な他の直接main pushは見つからなかった。

旧buildは同じaccepted inputsで実行し、installed LKGと全行・順序・全field一致を確認してからsnapshotを生成。
そのsnapshotを新compilerでcatalogへ戻し、再び全fieldを比較した。historyはprovenanceとして残るが、
productionがIssue chronologyをbuild architectureとして実行することはなくなった。

## Acceptance結果

| 項目 | 結果 |
|---|---|
| clean Release build | PASS / warning 0 / error 0 |
| full suite | 368 PASS / 7 SKIP / 0 FAIL |
| relevant opt-in discovery / SexualIntent / no-safe search | 3 PASS / 0 SKIP / 0 FAIL |
| 実行したprotected testsを含む合計 | 371 test cases PASS; 残り4 opt-inは対象外 |
| ordered semantic payload / population | 124,895行全field一致 |
| General / Special / Character / Copyright / Artist | 30,629 / 3,059 / 35,278 / 7,616 / 48,313 |
| stable Special identity | 3,059 IDs / canonical・surface・membership一致 |
| adult/hard-niche / SexualIntent / Unified | 全field + 12検索query + 全19 routes × intent × deep-only、body/theme count一致; practical scenario PASS |
| HOME / BrowseGroup / quality projection | 全field一致 / HOME backing 32,942行 / 64 groups |
| 同schema差替 | 別path/hash/count/populationのfixtureをコード変更なしでread成功 |
| 検証拒否/出力保護 | schema/hash/count/identity/path逸脱、既存output、authority/UserData出力拒否PASS |
| Windows | self-contained候補publish・実WPF起動/終了・disposable UserData PASS; WPF tests 11件 |
| real UserData / Library / LoRA | 14ファイルSHA・size・path集合一致; production未適用 |
| workflow P0 | 2本live disabled + source archive |
| worktree tooling | Python 2件 + lifecycle fixture + runtime pipeline contracts PASS |

full suiteの7 SKIPのうち3件を別runで有効化してPASS。
残る4件はlive Forge再生成、過去authority生成、one-time migration export、過去性能比較。
one-time exportは移行時に別途1 PASSを確認済み。新たな生成feature/性能projectは実施していない。
pixel appearanceの独立確認はしていない。XAML変更はなく、WPF fixtureと実startupを検証した。

## dirty worktree再発修正

詳細はworkspace auditに全42 worktreeのpath/branch/HEAD/tracking/ahead-behind/status/ignored分類を記載。
開始43 → clean main追加1 → merge済みで完全空の終了済みworktree除去2 = 現在42（detached 13）。

大量変更の場所は旧root。initial unstaged 2,051件は全て改行差。
全tracked raw bytes調査では2,403件がLF-equivalentで、実ソース編集は0。
rootのuntracked 13,784 entriesには入れ子worktree23件が含まれ、実ローカルartifact/settingsは13,761件。
Git改行設定不一致、古い保存cwd、未退役worktree、staging/browser/publish/log除外不足が再発経路。

元ファイルは書き換えず、worktree-specific Git設定・local excludes・versioned ignore/attributesを修正。
元rootと新main入口はclean。未保存research65件とKNOWLEDGE5件は保持・復旧コピー済み。
unique history/protected ignored files/他chat ownershipのあるworktreeも保持した。
reset/clean/stash drop、protectedデータの削除、全branch整理はしていない。

新main入口は `C:/Codex/DanbooruTagTool/.worktrees/main`。
旧rootはcompatibility/protected-data/recovery用。helperはclean mainからIssue専用worktreeを作り、
dirty/ignored/未mergeの終了操作を拒否する。軽量診断のstale-worktree advisoryは継続して見える。
既存chatの保存cwd変更はapp toolでは行えず、古いroot自体をcleanにしたうえでlayoutとAGENTSに入口を明記。

## 残ったリスク / 次の判断

- 新semantic snapshot自体の採用はsemantic review対象。manifestを書き換えれば自動で「accepted」になるわけではない。
- domain schema/vocabularyが変わる場合はC# / schema version変更が必要。
- SQLite metadata/provenanceが変わるためcatalogファイルSHAは旧LKGと異なる。payloadは一致。
- ignored inventoryは権限不足の古いbackupに対してlower bound。未知内容は未削除。
- default .NET bin/objは既存test fixtureとの互換のためtask内でignored保持。除去toolは保護対象と同様にrefuse。
- 他chat所有の42 worktree全整理や旧workflowの一括整理は未実施。scopeをBatch Bへ広げていない。
- runtime promotionとpost-Foundation LKGはこのPRレビュー後の別判断。rollbackは既存LKGと旧source/oracleで可能。

**STOP: PRレビュー待ち。** Batch B開始前に、このauthority/compiler境界とparity evidenceを確認し、
accepted input/provenanceの依存先を踏まえてcold evidence/worktreeの個別recovery/ownershipを判断する。
