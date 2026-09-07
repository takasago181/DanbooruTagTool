# TRIAL v0.2 実装メモ

## 再設計で反映したもの
- 日英同格入力。モード切替なし。
- internal canonical / UI display / Prompt outputを分離。
- 特殊2,788は重要レイヤーとして保持。
- 特殊辞書の比重は検索・表示・辞書関連候補で上げる。
- 統計数値の補正には使わない。
- LoRAはDanbooruタグとは別レイヤー。
- 最終出力のみPrompt-friendly space形式。
- 旧Prototypeの多スコア選択UIは廃止。
- 参考共起を使う場合、行列方向を input -> candidate として読む。
- 複数タグのペア共起を「正確なAND」と表示しない。

## 今回まだ実装していない本命機能
- 2026最新post-level metadataの正式採用
- tag -> post bitmap / post -> tag index
- 真のmulti-tag AND
- AND集合内の候補タグ実枚数
- 同一snapshotからの「普段より○倍」
- 一般12万タグの日本語辞書拡張
- LoRAフォルダ自動scan

これらはv0.2のデータ層・UIを壊さず追加できるよう分離している。
