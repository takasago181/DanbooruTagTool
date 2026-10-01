# #225 — STOP POINT / UI・UX consolidation待ち

2026-10-02 JST。指定された #228 / #229 / #232 の実装・tests・PR・CI・merge・Issue/#225 checkpointを完了し、新しい大型機能の実装を停止した。以下は現状の記録と次フェーズの検討案であり、UI再設計の実装ではない。#225全体のroadmapは未完了のためOPENのまま。

## Main / completed

Starting main: `70838a55c6d914d60d1450bbaa87a8e00a223f06`。
機能完了main snapshot: `761e71215f0eb4ccc108761aad0a2c8846a5e8d8`。この後は本report/routingのdocumentation-only closeout。最終mainはlive GitHubを取得すること。

| Issue | branch / source head | PR / merge commit | tests / CI | 主な実装 |
|---|---|---|---|---|
| #228 COMPLETE | `codex/issue228-forge-api` / `2be77c2118f054f31c16d4efe03eeddd9d9b2e93` | [#240](https://github.com/takasago181/DanbooruTagTool/pull/240) / `36b52ca353fff6d4283840397ae2324f3e296e4b` | focused 25; full/protected 301 PASS / 4 opt-in SKIP / 0 FAIL; CI 8 SUCCESS | API-first GenerationRecipe、Model/Seed/Steps/Sampler/Scheduler/CFG/Width/Height/Positive/Negative、1画像bounded生成、actual PNG→Library照合、不一致保持、model restore検証 |
| #229 COMPLETE | `codex/issue229-local-lora` / `ed81241ba07366e08f713e1677e557bb10621cb7` | [#242](https://github.com/takasago181/DanbooruTagTool/pull/242) / `7ca83e08e0d47cd5a10cb20baa0c6e128ec12af1` | focused 12; full/protected 313 PASS / 4 SKIP / 0 FAIL; CI 9 SUCCESS | offline再帰scan、size/mtime hash skip、SHA identity＋path別inventory、sidecar/embedded/preview、user override、category/favorite/note/weight/relations/recipe、明示Prompt挿入・Preset連携 |
| #232 COMPLETE | `codex/issue232-prompt-intelligence` / `2f9d76b3d2bca1eda43e93bfeceaa46bd9167ed4` | [#243](https://github.com/takasago181/DanbooruTagTool/pull/243) / `761e71215f0eb4ccc108761aad0a2c8846a5e8d8` | focused 27＋Python adapter 7; full/protected 340 PASS / 4 SKIP / 0 FAIL; CI 9 SUCCESS | 既存Workspace再利用のNegative、独立Undo/Recovery、schema2保護移行、PNG/Library/Preset/LoRA連携、canonical duplicate/conflict警告、lossless BREAK/AND、source/model-aware token adapter |

全機能でclean self-contained publish、disposable Windows起動・UserData health・strict runtime shape、scope review、clean task worktreeを確認した。#228は実Forge Neoのbounded request 3回→actual PNG 3枚→既存Libraryへの全10項目round-tripとcheckpoint復元を検証。#232の最終EXEでPrompt/Library/LoRAの3つの明示acceptance hookがPASS。900x600・1400x900のNegative WPF表示を確認し、短いpaneでchipが読める小調整だけを実施した。

外部OSSのexact revision/license/reviewed functions、copied/ported無し・behavior/protocol reference/adapterの判断は各 `docs/issue228/IMPLEMENTATION.md`、`docs/issue229/IMPLEMENTATION.md`、`docs/issue232/IMPLEMENTATION.md` に記録済み。

## Current UI map

| workspace / tab / pane | 主な機能・操作 | 主要導線・状態の所在 |
|---|---|---|
| 共通header | Positiveのclipboard読込、新規、Recovery、コピー、出力形式、Preset、単PNG読込、旧Forge送信/current-settings生成、Forge設定 | 全workspaceの上。現在のPositiveに対する操作。旧Forge送信はNegativeを変えない |
| 辞書・検索 / 左 | General/Special、Character/Copyright等のnavigation、HOME/Browse Group、既存accepted taxonomy | immutable catalog/overlayを読む |
| 辞書・検索 / 中央 | 日本語/英語/混在検索、Browse結果、BODY/THEME等の絞込、関連Browse、明示追加/削除 | tag選択→現在のPositiveへ追加。研究authorityを編集しない |
| 辞書・検索 / 右 | 現在のPositive chip、EN表示、未解決、削除、Prompt編集へ、コピー | 編集本体と同じWorkspace。Negative編集の入口はPrompt tab内 |
| Prompt編集 / Positive | 同じ既存chip/order/category表示、複数選択、weight、Undo/Redo、内検索、English preview/raw direct edit | dictionaryと共有Positive Workspace |
| Prompt編集 / Negative | Positiveと同じeditor/view構成、独立chip/raw/Undo/Redo、Negative読込/新規/Recovery | separate Workspace snapshot、同じuser.dbにatomic保存 |
| Prompt編集 / Negative上部 | 明示 `Positive + NegativeをForgeへ` | 両側置換、空Negativeも置換、生成は開始しない |
| Prompt編集 / 診断expander | canonical重複/両側競合/raw警告、BREAK/AND node境界、Steps指定・明示Forge token照会 | 警告のみ。tokenは照会時URL/model/hash/engine/tokenizer/contractを表示。未取得は推定しない |
| LoRA Library / 左 | 登録root、手動scan/hash検証、検索/favorite filter、100件paging、path/hash/copy/usage一覧 | `UserData/lora-library.db`。startup scan/hash/network無し |
| LoRA Library / 右 | selected-only preview、出典/base model、category/favorite/weight、trigger選択、links/note、user override、Recipe Positive/Negative | LoRAだけ/Recipe挿入、trigger/Negativeコピー、明示Negative追加、Preset化、保存 |
| 生成画像 / 左 | root追加/scan停止再開、scan/cancel、DB backup、検索/metadata filter | separate generation-library.db / thumbnail cache |
| 生成画像 / 中央 | thumbnail一覧、100件paging、画像選択 | PNG/対応metadataの個人Library |
| 生成画像 / 右 | preview、画像/場所を開く、favorite/rating/note、Positive/Negative、raw metadata、画像間diff | Positive復元、独立Negative置換、Preset化、旧送信/生成、画像Recipe API生成→actual result自動索引 |
| 生成プリセット dialog | saved list＋editor、Positive/Negative capture、任意Recipe、保存/削除 | Positive追加、独立Negative置換/コピー、旧Forge送信、保存PresetのRecipe API生成 |
| 単PNG import dialog / Prompt・生成条件・生データ | metadata読込、Positive復元、独立Negative置換/コピー、Recipe draft作成 | Library登録を経由しない既存入口。読込だけではWorkspaceを変えない |
| Forge設定 dialog | loopback URL、extension配置先、明示保存/配置 | current-settings compatibility BridgeとAPI-first Recipeは別path。勝手な再起動なし |

現在の流れは `タグ探索 → Positive/Negative → LoRA → Presetの生成条件 → Forge → 生成画像Library → Prompt/Presetへ再利用`。全体を横断する統一された生成条件paneはまだない。LoRA・Library・Presetは独立したsurface/dialogを行き来する。

## UX debt — 観察とsource inspection

- 共通headerの操作数が多い。900x600 WPFでは右端のForge/出力/コピー操作が画面外に出る。全headerの再設計は行っていない。
- 辞書は左navigation 240px・中央結果320px・右Prompt360pxの最低幅があり、900px級では横方向に窮屈。右のPositive状態は便利だがNegativeが見えない。
- Positiveのコピーはheader・辞書右pane・editor previewに重複。読込/新規/RecoveryのheaderとNegative専用barは対象が異なる。Negative tabでもheaderはPositive対象なので初見では取り違えやすい。
- Forge送信の対象が場所で異なる。共通header＝現在Positive/Negative unchanged、明示pair＝両Workspace、Preset旧送信＝現在Positive＋Preset Negative、Library＝選択画像の両側、Recipe API＝選択Recipeの両側＋条件。ボタン名だけでは差を説明できない。
- Presetはdialog、LoRA/Libraryはtab、条件はPreset内expander。現在のPromptに条件を揃えてAPI生成するまでの移動が多い。保存済みPresetと未保存draft、画像Recipeの区別も見落としやすい。
- PNG importとLibrary selected detailはPrompt/条件/metadata/restore/Preset化が重複する。単PNG読込を残す価値とLibrary中心の導線の整理が必要。
- `Prompt / Positive`、`Preset / プリセット / レシピ / Recipe`、`復元 / 回復 / 置換 / 追加`、`Forgeで生成 / Recipe API生成`の用語揺れ。Undoと置換前Recoveryは異なるので意味を消さず統一したい。
- 一部Preset fieldラベルに旧 `Model/Sampler/Scheduler参照・手動` が残り、Recipe API生成の説明と並存している。旧Bridgeでは正しいが、API pathでは誤解を招く。
- LoRA詳細はcategory/base/trigger/relationships/preview/recipeが長い。頻繁な挿入/保存は上に移したが、使用頻度の低いhash検証はtoolbarに同列。編集の未保存/保存済み状態がもっと見えるとよい。
- Library右paneはannotation、両Prompt、raw metadata、Forge操作、diffが集中。全metadataが初期展開され、再利用操作より情報量が目立つ可能性がある。
- 警告は診断expander内。raw/unknownはForge構文エラーではないが、初見では強いエラーと受け取られやすい。実token結果も特定時点のモデルのUI counterで、モデル変更後は再照会が必要。
- MainViewModelにchild ViewModelへのforwarding members/Commandsが多数残る。大半は同じCommand参照で、独立engineの複製ではない。PNG/Library/Presetのrestore wrapper・status表現の共通化余地がある。
- WPFの単PNG dialog、旧Prompt-current-settings BridgeとAPI Recipe pathが並存する。旧Gradio DOM Recipe automationは復活させていない。旧Python/Tkはreference/protected legacyで、WPF runtimeの画面ではない。削除/移動はしていない。
- LoRAからPrompt確認はtab選択→file選択→挿入→Prompt tabへ、Negative直接編集はPrompt tab→Negative tab→直接編集→適用が基本。これはsource由来の操作数で、離席中ユーザーの実利用頻度/所要時間を計測したものではない。

## Recommended consolidation — 未実装の検討案

1. 主導線を探索・Prompt作成・生成・結果再利用に整理し、Positive/Negative/LoRAを「現在の作業セット」として見えるようにする。tabの名称/優先順位とPresetの役割を先に決める。
2. 生成前に **何のPositive / Negative / Recipeを使うか** を1箇所で確認できるpane/action summaryを検討する。旧current-settings生成と検証済みRecipe API生成を明確に区別する。
3. 共通headerを頻用操作に絞り、settings/単PNG import/hash検証/backup等はsecondary menuへ。900x600と1400x900双方で主操作・chip・previewが読めるresponsive設計を比較する。
4. Libraryと単PNG importの詳細/再利用操作を共通surfaceへ寄せられるか検討する。Preview→両Prompt→条件→再利用を優先し、raw metadata/diffはsecondaryにする。
5. copy/import/restore/appendの名前・対象を統一し、選択画像・savedPreset・draft・現在Workspaceのscopeを表示する。自動上書き/hidden insertionは導入しない。
6. ViewModel forwarding/restore wrapperを小さな共通command seamへ整理する候補を洗い出す。現行PromptParser/Workspace/store/authorityを置換せず、先に最も短い日常workflowを実測する。

これらは提案のみ。次フェーズでユーザーの代表タスクと優先順位を確認してから設計/実装する。新しい大型workspace追加より先にinformation architecture/workflowを整理する。

## Production / protection / remaining verification

- Production `C:\Codex\DanbooruTagTool-App` は変更していない。source SHA `49963dc129a1725c8a74d7f29aeb960884b67569`、EXE SHA256 `A805FBBD80B735F354AB0CC2FBFE7F4B24A93436243888A6C6A1A4EAE8431FBE`。
- 未適用: #228/#229/#232。最新版candidateはsource `2f9d76b3d2bca1eda43e93bfeceaa46bd9167ed4`、EXE `37903D91C0F562AD494CC51DE9BE8867222FF1762024B496207A0E81AE9B4461`。promotionは別判断。
- catalog SHA256 `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F` は全publish同じ。existing production catalog＋8 UserDataの9 hashは変更0。reviewed catalog/#179/#180/#216/#223、research、legacy/dataは変更0。
- UserData schema2 migrationはdisposableで確認、productionでは未実行。既存Prompt/Preset/favorite/note/Library/LoRA metadataのreset無し。
- 元のdirty checkoutを触らず独立worktreeを使い、task branchesはpush済み・clean。既存ignored/protected dataをcleanupしていない。
- Forge Neo本体/production bridge設定を更新していない。元の127.0.0.1:7860を保持し、#228一時serviceは停止済み。生成smokeは合計3画像、batch/n_iter各1、追加の大量生成無し。
- Native pointer smokeはWindows Python firewall/security promptに遮られた。実EXE/WPF render/command/data workflowsはPASSだが、native pointer、別PC、物理offline切断は未検証。security promptは操作していない。
- #232新companionのlive loaded-model counterは未検証。既存Forge endpoint 404は取得不可として確認。local推定/heuristicを自動適用しない。新extension配置/restartと実token比較はpromotion/UX acceptance時に行う。
- #229 optional network enrichment、#232 optional opposite rulesは許容されたdefer。必須scopeのBLOCKED Issueはない。

## Next

**UI/UX consolidation待ち。** #230/#231はユーザー確認後。#233/#234/#235/#236/#237も未着手のまま停止。依存順はUI整理→必要に応じpromotion/runtime acceptance→#230（安定#228＋#229）/ #231（Forge extension API一致）→その他個別scope、#237最後・default OFF・認証必須・LAN公開無し。
