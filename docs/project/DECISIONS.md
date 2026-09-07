# DECISIONS

重要な設計判断だけを残す。
日々の進捗は `CURRENT_STATE.md` に書く。

---

## D-001 常設4班制

Status: ADOPTED

常設:
- 本体開発班
- 監査班
- 知識班
- テストPrompt班

理由:
- 仕様決定・第三者監査・外部調査・実験Prompt作成を分離できる。
- これ以上の常設分割は個人開発では管理コストが増えやすい。

---

## D-002 Codexは独立班にしない

Status: ADOPTED

Codexは開発班の実装担当。
独立した仕様決定権を持たせない。

---

## D-003 Forge Neo環境準備は臨時担当

Status: ADOPTED

Stage10比較環境の導入・動作確認まで。
完了後は常設しない。

---

## D-004 Stage10実験実行・記録班は保留

Status: HOLD

Stage10で数試験を実行後、
Prompt作成より metadata保存・A/B評価・集計が重いと判明した場合のみ独立させる。

---

## D-005 Stage10実験知識をStage9へ先行固定しない

Status: ADOPTED

NoobAI / WAI / Illustrious / Anima のPrompt grammarはモデル差を保つ。
Stage10用framing、caption順、hybrid形式などを全モデル共通ルールへ昇格させない。
