Danbooru Tag Explorer TRIAL v0.2
=====================================

これは、これまで相談して再設計した内容を
実際に触って確認するためのローカル試用版です。

■ すぐ試せる機能
- 日本語 / 英語を同じ検索欄から検索
- 日本語と英語の混在入力
- comma区切り
- autocomplete
- 2026-09-02 Danbooru 124,016タグ
- 34,417 normalized alias index
- 特殊2,788語を重要レイヤーとして統合
- 特殊辞書の日本語表示
- 特殊辞書のカテゴリ関連候補
- canonical化
- Prompt用 underscore -> space 変換
- 重複除去
- 手動LoRA追加
- `english, english, <lora:name:weight>` 形式でコピー

■ 特殊2,788語
原本や監査済みデータも data/ 以下に同梱しています。

確定集計:
- Core 759
- Extended 915
- Alias 778
- Semantic 336
- canonical 1,674
- unique alias 767
- curated ambiguous alias 2
- unresolved ambiguous alias 9
- semantic/unmapped 336
- 一意canonical解決 2,443 / 2,788

特殊辞書だからという理由で使用数や共起率を水増しする処理はありません。
優先度は検索・表示・候補抽出で表現しています。

■ 起動
1. ZIPを展開
2. `START.bat`
3. 検索欄へ日本語または英語を入力

例:
  twintails
  ツインテール
  twintails, 制服
  school un

Enter / Tab / ダブルクリックで候補を追加できます。


■ 一般タグ日本語・試験辞書
特殊2,788語とは別に、試用しやすいよう一般的なPromptタグへ
少量の日本語検索語を追加しています。

例:
  ツインテール -> twintails
  制服 -> school_uniform
  長髪 -> long_hair
  座る -> sitting

これは `data/translation_seed_ja_trial.csv` に分離しており、
`UNREVIEWED_TRIAL` 扱いです。
特殊2,788語の監査済み対応や元CSVを上書きしていません。
最終版では正式な日本語辞書へ差し替え・拡張できます。

■ 参考共起（任意）
`DOWNLOAD_REFERENCE_COOCCURRENCE.bat`

を実行すると、約456MBの2026-05-18公開共起行列を取得します。
numpy用の .venv も自動作成します。

その後START.batを起動し「参考共起を読込」を押してください。

重要:
- 1タグの場合は「その入力タグの画像で候補タグも付く割合」の向きで読みます。
- 複数タグの場合は各入力とのペア共起をまとめた参考値です。
- 複数タグ全部を含む画像の正確なAND率ではありません。

■ なぜ最新post共起がまだ入っていない？
再設計後の本命は2026年post単位metadataから
A AND B AND C の実画像集合を作る方式です。

ただし採用する4GB級データセットはまだ実ファイル監査前なので、
試用版に勝手に固定していません。

このv0.2は
「UI・日英検索・特殊辞書・Prompt化を先に実際に触る」
ための版です。

■ データを壊さない
data/source と data/special2788 の原本は参照用です。
アプリはこれらへ書き込みません。
ランタイム検索は `data/catalog_20260902.json.gz` を読みます。
