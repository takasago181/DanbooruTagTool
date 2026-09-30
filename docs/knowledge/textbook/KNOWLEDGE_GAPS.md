# Knowledge gaps / editorial limits

## 知識そのものの不足

- 普遍的な最適weight、過剰weightの数値閾値、semantic bleed/anatomy/style dominanceの正確なモデル別条件は未確定。語を増やして埋めない。
- NoobAI EPSのactor/body-site/count ceiling、canonical/Alias/historical反応、Negative効果はK-MODEL-NOOB-004/HOLD。
- Anima tag-onlyとhybridの成功率差はK-MODEL-ANIMA-004/HOLD。Base/Aesthetic/Turboを分離。
- LoRA×Special/SupportはK-LORA-002/HOLD。互換性の全面保証はない。
- 本文用語の医学的説明とDanbooruの正確なcanonical境界は別。個別成人用語のactive Alias/Wiki再確認は本タスクでは新規semantic採用にしない。
- 各モデルの得意領域の比較は作者説明・運用上の候補。直接比較ランキングは作成できない。
- 本書はsnapshot。2026-10-01時点の外部モデル最新版確認は行っておらず、2026-09-09〜17の原資料確認日を表示。

## 正本間で自動解決しない差

- ledgerのWAI行にPRIMARY_LOCAL_TESTが残るがhandoff/Quick ReferenceではNoobAI-first。原行を保存し、本文で現在の優先度と比較baselineを区別。
- K-EVAL-004/H-K-014にはfreeze前文言が残る。mainのproduction population完成からRegistryのHOLDを勝手に閉じない。
- SW-01..04はBatch Nの研究問い。現行UIが変化していても本書では最適UXやgeneration-effectivenessへ昇格しない。
- 旧SD1.5の個々の技法を年代比較として説明する十分なscope付きClaimは不足。推測で歴史章を作らない。
- S-RESEARCH-004はsource registry自身でNegative mechanism backlogとして記録され、単一の論文URLが未登録。架空の出典で補わず固定版source registryへリンクする。

## 編集上の収録範囲

成人向け用語は臨床的語義、既存Claim、構造監査を収録する。露骨な性行為画像の具体的Prompt、Support列、生成最適化手順は収録対象外。この点ではユーザーの元タスクの全詳細要件を満たさない。原本を削除・書換えずリンクで追跡する。

## 閲覧確認の限界

PDF全ページの解析・レンダリングと1080×2400 phone-fit画像でQAする。Android/iPhone実機のPDF viewerでのタップと視覚確認は本環境では実施していない。実機PASSとは呼ばない。
