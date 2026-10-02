# #245 Phase B — 8 task audit

2026-10-02 JST / unchanged product baseline `a96dcd10d77e85d629e0169669ea26028f88c835`。
Phase Aの[操作棚卸し](PHASE_A_CURRENT_PRODUCT_AUDIT.md)、[control bindings](BASELINE_CONTROLS.csv)、23 render/tree、今回の[native diagnosis](BASELINE_FAILURE_DIAGNOSIS.md)とsource/testを突き合わせた**expert walkthrough**。人による所要時間・native pointer usability testではない。

数値は再現可能な指定経路のlogical primary activation数（tab、button、list selection、checkbox）。入力文字数、入力field focus、scroll、OS window focusは除外。画面から見切れているactionへ実際に到達する手数は含まないため下限である。top-level switchと内tab switch、modeless補助windowとOS modalを区別する。生成commandの到達と意味を監査し、実Forge生成/通信は実行していない。APIの成功証拠は既存#228 regressionであり、今回の新しいlive generation成功とは主張しない。

共通初期条件: 新規disposable fixture相当の登録済みcatalog / 2 metadata PNG / SHAで区別されるowned LoRA / 空P/N。root登録・scanは準備工程として別扱い。production UserDataや実モデルに作用しない。検索結果・対象が既に分かるtrained pathを数え、初見での探索コストは定性的に別記する。

## Summary

| task / 初期surface | 指定経路のactivation | top switch | 内tab | modeless / modal | 主な迷い・記憶負荷 |
|---|---:|---:|---:|---|---|
| 1 普通生成 / 辞書、tag結果あり | 8（LoRAあり、current-settings終点） | 3 | 1 | 0 / 0 | Negativeも生成条件も共通Generateへ渡ると思いやすい |
| 2 owned LoRA / Prompt | 6（trigger toggle1） | 2 | 0 | 0 / 0 | tokenのみと「Recipe」の意味、別Negative追加 |
| 3 old image / 生成画像 | 3（検索/更新→選択→画像Recipe生成） | 0 | 0 | 0 / 0 | 編集中Promptとは別のselected imageが生成source |
| 4 compare / 生成画像 | 4（左選択→保持→右選択→比較） | 0 | 0 | 0 / 0 | 保持した左画像の同定、metadata diffと画像比較の違い |
| 5 diagnose / 生成画像 | 5（選択→P/N復元→Prompt→診断） | 1 | 0 | 0 / 0 | 画像metadataとcurrent Prompt診断を別画面で対応づける |
| 6 organize / 選択画像あり | 3（favorite→favorite filter→更新） | 0 | 0 | 0 / 0 | rating/note入力は別。保存契機の差、更新で選択解除 |
| 7 discover / Prompt | 5（辞書→関連→group→追加→Prompt） | 2 | 0 | 0 / 0 | フィルタ/context保持は強いがgroup占有で一覧消失 |
| 8 advanced / 各記載surface | 下記4経路を別計上 | 0–1 | 0 | 0–1 / 0–1 | raw/読込/backup/compatibilityの発見と用語 |

タスクごとに都合のよい合算や任意PASS閾値は設けない。1の8手は「現在Negative/Recipeを正確に適用できた」という成功指標ではない。最大の障害は手数ではなく、この目的とcommand semanticsの不一致である。

## 1. 普通の生成

経路: tag追加 → Prompt編集 → Negative内tab（編集）→ LoRA Library → 対象選択（weight入力）→ LoRA+Recipe挿入 → Prompt編集 → 共通「Forgeで生成」。8 activations / top3 / inner1。LoRAなしならtop1 / inner1 / 4 activations（tag追加・Prompt・Negative・生成）。LoRAの追加Negativeも欲しいなら別actionが1増える。

- 迷い: Negativeを編集した直後のglobal headerで生成しても、Forge Negativeはunchanged。条件draftは普通のPrompt Workspaceにはない。送信のみ/現在条件生成/保存条件生成の似た入口から、目的に合うものを選ぶ知識が必要。
- 正確なsaved Recipe生成へは、Preset windowを開く→現在P取得→現在N取得→条件expander→保存→保存済みカードRecipe生成、さらに6 activationsとmodeless1。条件・名前入力は別。**生成sourceは保存済みsnapshot**。編集後の再capture/saveを忘れれば古いPromptで生成する。
- 重複: Positive copy3入口。Negativeにも同じ「英語Prompt」label。header操作のactive-side誤認。
- 記憶: P/N、LoRA挿入結果、保存済みvsdraft、Forge現設定。画面間の戻りで同じstateは残るが一覧確認は必要。
- feedback: Bridge終端はbottom Main.Status、Recipe busy/statusはPreset/Library。常時current Forge model/条件は見えない。tokenモデル表示は取得時点情報であり現在条件の保証ではない。
- source: MainWindow.xaml、PromptEditorView、ForgeViewModel、GenerationPresetDialog、GenerationPresetsViewModel。

## 2. owned LoRAを追加

Prompt → LoRA → 検索/更新 → 選択 → trigger checkbox1 → LoRA+Recipe挿入 → Promptへ戻る。6 activations / top2。weight入力は別。登録rootなしならroot追加・OS folder dialog・scanが前提として増える。

- 迷い: 「LoRAだけ」はtokenのみ。「LoRA+Recipe」はtoken+enabled triggers+Positive additionsであり、Model/Seed等のGenerationRecipeではない。Negative additionsは別button。名前同一/別hashはfail closed、SHA identityを隠して消さない。
- 重複/密度: detailに挿入、copy、Negative追加、Preset化、保存とuser override/管理欄が同時に現れる。挿入に必要なweight/triggerが管理metadataと競合。
- 記憶: 固定440 DIP detailの外にcurrent P/Nが見えない。挿入後にPromptへ戻って確認。draftは保持されるが明示Saveまで永続化されない。
- feedback: statusは挿入/保存/名前解決失敗を区別。scan/hashはBusy、cancelなし。startupはoffline、scan/hashを自動化しない。
- source: LoraLibraryView.xaml/.cs、LoraLibraryViewModel.Insert/AppendNegative/Save、#229 tests。

## 3. 過去画像を再現

生成画像でquery入力 → 検索/更新 → 画像選択 → 「画像RecipeをAPIで1画像生成」。3 activations / switch0 / dialog0。**WorkspaceへのP/N復元は直接再現に不要**。復元ボタン2つを押してもModel等をcurrent Workspaceへ設定する操作にはならない。

- 迷い: 隣の「Forgeで生成」は元画像Model/Seed等を適用しない。外観が似た成功ボタンでも別契約。画像Recipeの再現と「復元後に編集して生成」は別task。
- 記憶: selected imageのP/N/metadataは右detail。current Workspaceが残っていてもこのAPI生成には使われない。source labelが弱い。
- feedback: 保存Recipe不備/capability mismatch/round-trip不一致をfail closed、失敗画像も保存・Library linkage。この安全性をUI consolidationでも保持。通常startupではForge照会なし。
- source: GenerationLibraryViewModel.GenerateRecipe、ForgeViewModel.GenerateRecipeAsync、#228 recipe tests。

## 4. 2枚を比較

左画像選択 → 左画像に保持 → 右画像選択 → 選択画像と比較。4 activations。2枚multi-selectではない。

- 迷い: compareはmetadata difference。画像side-by-side比較表示の保証はない。「左」は保持したmetadataであり現在選択と異なる。右detail下部にcompare入口。
- 記憶: 保持した左を覚える必要がある。新selectionのpreviewは右だけ。left snapshotはsessionのみ。
- feedback: 左保持はStatusで説明され、Differencesが比較結果。compare後のMain.Status成功toastは必須ではない。対象名を常時見せる改善余地。
- source: GenerationLibraryViewModel.SetCompareLeft/Compare、GenerationMetadataDiff、#226 tests。

## 5. generationを診断

画像選択（metadataを読む）→ Positive復元 → Negative置換 → Prompt編集 → 診断expander。5 activations / top1。Negative editorを見るには内tab+1、token実測は明示照会+1（今回通信しない）。復元する経路はcurrent P/Nを変更するので、閲覧だけの目的には不要な変更を伴う。

- 迷い: selected-image metadataのModel/Seed/Steps/Sampler/Scheduler/CFG/sizeと、current P/N conflict/token診断が別owner。画像内LoRA raw textとLocal LoRA detailを対応づける専用自動診断はない。存在しない機能を「監査PASS」としない。
- 記憶: 前画面のModel/conditions。P/N restoreは別action、片側だけ復元した混合状態にも注意。診断は自動修正/生成失敗診断ではない。
- feedback: image metadata absence/parse warning、Prompt raw/unknown/conflict warning、Forge token取得失敗を別で表示。diagnosticが初期collapsedなのでwarning存在を見逃しやすい。
- source: GenerationLibraryView、PromptEditorView、PromptIntelligenceViewModel、#232 tests。

## 6. output整理

選択画像からfavorite → rating/note入力 → favorite filter → 検索/更新。primary3、入力focus/typing別。ratingはLostFocus、note/favoriteは即時保存。note fieldへ移ることでrating commitする。

- 迷い: Library「DB保存」はバックアップであり、annotationの保存buttonではない。refreshが選択を解除する。favorite filterとselected favoriteは同名・別対象。
- 記憶: annotation自体はDB保存。フィルタ/selected imageはsession。再scanは分類authority変更ではない。
- feedback: flush失敗ならselection/closingを守る。更新後selected detailが消えることは明示successと別。scan中Busy/Cancel、root停止とscan中止は別。
- source: GenerationLibraryViewModel annotation/LoadPage/flush、GenerationLibraryView、#226 tests。

## 7. tag discovery往復

Prompt → 辞書 → related HOME → group選択 → tag追加 → Prompt。5 activations / top2。facet選択は+1、HOME探索の途中選択は別。

- 強み: shared Positive、canonical English末尾追加、query/facets/routes/entry/scrollのUiState。戻ってもPrompt engineを作り直さない。関連Browseはdisplay authorityのみ。
- 迷い: group一覧の選択後も大きな候補群が残り、今回900×560 list0、1280×720 list41.33。初見では「45件あるのに表示されない」と見える。結果を確保するscroll/collapse構成が必要。
- 重複: 辞書右Promptとeditorのcopy/delete/Undoはshared command。右paneは即追加確認に有用なので全部撤去する判断はしない。
- feedback: current group/contextのbannerは有用。戻る/cancel、group reset semanticsを保った上でcandidate densityを調整すべき。
- source: DictionaryWorkspaceView、DictionaryWorkspaceViewModel、#223 native test/probe、#216/#179 protected authority tests。

## 8. rare / advanced

4独立経路を数える（1タスクへ合算しない）:

| branch / start | primary | top switch | modeless / modal | 迷い・feedback |
|---|---:|---:|---|---|
| raw / Prompt | 2（direct edit→apply） | 0 | 0 / 0 | raw保全、cancel/validation、適用後Undoを維持 |
| backup / Prompt | 3（画像tab→DB保存→OS確定） | 1 | 0 / 1 | DBだけ・画像含まない。annotation保存とは別 |
| PNG import / 任意 | 4（header→picker確定→P復元→N置換） | 0 | 1 / 1 | 読込だけでは変更なし。条件はRecipe作成へ、全条件restoreと誤認しやすい |
| compatibility / Prompt | 1（header send またはcurrent-settings Generate） | 0 | 0 / 0 | 元仕様はNegative unchanged。送信/生成を混同しない |

rawはPrompt編集mode、backupは画像maintenance、PNGはsource import、Forge設定はconnection settings。全てglobal headerへ並べる必然性はない。一方、移動先のlabel/tooltipとkeyboard focusを提供し、機能削除扱いにしない。

## Phase B findings / Phase C inputs

1. 高優先: 生成source（current / saved / image）とP/N/条件の適用範囲を生成前に認識できること。複数buttonを1名へ置換するだけではsilent semantic changeになる。
2. 高優先: group Auto高さとglobal header overflow。結果listをstarにするだけでは解決しない。低頻度toolbarを移すだけでもgroup高さ問題は残る。
3. 高優先: 編集P/Nと生成条件の関係。ただしcurrent Recipe ownerは現状存在しないため、Createへ並べるだけで実装済みになるとは考えない。無保存working Recipeは要設計・明示handoff。
4. 中優先: LoRA使用操作を管理metadataより前に置く。token/trigger/P additions/N additionsは別効果として維持。
5. 中優先: source-image inspectorとPrompt診断を混同しない。保持したcompare-left source、status、busyを対象surfaceに明示。
6. 中優先: 用語統一と保存/追加/置換/backupの差。global headerのscopeを曖昧にしない。
7. 維持: offline startup、shared Workspace、raw/unknown、Undo/Recovery、fail-closed Recipe、protected Browse、SHA identity、注釈flush protection。

全8タスクのbefore監査を記録済み。ユーザーテスト/native pointer時刻/実生成は未実施。afterは実装前なので次文書の予測のみ。
