# #245 — B-lite implementation / after audit

2026-10-02 JST。**Implementation gates PASS / user review before merge・production promotionでSTOP。** Draft PR [#246](https://github.com/takasago181/DanbooruTagTool/pull/246)は未merge、#245はopen。starting/live mainは `a96dcd10d77e85d629e0169669ea26028f88c835`、branchは `codex/issue245-ui-audit`。検証・clean publish対象の最終product source: `788e03e6cec3e0c9181337d9a7fbfcff79abe60f`。後続のreport/evidence commitは製品sourceを変更しない。

IA選択authority: [ユーザーのB-lite決定](https://github.com/takasago181/DanbooruTagTool/issues/245#issuecomment-5944355694)。Phase A/B/Cのbefore証拠・初回FAIL・当初A推奨はhistorical evidenceとして保持。今回の採用案と境界は [implementation contract](B_LITE_IMPLEMENTATION_CONTRACT.md)。新機能laneやproduction applyを開始していない。

## Final IA / action map

| surface | 配置・主な操作 | owner / 意味 |
|---|---|---|
| Global header | 製品名、Forge接続/処理状態、設定 | startupは未確認・通信なし。requested Modelを実loaded modelと表示しない |
| 作成 > Positive / Negative | shared chips、カテゴリ表示、選択/削除/weight、Undo/Redo、検索、英語出力/copy、Raw適用/キャンセル | 既存2 PromptWorkspace / PromptEditorVM。同じraw/order/Recoveryを保持。両側のUndoは独立 |
| 作成 > 生成条件 / Preset | 保存Preset選択→作成で使う、Preset管理、Model/Seed/Steps/Sampler/Scheduler/CFG/Width/Height、現在P/N preview、新Preset保存、明示capability照会 | CreateVMは8項目のworking条件のみ。P/N ownerを増やさない。選択だけではloadせず、saved snapshotや管理draftへ自動syncしない |
| 作成 > LoRAを追加 | 登録済み検索/選択、preview、今回weight/保存preferred weight、trigger選択、tokenのみ / trigger+Positive / Negative明示追加 | Libraryと同じ#229 VM・store・選択・draft。管理用VM/DBの複製なし |
| 作成 footer | origin→現在値/編集済み、8条件summary、入力状態、主操作「生成」 | 現在P/N出力+条件のimmutable snapshot。Preset未保存でも実行。既存#228 serviceがcapability・実PNG round-tripを照合、失敗出力もLibraryへ。fallbackなし |
| 作成 > その他 | PNG読込、両側clip読込/新規/回復、互換送信/現在設定生成、pair送信、Positive出力形式、layout reset | Negative変更なし / 両側置換 / 条件未適用を名称とhelpに明記。回復はRecovery、読込はsource import、追加はappend |
| 作成 > 診断 expander | conflict/duplicate/構文境界、token/chunk、明示token照会 | 既存#232 intelligence。警告のみ。Counter Stepsはtoken照会用で、生成Stepsとは別。自動修正・自動生成なし |
| タグ探索 | navigation、混在検索、browse/facets/related/HOME/groups、共有現在Positive、追加/Undo/戻る、作成を開く、copy | taxonomy/canonical authority不変。selected group後は候補を畳み、contextをbounded scroll化。日本語labelを狭幅で折り返す |
| ライブラリ > 生成画像 | root/scan/cancel/backup、検索/filter/page、preview/annotation/metadata、作成で使う、この条件で生成、左保持/右選択/比較 | #226 store/metadata/annotation flush/missingを維持。再現はsource画像Recipeから直接#228。current stateへのloadは別の明示操作 |
| ライブラリ > LoRA | recursive scan/hash、identity/metadata/override/favorite/note/preferred weight/usage、挿入/copy/Preset化/保存 | 既存#229管理view。通常起動offline、同名を同一identityとみなさない |
| Preset管理 dialog | saved list、管理draft/capture/save/delete、P/N利用/copy、source条件生成、互換送信、作成で使う | modal化。管理draftとworking条件を同時に編集しない。管理からloadする場合はdialogを閉じて明示適用 |
| PNG / Forge設定 dialog | 元のPrompt/条件/raw情報/復元/copy/Preset化、URL/extension配置/保存 | PNGは追加の「作成で使う」でP/N/条件を明示置換。個別復元は維持。Forge設定はmodeless、保存前URL編集の既存意味も維持 |

Positive copyは編集面と探索の現在Promptに残す。headerの重複copyを除去したが、異なる作業面から共有出力をコピーするcontext actionは意図して維持。MainVMの既存forwarderもbindingsとの互換に残す。別Prompt engine・dock framework・DB・runtimeを導入していない。

## Source / persistence / compatibility

- originは未保存working / Preset名 / image名。load後のP/Nまたは条件編集で「現在値は変更済み・未保存」。生成はsource originの古い値ではなく、押下時の現在値をcaptureする。busy中はUI編集/二重送信を停止。
- working生成条件とoriginは**session-only**。終了時破棄とPreset保存を条件画面に明記。P/Nは既存schema2で保存される。新Preset保存は新GUIDのsnapshotで既存を上書きしない。save失敗時は追加分だけ取り消し、current/既存Presetを保持。
- 旧workspace index 0辞書/1Prompt/2画像/3LoRAは保存形式を変更せずshellへ写像する。schema migration追加なし。古い0はタグ探索、1は作成、2/3はLibraryの該当内tabへ。新規起動も従来のタグ探索初期値を維持。
- current条件はall8/fixed seed/8-multiple sizeを要求。保存Presetの部分Recipeは引き続き許容し、実行時に既存API adapterがfail closedで判定する。選択画像が不完全ならcurrent生成も停止。
- 「Forgeへ送るだけ」「Forgeの現在設定で生成」は現在Positive、Negative変更なし、DTT生成条件未適用。pair送信は現在P/N両側置換。画像互換操作はsource画像P/N、条件未適用。保存Preset互換sendの旧契約（現在Positive+saved Negative）も消さず詳細labelで保持。
- Forge実loaded model・他clientの処理状態は未確認。明示capability照会で接続/対応数を取得してもloaded modelとはみなさない。DTT生成のbusy/error/照合完了とLibrary登録失敗はfeedbackを残す。startup network/pollなし。

## Before / after — same 8 tasks

[Phase B](PHASE_B_TASK_AUDIT.md)と同じlogical primary activationの下限。tab/button/list/checkboxのみ、文字入力・field focus・scroll・OS focusは除外。trained routeのsource/render/native-test walkthroughであり、人の所要時間やpointer実測ではない。狭画面scrollのコストは別記する。生成はfake HTTP上の実API adapter+PNG round-tripで確認し、今回live Forge生成はしていない。

| task / 同じ初期surface | before → after | switches / 主要改善・残る負荷 |
|---|---:|---|
| 1 普通生成（辞書resultあり・LoRAあり） | 正確なP/N/条件経路 **14→8** | after: tag追加→作成→Negative→quick LoRA→選択→挿入→条件→生成。top3→1、inner1→3、Preset window1→0。beforeの8手current-settings終点はNegative/条件適用を保証せず、同じ成功指標として比較しない。名前/save/capture迂回不要。8条件入力自体は必要 |
| 2 owned LoRA（作成起点） | **6→6** | quick tab→検索/更新→選択→trigger→挿入→Positive。top2→0、inner0→2。管理metadataを読む必要がなく同じdraftを使用。結果P/N確認は内tabで行う。900高ではactionまでscrollが必要 |
| 3 過去画像再現（画像面） | **3→3** | 検索/更新→画像選択→この条件で生成。現在Promptのload/save不要。source画像metadataとexact APIは従来どおり。別Library内tab起点なら画像tab1手が別途増える |
| 4 2画像比較（画像面） | **4→4** | 左選択→保持→右選択→比較。固定contextの左右filenameで左targetの記憶を不要に。比較はmetadata diff、side-by-side pixel表示ではない |
| 5 generation診断（画像面） | **5→3** | 選択→作成で使う→診断expander。top1維持、P/N/8条件の同時明示loadで対応づける。閲覧のみならLibrary metadataを使用しload不要。診断は警告であり画像品質の真偽判定なし |
| 6 整理（画像選択済み） | **3→3** | favorite→favorite filter→検索/更新。rating/noteは入力/lost-focus別。annotation/missing/flushは維持。「DB保存」を「DBバックアップ」に変更。検索更新時の選択解除は既存仕様 |
| 7 tag discovery（作成起点） | **5→5** | タグ探索→related→group→追加→作成。top2維持。group candidate全件残留による結果surface消失を解消。sharedPositiveとbrowse contextは保持。navigationの日本語はwrap |
| 8 rare operations（各surface） | raw **2→2** / backup **3→3** / PNG **4→4** / current-settings **1→2** | Raw開始/適用は各side。DB backupはLibrary+OS dialogで同じ。PNGはその他→読込→picker→作成で使うでP/N/条件を一括load（beforeはheader→picker→P復元→N復元）。互換生成はmenu1手追加で意味を明示。rareへの1手増をroutine簡素化とのtradeoffとして記録 |

単純な手数減を一律PASS条件にしない。改善の中心はgeneration source誤認・別画面の値の記憶・管理画面への往復・失敗feedbackの位置。8taskのmajor actionはaction map/source bindings/既存focused/fullで対応づけた。意味の異なるcommandは一本化していない。

## Small window / evidence

| native requested = actual DIP | clean-main list | B-lite list | result |
|---|---:|---:|---|
| 900×560 | 0 | **99.33** | selected group45件、元>80を維持、戻る/17候補/filter/labelも保持 |
| 1280×720 | 41.33 | **259.33** | 同上 |
| 1200×900 / 1500×900 | 221.33 / 235.33 | **439.33 / 439.33** | 元#223のnative acceptanceと整合 |

Same Session1、144DPI/1.5、primary/virtual1706.67×960 DIP、work area1706.67×912。Window Normal。geometryと親/行/header/tab寸法は [native-geometry](evidence/after/native-geometry.json)。#223の元test/assertion/skip/MinHeight/文字サイズを変更していない。原因比較は [baseline diagnosis](BASELINE_FAILURE_DIAGNOSIS.md)を保持。

900×560 / 1280×720 / 1600×900 / 2560×1440のPositive/Negative/条件/quick LoRA/探索/画像/LoRA管理/selected-group結果、compareと3dialogの**36 WPF render/tree**: [manifest](evidence/after/renders.json)。描画は96DPIのdetached client viewportでありnative pixel/pointer acceptanceではない。Window ancestor command bindingsがdetached中に無効に見える場合があり、command semanticsはsource/native testsで確認した。四つのrequested sizeのnative WPF testsもPASS。異なるPC/物理display設定へ切り替えた検証ではない。

小画面のcurrent条件summaryはbounded scroll、長いerrorもbounded status。未設定条件でもPositive chips/英語出力を表示。splitterとwide保存幅を維持しsmall adaptationで保存値を上書きしない。Negative側のsplitterも保存、明示layout reset。小画面では条件/quick LoRA/full asset detailをscrollする必要がある。

## Gates / protection

- 最終full Release **355 PASS / 4既存opt-in SKIP / 0 FAIL**。focused #223/#226/#228/#229/#232/#245 **103 PASS / 1既存live-Forge SKIP / 0 FAIL**。新規skipなし。[TRX](evidence/after/full-results.trx)、[focused TRX](evidence/after/focused-results.trx)。新#245は15 cases（navigation4、Create7、native4）。既存API mock経由の1画像/1batch PNG実metadataとLibrary索引を成功/CFG mismatch双方で確認。
- Build 0 warnings/errors。product headのGitHub **9 checks SUCCESS**: [CI](evidence/after/ci-product-head.json)。#223/#216 assets/runtime、#226、#145/#147/#150、advisory。full355はWindows local gateでありCIのfull件数とは混同しない。
- Clean canonical self-contained win-x64 publish PASS、124,895 catalog rows、loose DLL/PDBなし。[runtime manifest](evidence/after/runtime-manifest.json)。source `788e03e6…`、EXE SHA256 `27B11324A5DC778396059D1EA7F91E6D3C18E636D30D686E15D3502133214AA6`、catalog SHA256 `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F`（productionと一致）。candidate: `C:\Codex\DanbooruTagTool\.staging-issue245-portable-reviewed`。
- 上記EXEの隔離Prompt/Negative・LoRA・Library runtime hooks全PASS、通信/実generation0。[Prompt](evidence/after/prompt-intelligence-runtime.json)、[LoRA](evidence/after/lora-runtime.json)、[Library](evidence/after/library-runtime.json)。別folderコピーの通常App startup→正常終了→restartもPASS。schema2・旧workspace3・Nav/Prompt幅・ratio・window size・出力形式・Forge URL・P/N/presets保存を照合: [normal restart](evidence/after/normal-startup-restart.json)。初回の固定3秒待ちではcatalog起動前に判定したためharnessだけ最大30秒の実MainWindow待ちへ変更。製品startup codeへのhackなし。
- 9 protected runtime/catalog/UserData file hashes全一致。[protected hashes](evidence/after/protected-hashes.json)。Core/Data、catalog/research/#179/#180/#216/#223 accepted authority、legacy/dataの変更0。既存UserData reset/migrationなし。元のdirty checkoutをreset/clean/switchせず、task worktree内だけ変更。scope review PASS。
- Production `C:\Codex\DanbooruTagTool-App`は未変更、source **`49963dc129a1725c8a74d7f29aeb960884b67569`**を維持。#228/#229/#232および本PRは未適用。新機能#230/#231/#233–#237へ進んでいない。

## Known limits / next

Live Forge capability/実生成は今回未実施。previous #228実Forge証拠を今回の新smokeとは呼ばない。native pointer user study、別PC、全四physical display modeは未確認。working条件は明示されたsession-onlyで、restart後はPresetをloadする。条件入力はtext fields + explicit capability確認で、model等の自動選択/自動推奨は追加していない。小画面のscroll、Library full管理密度、既存modeless PNG/設定とforwardersは残る。

OSS provenance: #241とPhase Cに記録済みのbehavior/IA研究を参照。今回新しい外部sourceやcodeのcopy/portなし。DTTの既存#226/#228/#229/#232のview/model/serviceを再利用する**clean composition/reimplementation**。architectureに合わせて大規模dock/engine移植を避けた。

**Next: User review before merge / production promotion。** 実装・after監査・local/CI/publish/runtime gatesをreviewできる状態で停止。自動mergeしない。レビュー後の変更があれば該当Gateを再実行し、production promotionは別の明示判断。
