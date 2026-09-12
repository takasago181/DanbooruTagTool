# PERMANENT RULES

## 管理

### 体制・権限

1. 常設は2班のみ。
   - DEV（開発）
   - KNOWLEDGE（知識。旧PROMPT責務を含む）
2. Codexは独立班ではなくDEVの実装担当。
3. Forge Neo環境準備やその他TEMPは期間限定担当。
4. 正式仕様の決定権はDEVにのみある。
5. AUDITは常設班ではなく、必要な品質Gateごとに起動する独立監査ロール。監査完了後は常時待機させない。
6. KNOWLEDGE / AUDIT / TEMPは勝手に本体仕様を変更しない。KNOWLEDGEがPrompt・generation-effectiveness知識を所有しても、production採用権限は得ない。
7. チャット履歴を正本にしない。

### 正本・現行DEV・checkpoint

8. 全体Stage/Gate/担当/大方針が変わった時、または正式handoff前に `CURRENT_STATE.md` を更新する。
9. CodexはGitHub live `main` の `CURRENT_STATE.md` からcurrent DEV Issue番号を取得し、そのlive GitHub Issue本文と最新コメントを直接読む。
10. DEV開始時はIssue title / state / body / latest checkpoint / continuation / completion / blockerを確認し、本ファイルと照合する。
11. GitHub/Issue取得失敗、番号不一致、unexpected closed/superseded、task contract不明、恒久ルールとの矛盾がある場合はfail-closed。古い資料で続行しない。
12. 会話長大化・大区切り・大方針変更時は、ユーザーの明示依頼を待たずチャット移行を提案してよい。ただし先にGitHub正本を更新する。
13. 長大な手書きhandoffをユーザーへ要求することを標準運用にしない。
14. `CURRENT_STATE.md` はrouting正本。目的・scope・禁止事項・完了条件・evidenceはlive Issueが正本。
15. 意味のある途中成果をchatだけに保持し続けず、自班/担当Issueへcheckpointを残す。
16. checkpointには最低限「最後に成功したこと/結果」「未完了/blocker」「次作業」「branch/commit/file/evidence」を含める。
17. `CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` 等のshared管理文書を変更する前にlatest mainを再取得し、staleな会話内コピーで全上書きしない。
18. Codexへ再開/新規指示を出す場合も、Codex自身がlive preflightを行う。

### Live GitHub authority

作業開始・再開・復元時の優先順:

1. GitHub live `main` HEAD
2. live `main` `docs/project/CURRENT_STATE.md`
3. current live GitHub Issue本文
4. Issue latest checkpoint/comment
5. live `docs/project/PERMANENT_RULES.md`
6. 必要なfeature branch / local worktree

local `CURRENT_STATE.md` / handoff / branch-local management docはhistorical snapshotの可能性がある。
食い違う場合はlive authorityを優先し、routing同期まで停止する。
Codex自身がIssue本文を推測して書き換えない。

### Local protected data

19. GitHubは管理状態・commit済みcode/docsの正本であり、local workspace全体のbackupではない。`.gitignore`対象のsource/derived/runtime/runtime_index/Special大容量data等はlocal protected data。
20. `git clean -fdx` / `git clean -fdX` / ignored protected dataの広範囲cleanupは禁止。fresh cloneだけでfull runtime/full testsが復元できると仮定しない。

### Codex branch・成果物・監査handoff

21. Codex本体実装は原則latest mainからtask feature branchで行い、直接mainへ未review実装をcommitしない。
22. stable checkpointはcommitし、可能ならremoteへpushする。
23. GitHub branch/commit/PRからreview可能な成果物について、ユーザーへ手動ZIP uploadを要求しない。local-only/binary/push failure時だけfallbackを使う。
24. Codexの「完了」自己申告だけで次Gateへ進まない。DEVがbranch/commit/report/tests/protected確認を取得してIssueへ証跡化して初めて監査渡し可能。
25. ユーザーが「Codex終わった」と言った場合も、次工程前にGitHub上の成果物を確認する。成果不足なら監査/次Stageへ進まない。

### 班間handoff

26. DEV / KNOWLEDGE / 必要時AUDIT / TEMPの依頼と返却は原則GitHub Issue経由。ユーザーをコピペ中継役にしない。
27. 依頼は最低限 `FROM / REQUEST / WHY / EXPECTED OUTPUT / RELATED ISSUE・FILE` を含める。
28. 結果は最低限 `RESULT / EVIDENCE / VERDICT / LIMITATION / NEXT` を含める。
29. 依頼元の次作業に必要な結果は、依頼元Issueにも短い返却checkpointを残す。
30. local-only/binary/protected dataやconnector障害時だけ合理的fallbackを許可し、その理由/所在をIssueへ残す。
31. task contract自体が変わる場合、Issueコメントだけで済ませずIssue本文/Decision/必要な仕様/CURRENT_STATEを同期する。
32. GitHubへ登録した班間依頼・重要返却はユーザーにも要約して見せる。
33. 大方針変更では少なくとも `PRODUCT_GOAL_LOCK.md` / #42等product-scope Issue / `DECISIONS.md` / `FEATURE_PRIORITY.md` / `FLOWCHARTS.md` / `AGENTS.md` / 必要なlane Issueを照合する。

## KNOWLEDGE generation / Prompt支援ルール

> 旧PROMPT班は廃止され、Prompt・generation-effectiveness知識はKNOWLEDGE #44へ統合された。この節はKNOWLEDGEが将来/高度支援として扱うPrompt知識のルールであり、v1 runtimeが自動Prompt生成を行う義務ではない。

34. KNOWLEDGEが個別Prompt作成・Prompt知識を支援する場合、ユーザーに毎回Special探索・Prompt再構築・大量手動差し替えを戻さず、対応可能な範囲を完成Promptとして組み立てる。
35. 直接記述できない核心だけを最小限スロット化し、記述可能なpose/camera/visibility/binding等を無関係な別内容へ変更しない。必要ならSpecial候補を日本語付きで提示する。
36. 安全/能力境界を理由にPrompt全体を不要に曖昧化しない一方、対応できない範囲の無制限対応は約束しない。
37. 差し替えスロットを常にゼロにできるとは保証しないが、残るスロットの数と範囲を可能な限り減らす。
38. 対応可能な範囲で、ユーザー指定の意味・強度・identityを一般語への希釈だけで変えない。

## Product search / UI invariant

39. 検索入力は**日本語・英語の両対応**を恒久要件とする。日本語-first UIを日本語専用検索へ狭めない。
40. 日本語/英語は原則同じ検索欄・同じcandidate workflowへ入り、言語モード切替を要求しない。
41. exact canonical / exact English / word-boundary intentを incidental substring/fuzzy collisionより優先する。Alias/Japanese overlay/Semantic等を使ってもcanonical identityを変えない。
42. 候補表示は日本語-first + canonical English併記を基本とし、最終Prompt payloadはcanonical Englishを維持する。
43. 検索/UI回帰では日本語queryと英語canonical queryの両方を確認する。
44. v1の安定した主導線は **既存Promptを理解 -> 日本語/英語検索またはジャンル閲覧で発見 -> Special/Generalを自分で選択 -> Promptへ追加/削除/並べ替え -> canonical-English Promptコピー** とする。
45. Specialは#56の深いbrowse taxonomy、Generalはproduction Japanese overlay 30,629件を対象とした#64の浅い実用taxonomyを使う。General taxonomyを日本語overlay/canonical identityへ埋め込まず別sidecarにする。
46. v1ではhidden automatic support insertion / automatic minimum-sufficient Prompt / automatic model rewrite / automatic failure diagnosisをデフォルト挙動にしない。ユーザーが見えていない自動挿入と実際のPrompt出力を食い違わせない。
47. **現在のStage10はIssue #65 / `docs/stages/STAGE_10_LEARNING.md`で定義される実践画像生成学習ステージ**とする。Stage10はv1 product completion blockerではなく、v1 routeと並行して進める。旧Stage10 production A/B/evaluator資産はhistorical/testing evidenceとして保持するが、現在のStage10 completion定義には使わない。
48. 旧文書の `PROMPT:#5` / `PROMPT班` 参照はhistorical provenanceとして扱う。新規作業を独立PROMPT班へroutingせず、必要ならKNOWLEDGE #44へ統合して扱う。

## Stage10 learning invariant

49. Stage10 primary learning laneは **NoobAI XL 1.1 EPS + Forge Neo**。Animaはrelation-heavy / multi-character / tag+natural-language比較・fallback、WAI Illustrious v17はhistorical/comparison、NoobAI V-PredはEPSと分離したadvanced profileとして扱う。
50. Stage10は設定値の暗記ではなく、`意図 -> Prompt -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要な補助 -> 仕上げ -> 再現可能な保存` を自力で回せることを目的とする。
51. hard/niche生成の評価ではpresenceだけで成功扱いせず、必要に応じてactor/target/ownership/body-site/relation/count/visibility/source-destination/topologyを分離して確認する。
52. 診断では一度に多数の変数を変えず、原則として観測したfailure classに対応する最小の意味ある変更を試す。random seed探索とfixed-seed診断を混同しない。
53. LoRA/Hires/ADetailer/img2img/inpaint/regional/Controlは目的を持ったinterventionとして扱う。修復後の成功をbase Prompt capabilityと同一視しない。
54. Stage10の単発成功画像はlocal caseでありglobal/model-family truthではない。反復controlled evidenceのみ、scope付きでKNOWLEDGE #44のClaim更新候補にできる。
55. Stage10の学習checkpointは必要以上に事務化しないが、意味のある区切りでは model/profile/runtime / target / actual Prompt・Negative / settings / Seed / tools・LoRA state / result・failure class / lesson を復元可能にする。

## Product authority

現在の製品目的は `docs/PRODUCT_GOAL_LOCK.md` を正本とする。
Historical Stage仕様、旧Codex実装仕様、旧Issueコメント、既存コードの高度機能は、単に古い/実装済みという理由でcurrent product goalより優先しない。

Stage10 learningの正本は `docs/stages/STAGE_10_LEARNING.md` とIssue #65。Stage10学習成果が存在すること自体はv1 production/UI採用理由にならない。
