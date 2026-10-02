# #245 Phase A — 現行製品のUI監査

2026-10-02 JST。監査baselineはlive main `a96dcd10d77e85d629e0169669ea26028f88c835`。
ユーザーが#245開始を指示したため、#244の「UI整理待ち」からこの専用laneへ移った。新機能停止とproduction未適用の境界は継続する。

**状態: Phase Aのsource棚卸し・指定viewport renderは記録済み。実native画面寸法の検証とbaseline full regressionはBLOCKED。#245全体は未完了。UI変更・Phase C案の採用・promotionはしていない。**

## Authority / 方法

- [live #245](https://github.com/takasago181/DanbooruTagTool/issues/245): Phase A → task audit → 複数IA案 → 選定 → 実装、という順序。
- [#241 research ledger](https://github.com/takasago181/DanbooruTagTool/issues/241)の本文と2件のコメントを読んだ。これはreferenceでありpixel specではない。独立したworking stateを増やさず、操作対象の認識・progressive disclosure・既存操作の発見可能性を評価軸にする。
- [#244 STOP POINT](https://github.com/takasago181/DanbooruTagTool/pull/244)と[既存report](../issue225/STOP_POINT_2026-10-02.md)を読んだ。#226/#228/#229/#232の機能を維持する。
- CURRENT_ROUTING / NOW / CURRENT_STATE / PERMANENT_RULES / PRODUCT_GOAL_LOCK / AGENTSのlive基準を確認。旧#64/#66等の記述をactive laneとして復活させない。
- 実際のXAML、code-behind、composition root、各ViewModel、UserStateCoordinator、UiStateを確認。静的抽出[BASELINE_CONTROLS.csv](BASELINE_CONTROLS.csv)は8 XAML / 189宣言。95 Button / 51 TextBox / 9 TabItem / 5 Expander / 5 ComboBox / 5 GridSplitter / 9 CheckBox / 7 ToggleButton / 3 RadioButton。DataTemplate内の宣言を含むため、同時表示数ではない。
- `scripts/issue245/inventory.py`で再生成できる。bindingsのDataContext、template、tab/expander階層、label、command/callback、width、tooltipを保持した。Click callbackも読むことで、Command名だけの照合を避けた。
- `scripts/issue245/UiAudit.csproj`は開発用の別実行体。製品startup/hook/sourceは変更していない。実App assemblyとMainWindow/view/dialogを使用し、production catalogはReadOnlyで開く。Prompt/画像/LoRAは新規disposable fixture、clipboardはメモリ。通信0・生成0。
- 今回新たに外部OSS sourceをコピー/移植/採用していない。#241の外部比較は既存researchの仮説として引用し、各サービスの最新仕様を検証したとは主張しない。実装判断で追加referenceを使う場合はexact revision/license/reviewed functionsを別途記録する。

## Workspace / tab / pane

| surface | 左 / 中央 / 右 | 主な操作と対象 |
|---|---|---|
| 全workspace共通header | 左の製品説明＋右寄せhorizontal toolbar | 下表の9 button＋出力形式。現在Positiveに作用する操作が主体 |
| 0 辞書・検索 | navigation / search・facet・結果・選択詳細 / 現在Positive | General/Special、Character/Copyright、HOME/Groups、scope、BODY/THEME、content intent/deep filter、関連Browse、tag追加、chip inspect/delete、editorへ、copy |
| 1 Prompt編集 / Positive | chip editor / splitter / English preview・raw edit | 順序/カテゴリ表示、multi-select、delete、Undo/Redo、内検索、weight、drag reorder、copy、direct edit/apply/cancel |
| 1 Prompt編集 / Negative | Negative専用上部bar、その下に同じeditor | 同じ操作を別Negative Workspaceに適用。pair sendは現在の両側を置換送信、生成なし |
| Prompt編集 / 診断 | bottom expander、初期collapsed、最大200高 | Counter Steps、明示token照会、取得時点/model/status、BREAK/AND境界、重複/競合/raw警告。自動修正なし |
| 2 生成画像 | roots/scan/filter / image grid / selected-image inspector | folder再帰scan、取消、backup、検索/条件filter、60件paging、preview/open/reveal、favorite/rating/note、両Prompt、復元/Preset/Forge/API生成、rawmetadata、2画像diff |
| 3 LoRA Library | toolbar＋root/100件list / 固定右detail | manual scan/hash、検索/favorite、selected-only preview、weight/trigger、category/links/note/override、LoRA挿入、Negative追加/copy、Preset化、明示保存 |

辞書の選択詳細はDictionaryWorkspace内部のselected-entry contextual surface。関連Browseは表示上のcontextで、catalog authorityを書き換えない。旧Python/Tk UIはruntime surfaceではなくprotected reference。Gradio DOMによるRecipe条件適用は復活していない。

## Header全操作

| label | binding / callback | scope / 結果 |
|---|---|---|
| クリップボードから読込 | `Main.Import → Prompt.Import` | Positive置換、raw保持、Recovery/Undo。Negativeは独立 |
| 新規Prompt | `Main.New → Prompt.New` | Positiveを新規にする |
| 直前のPromptを復元 | `Main.Recover → Prompt.Recover` | PositiveのRecovery。Undoと別の機能 |
| 生成プリセット | `OpenPresets` | owner付き補助windowをShow/Activate |
| 生成PNGを読込 | `ImportGenerationPngClick` | modal file picker → metadata読込 → 補助window。読込だけでPromptは変えない |
| Forgeへ送る | `Forge.SendToForge` | 現在visible Positive、Forge Negative unchanged、生成なし |
| ▶ Forgeで生成 | `Forge.GenerateInForge` | 現在visible Positive、Negative unchanged、現在Forge条件で生成 |
| Forge設定 | `Forge.OpenForgeSettings` | URL/extension path編集window。自動配置/再起動なし |
| 出力形式: 生成向け / 原形優先 | `Prompt.OutputProfile` | Positiveの出力表現。Negativeには別OutputProfile stateが存在し、共通selectorは作用しない |
| 英語Promptをコピー | `Prompt.Copy` | 現在visible Positiveをclipboardへ |

Negative表示中もこのheaderはPositive対象。画面全体のactive sideを表すtoolbarではない。

## Dialog / modal遷移

| surface / default・minimum DIP | 入り口 / 閉じ方 / state |
|---|---|
| 生成プリセット 860×760 / 720×560 | header、画像Preset化、PNGレシピ作成、LoRA Preset化。**Show()のmodeless window**。同じwindowが開いていればActivate。保存済みlistとdraft editorは同じPresetEditor。Positive追加/Negative置換/copy/Bridge send/Recipe API、capture/save/delete |
| 生成PNGから復元 920×780 / 760×600 | header pickerまたは単PNG drop。modeless。内tab: Prompt / 生成条件 / 生データ。レシピ作成、Positive復元、Negative置換/copy、生成情報copy、閉じる |
| Forge連携設定 700×310 / 600×260 | modeless。URL、extension directory、保存、配置、閉じる。保存前URLはVM上では即時編集される。閉じるはrollbackではない |
| OS OpenFileDialog | PNG選択、single existing PNG。キャンセルは読込なし |
| OS OpenFolderDialog | Library/LoRA root追加。選択後登録、scanは別明示操作 |
| OS FolderBrowserDialog | Forge extension配置先選択 |
| OS SaveFileDialog | Library DB backup出力選択。画像は含まない |
| MessageBox | Preset削除のYes/No確認。外部画像open失敗等のエラー |
| shellへの遷移 | 選択画像をdefault appで開く / Explorerでreveal。DTT Workspace変更なし |

MainWindow closing時に補助3windowを閉じる。Library annotation flush失敗ならclosingを取り消す。scanはcancel要求する。modeless window間で同じ現在Prompt/Forgeを参照するため、別windowで編集したstateが送信に影響する点をPhase Bで確認する。

## 重複 / 類似操作の意味

| 操作群 | 同一 / 類似 / 違い | consolidationで維持する条件 |
|---|---|---|
| Positive copy | header、辞書右、Positive editorの3入口は同じ`Prompt.Copy` | shared command/stateを維持。Negative editorの同じlabelは別command/別出力 |
| Positive Undo/Redo | 辞書「元に戻す/やり直す」とeditor「Undo/Redo」は同じcommandをforward | Recoveryと混同しない。NegativeのUndo/Redoは別history |
| chip削除 | 辞書の×とeditorの×はPositive DeleteOne、選択削除は別parameter semantics | hover-only×に加えてvisible選択削除がある。同じengineを維持 |
| import/new/recovery | header PositiveとNegative barの類似操作 | 対象が別。単純に全て1commandへまとめない |
| PNGと画像Libraryの復元 | metadata sourceが異なる、どちらもPositive/Negativeへの明示Replace | Library全体を単PNG dialogと同一機能とみなさない |
| Preset化 / レシピ作成 | PNG/LibraryはPrompt＋生成条件draft、LoRAはtoken/trigger/additionsからdraft | 自動保存ではない。元の選択stateを保持 |
| Positive追加 vs 復元 | saved PresetはAppendPreset、画像/PNGはReplace | 操作名・previewで差を示す必要。意味を変更しない |
| LoRA + Recipe挿入 | LoRA token＋選択trigger＋Positive追加をappend | GenerationRecipeのModel/Seed等を設定する操作ではない。「Recipe」の二重意味 |
| Negative置換 vs Recipe Negative追加 | Preset/PNG/LibraryはReplace、LoRAはAppendPreset | 空欄置換も意図通り。Undo/Recoveryの対象を維持 |
| DB保存 vs 保存 | Library DB保存はBackup、Preset/LoRA保存はuser editの永続化 | labelが似ていても削除可能な重複ではない |

生成pathの違いは特に重要:

| 入口 | Positive | Negative | 条件 / result |
|---|---|---|---|
| header send / generate | 現在Positive出力 | Forge現状を保持 | sendのみ / current-settings Bridge generate |
| Negativeのpair send | 現在Positive出力 | 現在Negative出力でReplace（空も） | sendのみ |
| saved Preset Forgeへ送る | **現在Positive出力** | saved Preset Negative | sendのみ。Preset Positiveは使わない |
| 画像Forge send / generate | selected image Positive | selected image NegativeでReplace | 条件を適用しないBridge。現在Workspaceの編集状態を使わない |
| saved Preset Recipe API生成 | **saved Preset Positive** | saved Preset Negative | saved Recipe、1画像、実PNG metadata照合、失敗出力も保持/Library索引 |
| 画像RecipeをAPIで1画像生成 | selected image Positive | selected image Negative | metadataからRecipe、同じverified API path |

`MainViewModel`にはchild commandを返すforwardingが多い。今回のliteral検索では55のexpression-bodied forwarder行（property/methodを含む）。独立したPrompt engineの複製ではない。GenerationImport/Library/Presetのsource別adapterもあり、単純な名前重複だけで消せない。

## State ownership / persistence

| state | owner / 保存 | transition・restartの注意 |
|---|---|---|
| Positive / Negative | Mainが各PromptWorkspaceをcomposition、各PromptEditorVM。user.db schema2の別snapshotをatomic保存 | 両側items/raw/order/Recoveryは共有ページ遷移で保持。Undo/Redo historyとselection/direct draftはsession state |
| 表示workspace index | **Positive PromptEditorVM.WorkspaceIndex**をMainがforward、UiState.Workspaceで保存 | shell navigationがPositive VMに所有されている。active Negative sideはIntelligence.ActiveSide、UiStateには未保存 |
| output format | Positive OutputProfileはUiState保存。Negative OutputProfileは独立・未保存 | headerはPositiveを変更する。Negative copyのlabelだけから形式scopeを判断しにくい |
| Promptカテゴリ/複数選択/検索 | 各PromptEditorVM | session。全てがrestart後に復元されるわけではない |
| Recipe / Preset | saved `GenerationPreset.Recipe`はuser.db。生成条件draftはPresetEditorの文字列fields | **現在Workspaceに対する独立したcurrent Recipe ownerは存在しない**。draft保存前、saved Preset、selected image Recipeを区別する必要 |
| Preset draft/selection | PresetEditor、windowを閉じてもVMは生きる | reopenは同じsession draft。別Preset選択/Newはdraft fieldsを置換、unsaved draftをrestart保存するschemaではない |
| Forge | ForgeVM URL/path/RecipeBusy/RecipeStatus、設定はUiState保存 | URL/path editはVMへ即時反映、明示saveで永続化。読み込み済みForge modelを通常startupでは照会しない。Counterは取得時点のmodelである |
| selected image / filters / compareLeft | GenerationLibraryVM、annotation/root/metadataは別DB、cache再構成可能 | session selection/filter/diff。RefreshでSelected=null。favorite/noteは保存、ratingはLostFocus入力＋flush。annotation保存失敗時はselection/closeを守る |
| selected LoRA / draft / filters | LoraLibraryVM、SHA identityのuser metadataは別DB | selection/draft/searchはsession。選択変更前にdraftをretainし、明示saveが永続化。startup scan/hash/networkなし |
| Dictionary browse/query/selection | DictionaryVM＋UiState | query、browse scope/routes/facets/deep/content intent/scroll/entryを保存。ranking/source authorityはimmutable |

この表はsource ownershipの記録。Phase Aだけで全restart/Undo/Recoveryのruntime acceptanceが完了したとは主張しない。

## Pane寸法・保存・density

| surface | geometry / persistence |
|---|---|
| Main | default1280×720、min900×560、startup Maximized。UiState Width/Height/Left/Top、旧height820は720へmigration。WindowState自体はUiState fieldなし |
| Dictionary | nav300 min240、中央3* min320、右400 min360、splitter各8。nav/right幅保存、最低列幅合計936（外側margin/paddingを除く）。900で既に収まらない |
| Prompt editor | editor3* min350 / splitter8 / preview1* min225、ratio default .75をconstructorで適用 |
| ratio persistence | Positive Editor.EditRatioChangedのみSaveGeometryへ接続。Negativeの同eventは接続されない。保存値もPositive ratioから読むため、両側共通保存というUI説明はできない |
| Library | 左220 / splitter6 / grid* / splitter6 / 右330。調節可能だがUiStateへの幅保存なし。左/右はvertical scroll |
| LoRA | list* / 固定right440、splitterなし。toolbarWrapPanel、rightscroll、100件ページ |
| Preset | list380 + gap12 + editor*。右scroll、条件expander初期collapsed。minimum720の時右formは狭い |

## Render / tree evidence

[evidence/renders.json](evidence/renders.json)と同directoryのPNG/JSON。5surface（辞書、Positive、Negative、生成画像、LoRA）×4サイズ＝20、補助window3＝**23 renders**。

- required viewport: **1280×720、1600×900、2560×1440**。追加low-width **900×600**。
- PNG寸法は96 DPIの**client viewport DIP**。OS chrome込みのnative window pixel寸法ではない。
- 初回Window.Showでは全MainWindowのActualWidth/Heightが900×560へ縮められた。指定幅を再設定しても同じ結果。requested dimensionsだけの証拠を採用せず、window.Contentを一時的にdetachして元font/resources/DataContextを保持したviewportをMeasure/Arrangeした。
- このrunのSystemParameters Primary/VirtualScreenはいずれも682.6667×512 DIP（manifest記録）。requested viewportより小さい。画面設定変更やsecurity prompt操作はしていない。
- detached時のAncestorType=Window command binding/IsVisibleの意味はnativeと異なる。JSONはlocal Visibilityとgeometryを記録し、commandの効果・enabled acceptanceには使わない。Command semanticsはXAML＋source＋regressionを使う。
- ScrollViewer内のview外要素は正常なscroll領域。JSONの単純Right/BottomOverflowをそのままUX不具合数として数えない。
- Synthetic PNG/LoRAはユーザーassetをuploadしないためのdisposable fixture。LoRA preview sidecarなし、Library画像は単色fixture。大規模scan/性能評価ではない。

| viewport | 観察 |
|---|---|
| 900×600 | global headerは複数操作が横へはみ出す。辞書の最低幅のため右Positiveも窮屈。Negative専用barはwrapし、その分editorの縦spaceが減る |
| 1280×720 | 右headerの出力selector/copyがはみ出す。辞書は1列結果と現在Positiveが共存。Negativeは別sideのためPositive/条件は見えない。LoRA detailは下へscroll必須 |
| 1600×900 | headerの9button/出力selectorが入る。画像inspectorの再利用/現在Forge生成より下にAPI生成/raw/diffがあるため、それらはscrollが必要 |
| 2560×1440 | headerは収まる、辞書は結果2列へ。画面が広くても生成条件はeditor上に現れず、選択context/操作意味の分離は残る |

検証対象として残す: native DPI100/125/150%、physical keyboard focus、screen reader、各OS pickerの実操作。viewportをnative pointer acceptanceへ代用しない。

## Keyboard / focus

- Main `PreviewKeyDown`: Ctrl+F → 辞書search / Positive内検索 / Negative内検索 / Library検索。**LoRA workspace(3)もelseでDictionary.FocusSearch()へ行く**ため、LoRA検索の専用Ctrl+F routeはない。
- TextBoxにfocusがある時は通常のテキスト編集shortcutを優先。direct editing時はWindowKeyDownをearly return（両側DirectEditingをMainがORする）。
- Ctrl+Z/Y: textbox以外でPositive Undo/Redo。Negative side表示中はNegativeへ。Library/LoRAの非textboxからはPositiveへ到達する点を再配置時に確認する。
- Prompt editor: Ctrl+A全選択、Delete選択削除、Escape選択解除。Negative sideは同じキーのNegative版。chip mouse Ctrl/Shiftで選択、drag reorder。
- Find textbox: Enter次 / Shift+Enter前。一致へscroll。
- Dictionary list: Up/Down、2列時Left/Right、PageUp/PageDown(10行)、Home/End、Enter inspect。Enterはタグ追加ではない。
- Libraryは標準ListBox selection navigation。rating0..5の専用shortcut、global Generate shortcut、workspace shortcut、command paletteは現行実装に存在しない。
- custom button templateにはhover/press/disabled opacityがある。明示的なfocus triggerは定義されない。これだけでkeyboard focus不可とは断言せず、native確認項目とする。hover-only chip×もあるがvisible選択削除操作は残る。

## Status / long operation

- 共通Main.Statusはbottomに表示。copy成功は2秒で消える。通常Bridge send/current-settings generateは終端statusを返すが、同一command内部のIsRunning以外に常時見えるconnection/model状態はない。
- API RecipeはRecipeBusyで再送guard、RecipeStatusで生成中/失敗/照合/出力path。Preset detailとLibraryに表示、最後にMain.Statusへ。UI Cancel buttonはRecipe用に存在しない。#228の条件検証を弱めない。
- Library scanはBusy/status、CancelScan、未完了root transaction rollback。root「停止」はscan対象disableであり、実行中cancelの「中止」と別。
- LoRA scan/hashはBusyによりtoolbar/editをdisable、終了件数/status。Cancelボタンはない。
- token照会は明示action、モデル未読込/取得不能を表示、local75-token推定なし。診断expanderは初期閉じているため警告は常時は見えない。
- Forge設定の旧説明「画像生成やGenerate操作は行いません」は設定window自体の説明だが、連携全体の説明として読めば現在header/Recipeと矛盾する。用語監査に残す。

## Phase A検証 / blocker

- source/App/Core/Data/tests差分0。製品機能追加0、production apply0、extension配置0、generation0、既存UserData open/migration0。catalogはread-only。
- Audit helper Release build/runと23 exact-viewport render/geometry出力は成功。CSVは再生成一致、JSON/PNG寸法を検証。
- 同じbaselineのfull protected-source Release: **338 PASS / 4 SKIP / 2 FAIL**。SKIPは既存opt-in（#118 authority build、ordinary staging、live Forge、#199 performance）。
- FAIL: `Issue223WpfTests.RealWpfGroupButtonsBindWrapFilterAndReturn(1200)` / `(1500)`、line66 `DictionaryList.ActualHeight > 80`。focused repeatでも2 FAIL。製品source変更前の失敗なので、今回のUI変更regressionとは分類しないが、green baselineとも扱わない。
- local native windowが900×560になる観測と同時発生している。**環境要因との関連は仮説、根因未確定**。テストskip、threshold低下、software-render強制はしていない。
- 再開条件: geometry原因を切り分け、既存native WPF assertionの意図を保ったままbaseline full regressionをgreenにする。正常な表示環境での再確認、または製品側の実際のsmall-window defectを特定したfocused修正が候補。security/system settingsは変更しない。
- Phase Aでは新portable runtimeのpublish/promotionはしていない。前回feature gatesを今回のgreen証拠として流用しない。#245 merge gateは未到達。

## Next

Phase Bでは#245の8タスクについて、同じ初期stateでworkspace switch/modal/primary clicksを記録する。下記を特に区別する:

1. current-settings生成とverified Recipe生成（条件を渡すならsaved Preset経由の手数）。
2. LoRA-onlyとtrigger/Positive recipe追加、別Negative追加。
3. selected imageからの直接Recipe生成と、Workspace復元→編集→再生成。
4. 左保持→右選択→比較。直接2枚multi-selectではない。
5. metadataを見ることとPrompt conflict診断、tokenの取得時点。
6. favorite/note即時保存とrating LostFocus、refresh時のselection。
7. tag exploreのbrowse位置とshared Positiveを維持する往復。
8. raw edit、DB backup、PNG import、compatibility pathの発見可能性。

Phase Cで少なくとも2つの現実的IA案を比較する。#241仮説の機械的採用、新current Prompt engine、free docking、新DB、新機能を前提にしない。baseline blockerとbefore証拠を解消・補完してから製品UI実装へ進む。#230/#231とproductionは引き続き未開始。
