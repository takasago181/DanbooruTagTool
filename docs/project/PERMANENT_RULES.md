# PERMANENT RULES

## 管理

### 体制・権限

1. 常設は4班のみ。
   - 開発
   - 監査
   - 知識
   - Prompt
2. Codexは独立班ではなく開発班の実装担当。
3. Forge Neo環境準備は臨時担当。
4. 正式仕様の決定権は本体開発班にのみある。
5. 監査班は仕様決定者ではなく、独立した品質ゲート。
6. 知識班とPrompt班は勝手に本体仕様を変更しない。
7. チャット履歴を正本にしない。

### 正本・現行DEV・checkpoint

8. Stage完了・大方針変更・チャット移行前に `CURRENT_STATE.md` を更新する。
9. Codexは現行DEV Issue本文を `docs/project/CURRENT_DEV_TASK.md` の同期ミラーから読む。
10. 現行DEV Issueの本文・state・完了条件を変更する管理作業では、`CURRENT_DEV_TASK.md` も同じ管理作業内で更新する。
11. `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致しない場合、Codexは実装開始しない。
12. 本プロジェクトの作業チャット（常設4班、現行Issueを持つTEMP、GitHub管理・調整チャット）は、会話が長大化して現在地混同・取りこぼし・応答品質低下のリスクが出た場合、またはStage完了・大方針変更・大きな作業区切りに到達した場合、ユーザーから「引継ぎして」と言われるのを待たず、自発的にチャット移行を提案する。
13. 自発的なチャット移行では、旧チャット側が先にGitHub正本を更新してから移行を提案する。長大な手書きhandoffを新チャットへ貼ることを標準運用にしない。
14. Codexが守るべき現行DEVの目的・scope・禁止事項・完了条件は、GitHub Issue本文と `CURRENT_DEV_TASK.md` に反映する。Issueコメントだけに現行指示を置いてCodexの作業条件を変更しない。コメントは結果・証跡・履歴の記録には使用してよい。
15. 意味のある途中成果をチャットだけに保持し続けない。重要な成功結果・検証結果・判断材料が得られた時、長時間中断や話題切替の前、または直近作業を失うと再開コストが大きい時は、自班/担当Issueへ短いcheckpointを残す。
16. checkpointは原則としてIssueコメントに残し、少なくとも「最後に成功したこと/結果」「未完了またはblocker」「次作業」「関連branch/commit/file/evidence」を含める。通常の途中経過だけで `CURRENT_STATE.md` を頻繁に書き換えない。全体の現在地・Gate・担当・Stageが変わった時だけ共有正本を更新する。
17. `CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` / `CURRENT_DEV_TASK.md` / Stage Gate文書など共有管理ファイルを変更する前に、必ず最新mainの内容とblob/commitを再取得してから差分を統合する。古いチャット内コピーや記憶だけでファイル全体を上書きしない。競合があれば停止して明示的に解消する。
18. DEV/管理側がCodexへ新規実装または再開指示を出す直前に、private GitHubの現行DEV Issue本文/stateと、最新mainの `CURRENT_STATE.md` / `CURRENT_DEV_TASK.md` を照合する。同じIssue番号のまま本文だけ変更された場合も検出し、目的・scope・禁止事項・完了条件に差があればミラーを先に同期する。照合前にCodexへ実装開始させない。

Codex側の現行DEV task読取補足:
- GitHub Issueが実作業の管理記録で、`CURRENT_DEV_TASK.md` はCodex読取用ミラー。
- DEV Issueの本文・state・完了条件を変更する管理作業では、ミラーも同じ管理作業内で更新する。
- Codexが守るべき目的・scope・禁止事項・完了条件はIssue本文とミラーに存在するものだけを現行指示として扱う。
- Issueコメントは結果・証跡・checkpoint・履歴の記録には使えるが、コメントだけで現行taskの条件を上書きしたものとは扱わない。
- Codex自身がIssue本文を推測してミラーを書き換えない。
- DEV/管理側はCodexへ新規実装・再開を渡す直前にprivate Issue本文/stateと最新mainのmirrorをlive照合する運用。Codexはその管理preflightを代行せず、local側では番号・mirror・scope・Gateを再確認する。

### Local protected data

19. GitHubは管理状態・commit済みコード/文書の正本だが、ローカル作業環境全体のバックアップではない。`.gitignore` 対象の `data/source/`、`data/derived/`、`data/runtime*`、Special2788の大容量CSV等はローカル側の保護データであり、GitHubに見えないことを削除・欠損と解釈しない。
20. ローカル保護データを消し得る `git clean -fdx`、`git clean -fdX`、その他ignored fileを広範囲に削除する操作は禁止。fresh cloneだけでは全runtime/全テスト環境を復元できないため、必要なlocal protected dataを別途保全・復元してから扱う。

### Codex branch・成果物・監査handoff

21. Codexの本体実装は、原則として最新mainからtask用feature branchを作って行い、直接mainへ実装commitしない。レビュー可能なstable checkpointはcommitし、可能ならremoteへpushする。mainへの反映はDEV確認・必要なAUDIT Gateを経て行う。
22. ChatGPTレビューに必要な成果物がすべてGitHubのbranch/commit/PRから取得できる場合、ユーザーへ手動ZIP uploadを要求しない。GitHubに載らないlocal-only data、binary evidence、push失敗時などだけ `docs/CHATGPT_CODEX_HANDOFF.md` のZIP fallbackを使う。
23. Codexはprivate GitHub Issue APIやIssueコメントへの直接書込みを完了条件にしない。Codexの責務は、レビュー可能なbranch/commit、要求された実装レポート、テスト・protected確認結果をrepositoryへcommitし、可能ならremoteへpushすること。DEV/管理側はその成果をGitHubから確認し、対応Issueへcheckpoint/完了証跡を記録する。
24. Codex/DEVの「監査渡し可能」は、ローカル実装やCodexチャット上の完了報告だけでは成立しない。DEVがremote branch/commitまたはfallback成果物を取得し、実装レポート・テスト結果・protected確認・未解決事項・次Gateへの停止地点を確認した後、DEV自身が担当Issueへ完了証跡を残して初めて成立する。Codexのpushが失敗した場合は完了とせず、branch/commit SHAと失敗理由を報告し、ZIP fallback等でDEVが回収できる状態にする。
25. DEV/ChatGPTはユーザーから「Codex終わった」と聞いた時、次工程へ進む前にGitHub上のbranch/commit/report等を確認する。Codex自身のIssue書込みを要求せず、DEV側が取得できた成果からIssue証跡を記録する。成果物不足なら監査や次Stageへ進まず、必要なrepository反映またはfallback回収をCodexへ戻す。ユーザーへ毎回Codex全文のコピペを要求することを標準運用にしない。

### 班間handoff

26. 常設4班と現行Issueを持つTEMPの班間依頼・班間返却は、原則GitHub Issueを標準経路とする。ユーザーを「班Aの文章をコピーして班Bへ貼る中継役」にしない。
27. 班Aが班Bへ調査・監査・実装・Prompt作成・環境確認などを依頼する場合、班Aまたは管理側が班Bの現行Issueへ依頼checkpointを残す。少なくとも「FROM / REQUEST / WHY / EXPECTED OUTPUT / RELATED ISSUE・FILE」を明記する。
28. 依頼を受けた班Bは、結果をチャットだけで返さず自班Issueへ結果checkpointを残す。少なくとも「RESULT / EVIDENCE・SOURCE / ADOPT・HOLD・FAIL等の判定 / LIMITATION / NEXT」を含める。
29. 班Bの結果が班Aの次作業に直接必要な場合、班Bまたは管理側は班Aの現行Issueにも短い返却checkpointを残し、自班Issueの詳細結果へリンク・Issue番号で参照させる。班Aはチャット記憶ではなくGitHub上の返却結果を読んで再開する。
30. この往復ルールはDEV / AUDIT / KNOWLEDGE / PROMPT / 現行TEMPすべてに適用する。例外は、GitHubに載せられないlocal-only・binary・protected data、connector障害など合理的な理由がある場合だけで、その場合も理由と代替handoffの所在をIssueへ記録する。
31. 班間handoffでtask contract自体が変わる場合、Issueコメントだけで仕様変更を済ませない。対応Issue本文、Decision、Stage仕様、現行DEVなら `CURRENT_DEV_TASK.md` を既存ルールどおり同期する。
32. 班間依頼をGitHubへ登録した場合、その依頼内容をユーザーにも可視化する。ユーザーに転記作業は求めないが、「どの班へ・何を・なぜ・どんな結果を求めたか」が把握できるよう、チャット側で依頼本文または十分な要約を提示する。依頼を黙って裏で流すことを標準運用にしない。
33. 班間返却についても、ユーザーの判断や次作業に影響する重要結果はチャット側で要約して知らせる。GitHubを正本としつつ、ユーザーの可視性を失わせない。

### Prompt支援

34. Prompt支援では、ユーザーに毎回Special探索・Prompt再構築・大量の手動差し替えをさせることを標準運用にしない。本プロジェクトの制作目的とユーザー負担最小化を優先し、PROMPT班が対応可能な部分を完成Promptとして最大限組み立てる。
35. Prompt内に直接記述できない箇所がある場合でも、予防的にPrompt全体を曖昧化したり多数の差し替え札へ分解したりしない。本当に必要な最小箇所だけを局所スロット化し、Special2788からPROMPT班が第一候補と原則3候補程度を日本語付きで提示する。ユーザー自身に2788件の探索を要求しない。
36. 成人・合意は重要な前提だが、それだけを理由に無制限対応を約束しない。同時に、その境界を理由として制作目的から著しく乖離するほどユーザーへ手作業を戻さない。対応可能なcamera / pose / visibility / quality / model-family構造 / negative / support設計はPROMPT班が担い、差し替えが残る場合もユーザー作業を「候補選択または最小スロット置換」程度へ抑える。
37. 本プロジェクトのツール作成・検証用Prompt支援では、差し替えスロットを常にゼロにできるとは保証しないが、**残るスロットの数と範囲を実務上可能な限り減らすことをPROMPT班の明示的な品質目標とする**。対応可能な内容まで予防的にスロット化せず、同一核心概念の無用な分割を避ける。
38. 対応可能な範囲では、スロット数を減らすためにユーザー指定の成人Special・性癖の強度、具体性、identityを勝手に弱めない。一般語への希釈、ソフト化、婉曲化、曖昧化によって見かけ上スロットを減らすことをしない。境界が残る場合は必要な最小箇所だけを局所化し、記述可能な周辺構造は元の強度を保ったまま最大限完成させる。

### Product search / UI invariant

39. 本ツールの検索入力は**日本語・英語の両対応**を恒久要件とする。日本語UI優先・日本語表示強化を、日本語専用検索へ狭めてはならない。
40. 日本語入力と英語入力は原則として同じ検索欄・同じSpecial-first候補フローへ入る。ユーザーへ日本語/英語の別モード切替を要求しない。
41. 日本語入力はJapanese overlay / Alias / Semantic等のStage9で確立した経路を活用し、英語入力はcanonical / normalized Englishを直接利用できる既存Stage9検索能力を維持する。UI・辞書・ランキング変更でこの両経路を退行させない。
42. 候補表示は日本語優先＋canonical英語併記を基本とするが、**入力言語と表示言語を混同しない**。最終Prompt payloadはcanonical英語を維持する。
43. 検索/UI改修の受入れでは日本語queryと英語canonical queryの両方を回帰確認する。片方だけ通る状態を完成扱いしない。

## チャット移行プロトコル

1. 本プロジェクトの作業チャットを新しくする前に、旧チャット側で現在地・未完了・禁止事項・担当Issueまたは管理状態をGitHubへ反映する。
2. 新チャットは、実作業を始める前に次の順で現行状態を確認する。
   1. `docs/project/CURRENT_STATE.md`
   2. `docs/project/PERMANENT_RULES.md`
   3. 常設班/TEMPは `CURRENT_STATE.md` に記載された自班の現行GitHub Issue、管理・調整チャットは関係する現行Issueと管理文書
   4. 必要な現行Stage仕様・Decision・mainの実装状態
3. Issue番号はStage進行で変わるため、過去チャットや固定番号から推測しない。毎回 `CURRENT_STATE.md` から現行Issueを特定する。
4. 新チャットは確認後、自分の班または担当種別・現在Stage・担当Issueまたは管理対象・役割・次作業・禁止事項・Codexとの関係を自分の言葉で回答し、最後に `GitHub正本運用：認識済み / 未認識` を明記する。
5. 認識確認が完了するまで、実装・監査PASS・本番Prompt確定・Stage移行などの実作業を開始しない。
6. 古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合、古い資料で現在地を巻き戻さない。ただし勝手に破棄・統合もせず、衝突として確認する。
7. 詳細手順は `docs/project/CHAT_START_PROTOCOL.md` を正本とする。

## 開発

1. 実行時は非LLM。
2. ローカル個人利用を前提とする。
3. 不要な一般配布向け抽象化・権限管理・クラウド化は持ち込まない。
4. ただしデータ整合性・追跡可能性・バックアップ・再現性は弱めない。
5. Stage10の実験専用知識をStage9 Runtime Composerへ先行実装しない。
6. model familyごとのPrompt grammarを共有前提にしない。
7. ComposerはStage10後にPrompt構造・並び順を変更できる状態を維持する。
8. Stage10 A/B比較用に、決定論的出力と実際のPromptの追跡可能性を維持する。