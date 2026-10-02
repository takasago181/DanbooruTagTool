# #245 Phase D — selected B-lite contract

2026-10-02 JST。ユーザーが [IA selection: B-lite](https://github.com/takasago181/DanbooruTagTool/issues/245#issuecomment-5944355694) と添付実装指示でPhase Dを許可した。Phase CのA推奨は当時の比較として残す。採用はB-lite、ユーザーが選定理由をIssueへ記録済み。

- Top-level: 作成 / タグ探索 / ライブラリ。空の実験tabなし。
- Libraryは既存生成画像 / LoRAの固有viewを内tabに配置。Preset管理は作成の「生成条件 / Preset」に置く。汎用CRUD・新DB・新scan・dock frameworkなし。
- 作成のP/Nは既存shared Workspace。Positive / Negative / 生成条件・Preset / LoRA追加の内tab。低画面高で入力面を残すためPreset操作は条件文脈へ、rare操作はその他へ移す。
- 作成条件は1つの`CreateViewModel`が持つ**session-only current draft**。終了時に破棄する旨をUIに表示。永続化したい時だけ新Presetとして保存できる。生成のための保存は不要。既存saved Preset編集draftとは自動同期しない。管理dialogはmodalで同時編集を防ぐ。条件のrestart永続化用DB/schemaは増やさない。
- Preset選択だけでは変更なし。明示「作成で使う」でP/N/条件を置換。元sourceと変更済み現在値を区別。画像/PNGの明示読込も同じadapterへ。片側の旧追加/置換、直接source生成は互換として保持。
- 「生成」は押下時のcurrent P/N出力と入力条件からimmutable snapshotを作り、既存#228 API serviceへ。all8条件/fixed seed/8-multiple sizeを要求、capabilityは生成前に既存adapterが再確認、実PNG metadata照合・失敗画像保持・Library linkageはそのまま。検証不能時にBridgeへfallbackしない。
- capability照会は明示操作、生成なし。requested Modelをloaded modelと表示しない。startupでForge通信なし。DTTの実行busy/errorと外部Forge未確認を区別する。
- 互換: 現在Positiveのみ・Negative変更なしの送信/Forge現在条件生成、両Workspace送信、source画像P/N送信/現在条件生成を保持。入力条件を適用しないことを名称/helpに示す。
- LoRA quick-useは同じ`LoraLibraryViewModel`のAssets/Selected/Weight/Triggers/preview/Insert/AppendNegativeを使用。管理UIをコピーせず、独立store/draftを増やさない。Negative追加は明示。
- Tag discovery: sharedPositiveとroutes/facets/HOME/group authorityを維持。group選択後candidateを縮退、contextをbounded scrollへ。元#223 label/wrap/filter/return/assertionは弱めない。小幅はnav/currentPromptの幅を適応し、wide saved widthsを保持。
- Compareは左保持/右選択/比較を維持。保持中は左/右filenameをscroll外の固定contextで確認可能にする。
- Navigation保存は旧0辞書/1Prompt/2画像/3LoRAをそのまま保存し、shell表示だけ0作成/1タグ/2Libraryへ写像する。既存saved workspaceを再解釈しない。内Library LoRA選択も旧3で保持。UserData schemaは2のまま。

## Gates / stop

focused UI/ViewModelと既存#223/#226/#228/#229/#232、full Release、authority/protection、CI、clean self-contained publish、disposable executable startup/restart、4解像度render/tree、8task afterを確認する。Phase A/B/Cの証拠は削除しない。

**PR246はDraftのまま、自動merge・production applyなし。** 実装/検証/after監査を終えたら user review before merge / production promotion でSTOP。#230/#231/#233–#237は開始しない。
