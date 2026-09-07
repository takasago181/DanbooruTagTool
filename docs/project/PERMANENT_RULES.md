# PERMANENT RULES

## 管理

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
8. Stage完了・大方針変更・チャット移行前に `CURRENT_STATE.md` を更新する。
9. Codexは現行DEV Issue本文を `docs/project/CURRENT_DEV_TASK.md` の同期ミラーから読む。
10. 現行DEV Issueの本文・state・完了条件を変更する管理作業では、`CURRENT_DEV_TASK.md` も同じ管理作業内で更新する。
11. `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致しない場合、Codexは実装開始しない。
12. 本プロジェクトの作業チャット（常設4班、現行Issueを持つTEMP、GitHub管理・調整チャット）は、会話が長大化して現在地混同・取りこぼし・応答品質低下のリスクが出た場合、またはStage完了・大方針変更・大きな作業区切りに到達した場合、ユーザーから「引継ぎして」と言われるのを待たず、自発的にチャット移行を提案する。
13. 自発的なチャット移行では、旧チャット側が先にGitHub正本を更新してから移行を提案する。長大な手書きhandoffを新チャットへ貼ることを標準運用にしない。
14. Codexが守るべき現行DEVの目的・scope・禁止事項・完了条件は、GitHub Issue本文と `CURRENT_DEV_TASK.md` に反映する。Issueコメントだけに現行指示を置いてCodexの作業条件を変更しない。コメントは結果・証跡・履歴の記録には使用してよい。

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
