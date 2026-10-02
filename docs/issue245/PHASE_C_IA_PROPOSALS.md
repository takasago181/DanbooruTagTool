# #245 Phase C — alternatives / implementation STOP

2026-10-02 JST。[Phase B](PHASE_B_TASK_AUDIT.md)のbeforeを根拠に2案を比較。#241は参考であり強制仕様ではない。**推奨まで。採用・product UI変更は未実施。** 新機能、production、#230/#231は対象外。

## Option A — existing four workspaces, focused Create

top-level: **タグ探索 / 作成 / 生成画像 / LoRA**。現行順序/4 indexを維持し、Prompt編集を作成へ整理。Presetは作成内の明示source/保存管理、独立asset workspaceを増やさない。

- 作成: existing shared Positive/Negative editorを主領域、生成条件はresize/collapse可能なsection。狭い時はP/Nと条件を縦積み/内tabで切替、生成summaryと主要actionを残す。新Prompt engineなし。
- 条件owner: **現状のPreset編集draftをそのままcurrent条件と同一視しない**。将来、既存GenerationRecipe validation/serviceへ一時snapshotを渡す小さなcomposition adapterを設計する。current P/N + visible条件でimmutable実行snapshotを作り、saved Presetや画像から読み込む際はsource・変更範囲を明示。current Recipeが無効/未設定ならverified生成は不可で理由表示。暗黙current-settings fallbackなし。未保存条件のrestart保存は今回案に必須とせず、既存DB schema/migrationを増やさない。
- Preset: 保存済みsnapshotは既存DB/VM、管理editorは二次入口。保存/現在へ読込/追加/置換の契約を区別。draftとcurrentを二重の同期可能editorとして同時に出さない。現saved Presetからの直接再現はsource付きcontext actionとして保持。
- LoRA: 専用top-levelを保持。detail先頭をweight/trigger/挿入、user override/links/hash等は管理sectionへ。追加結果はshared Prompt、Negative別操作。新Quick Addは当初作らない。
- 生成画像: existing grid/inspector/annotation/diffを保持。selected imageからの再現は「この画像の条件で生成」、編集用途は「作成で使う」でP/N/条件のpreviewと明示適用。左compare対象を固定labelに示す。注釈commit契約は維持。
- global header: workspace navigation、copy（対象side明示）、設定/その他。import/new/recoveryは作成contextへ。Generateは作成に主要1action、selected sourceの再現はcontext内。送信のみ/現在Forge条件は二次menuに正確な対象・Negative扱いを表示して保持。
- Forge state: endpoint、idle/busy/error、今回使うrequested条件をsummary。実Forge状態が未取得なら「未確認」とし、requested modelをloaded modelと表示しない。既存Counterの取得時点表記は維持。startup polling追加なし。
- タグ探索: nav/context/結果/shared Positive確認を維持。低幅ではnav/右paneをcollapseでき、group選択後は選択context＋一覧へ戻るを残して候補群を縮退。candidate panelをbounded scroll領域へ。結果を確保するheight予算を設計。authority/filter/return意味は維持。

小画面: 900×560と1280×720でもoverflowでactionが失われず、結果listが実際に使えることをnative測定。単なるwrap toolbarはheightを奪うため、二次menu/collapseを優先。font shrinkやMinHeightだけでは対処しない。pane widthsは現savedUiの範囲内でclampし、resetは明示操作。

Migration risk: 低〜中。4 indexを維持し既存saved navigationを壊しにくい。P/N/画像/LoRA/Preset schema変更なしを第一候補。Recipe source adapterは中程度のsemantic riskで、capture/save/append/replace/Undo/failed round-tripのfocused testが必要。

Code complexity: 低〜中。XAML/resources/context commandsとshell navigation owner整理、少量のCreate composition。Core/Data rewrite、dock framework、新DBなし。Main forwarderは別engineではないので名前だけを理由に削除しない。現Dialogは保存管理/PNG source viewerとして再利用可能。

## Option B — three workflow workspaces / asset Library

top-level: **作成 / タグ探索 / ライブラリ**。Library内部に **生成画像 / LoRA / Preset**。各assetの固有view/VMを維持し、同一CRUD画面へ押し込まない。

- CreateのP/N/条件/Generate契約はAと同じ。一時snapshotとsource表示が必要で、3tabへ変えるだけではtask1のsemantic debtは解消しない。
- LoRA/Preset管理はLibrary。Createから軽量「LoRAを追加 / Presetを使う」を同じexisting VMのselection/context viewとして開ける案。これはoptionalで、新store/search engineを作らない。追加と管理で同じeditable draftを複製しない。
- 生成画像Libraryはimage grid、LoRAはlist/trigger/weight、Presetはsaved snapshot/editor。selected inspectorの一部だけ共通style化、domain stateは分離。source type内tabの保存/restoreとCtrl+F routingが必要。
- global header: 3workspace navigation、設定/その他。GenerateはCreate主action。Libraryの再現はsource context action。rare import/backup/hashを二次maintenanceへ。busy/status/source summaryはA同等。
- small window: Createは縦stack/内tab、Library subtypeは横幅に応じてtext selector、inspector collapse。Quick Addはoverlay/drawerでkeyboard focusを戻す。タグ探索のgroup高さはAと同じ専用対処が必要。
- migration: 中〜高。旧index0辞書/1Prompt/2画像/3LoRAからnewtop+subtypeへversioned/reversible UI-state mappingが必要。newer schema refusal、backup/transactionを守る。UserDataのPrompt/Preset内容はそのまま。Quick Add閉鎖とunsaved LoRA draft、選択画像annotation flush、modeless editor lifetimeに新しいtransitionが生じる。
- complexity: 中。shell mapping+Library selection/navigation+optionaldrawer/focus+state ownership。existing VM再利用でも新transition testsが増える。Aよりnavigation変更が広い。
- discoverability: assetを一括して探せる利点。一方routine LoRAへtop-level直達を失い、Quick Addなしでは内tabが1手増える。PresetがLibraryとCreate二方向に見え、用途説明が必要。

## Comparison

| dimension | A: four refined workspaces | B: three + asset subtypes |
|---|---|---|
| workspace構成 | 現順序/index温存、Prompt→作成 | workflow order変更、Library nested |
| Create | shared P/N + visible条件summary、existingRecipe path | 同左、任意Quick Add |
| Library/LoRA/Preset | 画像/LoRA直達、Presetは作成context管理 | 全asset管理をLibrary、固有views保持 |
| header | context化、rare menu、scope表示 | 同左＋3workspace grouping |
| Generate | user intent+source明示、verified条件、互換二次入口 | 同左、Quick AddからCreateに戻る |
| small window | pane collapse / height budget、group候補縮退 | 同左＋drawer/nested navigation budget |
| migration | index温存、schema増加回避第一 | top/subtype mapping + reversible migration |
| code complexity | 低〜中 | 中、focus/lifetime/restore多い |
| muscle memory | existingtab位置、context機能を保持 | tab再配置、LoRAに新inner selector |
| task benefit | semantic visibilityの主課題へ直に対処 | asset横断の発見性、Quick Add採用時LoRA往復削減 |

## Task before / after prediction

予測であり実測ではない。入力・scrollの除外はPhase Bと同じ。移動先button確定前なので、偽の精密なafterクリック値は置かない。

| task | beforeの問題 | Aで期待するafter | Bで期待するafter |
|---|---|---|---|
| 1 routine generation | headerがN/条件を使わない。exact条件にはPreset capture/save迂回 | CreateにP/N/条件/source、Preset保存せず実行snapshot。LoRAありtop3は維持、なしtop1。再capture/saveの迂回除去 | 同改善。Quick AddならLoRA往復top2回をoverlay開閉へ、未採用ならLibrary subtype1手増 |
| 2 owned LoRA | 管理密度とRecipe二重意味、top2 | 同top2、使用controlsを上へ、P/N結果scope表示 | Quick Addならtop0/overlay、管理ならtop2＋内tab0–1 |
| 3 reproduce | current-settingsとverifiedsourceを誤選択 | 検索/選択/再現3手維持、選択画像source＋照合feedback明示 | subtype選択が必要なら1手増、前回画像なら同3 |
| 4 compare | 左targetを記憶 | 4手維持、左右対象名常時表示 | 同左、Library subtype入口の差のみ |
| 5 diagnose | metadataとcurrent診断が別。復元に変更を伴う | selected画像metadataは閲覧のまま。currentへ使う時だけ明示適用、source/条件summaryで記憶減 | 同左。asset切替は増えうる |
| 6 organize | DB保存の誤認/保存タイミング | favorite/rate/note継続、backup二次menu、flush結果表示 | 同左、管理場所の統一 |
| 7 discover | list0/41DIP、top2 | top2維持、group候補縮退/結果height確保で到達改善 | 同左 |
| 8 advanced | scope不明header/保存/読込 | 二次入口は1手増えうる、rareの位置・対象明示 | 同左、source選択が内tab追加になりうる |

## Codex recommendation: A

**4workspaceを保ち、作成の意味とcontext toolbar・小画面を先に整理するAを推奨。** auditではassetを一括管理できないことより、同じ生成buttonが別source/P/N/条件を使うことと、一覧/toolbarの到達性の方が明確な障害だった。Bの3tab自体ではそれらは改善せず、Quick Addを作らない場合にはroutine LoRAへ1手増える。Aは主要なsemantic改善をBと同等に得られ、既存navigation・view/stateを再利用しやすい。

Bを否定するものではない。asset横断管理の実ユーザー頻度、Quick Addが管理draftを増やさずroutine往復を減らす証拠が出れば、後続IA判断でBを選べる。今は新しいnested navigation/lifetime/migrationを増やす根拠が足りない。#241例示を機械的に採用しない。

採用された場合の実装順候補（未実施）:

1. 対象/source契約とterminology/action mapを固定し、元BridgeとRecipeの互換testを維持。
2. header/context整理とgroup高さ対処、900×560/1280×720/1600×900/WQHD native/tree確認。
3. shared P/NとRecipe compositionをCreateに配置、saved/current/imageの明示handoff。条件validation、Undo/Recovery、原文、注釈flushをfocused検証。
4. LoRA使用/detail管理と画像compare/statusの局所整理。
5. beforeと同一8taskでafterを実測、全Release/authority/CI、cleanpublish/disposable smoke、restartを確認。

## Implementation stop / remaining gates

Phase B beforeとPhase C案/推奨まで完成。**ここで停止し、ユーザーによるIA選定を待つ。** Draft PR246はaudit成果でありUI実装の完成PRではない。#245はopen、merge/production applyしない。after map/実測/render/publish/newruntimeは未作成であり、実装後Gateへ繰り越す。

実装前に確定が必要: A/B採用、current Recipe一時stateのsource/handoff仕様、二次互換操作の名称とN契約。ユーザー指示なしに実装しない。
