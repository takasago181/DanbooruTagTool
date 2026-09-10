# PERMANENT RULES

## 管理

### 体制・権限

1. 常設は3班のみ。
   - 開発
   - 知識
   - Prompt
2. Codexは独立班ではなく開発班の実装担当。
3. Forge Neo環境準備は臨時担当。
4. 正式仕様の決定権は本体開発班にのみある。
5. AUDITは常設班・常設チャットではなく、必要な品質Gateごとに起動する独立監査ロールとする。仕様決定者ではなく、対象Gateの独立判定を行い、監査完了後は常時待機させない。次回監査はGitHub正本から新しい監査個体を起動してよい。
6. 知識班とPrompt班は勝手に本体仕様を変更しない。
7. チャット履歴を正本にしない。

### 正本・現行DEV・checkpoint

8. Stage完了・大方針変更・チャット移行前に `CURRENT_STATE.md` を更新する。
9. Codexは `CURRENT_STATE.md` からcurrent DEV Issue番号を取得し、そのlive GitHub Issueを `gh issue view <ISSUE_NUMBER> --comments` で直接取得して読む。GitHub Issueが現行DEVの正本である。
10. DEV開始時は、Issue title / state / body / 最新コメント / 最新checkpoint / continuation contract / completion condition / blocker・gateを確認し、`PERMANENT_RULES.md` と照合する。
11. `gh` 利用不可、GitHub認証失敗、Issue取得失敗、`CURRENT_STATE.md` のcurrent DEV Issue欠落、番号不一致、想定外のclosed / superseded、Issue本文と最新checkpointの関係不明、または明確な恒久ルール矛盾がある場合はfail-closedで実装を開始しない。古い資料を根拠に続行しない。
12. 本プロジェクトの作業チャット（常設3班、必要時に起動したAUDIT Gate、現行Issueを持つTEMP、GitHub管理・調整チャット）は、会話が長大化して現在地混同・取りこぼし・応答品質低下のリスクが出た場合、またはStage完了・大方針変更・大きな作業区切りに到達した場合、ユーザーから「引継ぎして」と言われるのを待たず、自発的にチャット移行を提案する。
13. 自発的なチャット移行では、旧チャット側が先にGitHub正本を更新してから移行を提案する。長大な手書きhandoffを新チャットへ貼ることを標準運用にしない。
14. `CURRENT_STATE.md` はcurrent DEVのroutingを示し、目的・scope・禁止事項・完了条件・checkpoint・evidenceは対応するlive GitHub Issueを正本とする。
15. 意味のある途中成果をチャットだけに保持し続けない。重要な成功結果・検証結果・判断材料が得られた時、長時間中断や話題切替の前、または直近作業を失うと再開コストが大きい時は、自班/担当Issueへ短いcheckpointを残す。
16. checkpointは原則としてIssueコメントに残し、少なくとも「最後に成功したこと/結果」「未完了またはblocker」「次作業」「関連branch/commit/file/evidence」を含める。通常の途中経過だけで `CURRENT_STATE.md` を頻繁に書き換えない。全体の現在地・Gate・担当・Stageが変わった時だけ共有正本を更新する。
17. `CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` / Stage Gate文書など共有管理ファイルを変更する前に、必ず最新mainの内容とblob/commitを再取得してから差分を統合する。古いチャット内コピーや記憶だけでファイル全体を上書きしない。競合があれば停止して明示的に解消する。
18. DEV/管理側がCodexへ新規実装または再開指示を出す場合も、Codex自身が上記のlive Issue preflightを実行する。Issue本文・state・最新checkpointの関係に不明点があればfail-closedで停止する。

Codex自身がIssue本文を推測して書き換えない。

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

26. 常設3班、必要時に起動するAUDIT Gate、現行Issueを持つTEMPの班間依頼・班間返却は、原則GitHub Issueを標準経路とする。ユーザーを「班Aの文章をコピーして班Bへ貼る中継役」にしない。
27. 班Aが班Bへ調査・監査・実装・Prompt作成・環境確認などを依頼する場合、班Aまたは管理側が班Bの現行Issueへ依頼checkpointを残す。少なくとも「FROM / REQUEST / WHY / EXPECTED OUTPUT / RELATED ISSUE・FILE」を明記する。
28. 依頼を受けた班Bは、結果をチャットだけで返さず自班Issueへ結果checkpointを残す。少なくとも「RESULT / EVIDENCE・SOURCE / ADOPT・HOLD・FAIL等の判定 / LIMITATION / NEXT」を含める。
29. 班Bの結果が班Aの次作業に直接必要な場合、班Bまたは管理側は班Aの現行Issueにも短い返却checkpointを残し、自班Issueの詳細結果へリンク・Issue番号で参照させる。班Aはチャット記憶ではなくGitHub上の返却結果を読んで再開する。
30. この往復ルールはDEV / AUDIT / KNOWLEDGE / PROMPT / 現行TEMPすべてに適用する。例外は、GitHubに載せられないlocal-only・binary・protected data、connector障害など合理的な理由がある場合だけで、その場合も理由と代替handoffの所在をIssueへ記録する。
31. 班間handoffでtask contract自体が変わる場合、Issueコメントだけで仕様変更を済ませない。対応Issue本文、Decision、Stage仕様を更新し、現行DEVの `CURRENT_STATE.md` とlive Issueの対応を保つ。
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
44. 最終UIの安定した主導線は **検索 → Special候補選択 → Special詳細/成立条件確認 → 必須・推奨support調整 → 完成Promptコピー** とする。具体的なレイアウト・視覚設計はUI-JA親Issue #34を管理先とし、内部機能の増加によって通常操作を複雑化させない。
