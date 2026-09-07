# Stage10 Prompt Replacement Candidate Reference

最終更新: 2026-09-08

## 位置づけ

Stage10のテストPrompt作成時に、ChatGPTが具体的に記述できない核心部分だけを置換札にする場合のPROMPT班向け参照ルール。

- 現在StageはStage 9B。Stage10本番開始を意味しない。
- Stage10正式handoff前の準備ルールであり、本体production仕様ではない。
- 本体仕様・Special意味正本を変更しない。
- 正式handoff / 正式Specialデータ / 正式実験仕様が渡された後は、それらを優先する。

## Prompt作成モード

PROMPT班は、ユーザー依頼の目的に応じて少なくとも以下の2モードを明示的に区別する。

### 1. 実験分離モード

Specialの成立可否・差分原因を観測しやすくするためのStage10 A/B向けPrompt。

- 原則1実験1疑問。
- A/Bの比較対象以外は可能な限り固定する。
- 品質タグ、装飾、複雑背景、人物属性、照明などは、観測に不要なら盛らない。
- 見栄えより因果分離・再現性・観測可能性を優先する。

### 2. ユーザー実戦Stress Testモード

ユーザーが実際に1枚を作る時に近い条件で、Specialを含む複雑・強い・難しいPromptを実戦的に組むモード。

- 純粋なA/B分離より、完成Promptとしての安定性と実用性を重視する。
- Special成立を阻害しない範囲で、quality、構図、身体の向き、camera、visibility、照明、表情、背景、negativeなどを必要に応じて補う。
- ただし無関係な要素を大量に盛って主題Specialを埋没させない。
- モデルfamily差を考慮し、全モデルへ同一grammarを機械的に流用しない。

ユーザーが「比較用ではなく普通にユーザーが作るようなテストPrompt」「実力を見るPrompt」等を求めた場合は、原則としてユーザー実戦Stress Testモードとして扱う。

## 基本ルール

1. ChatGPTが具体的に書ける成人向け内容は、予防的に置換札へ逃がさず具体的にPromptへ書く。
2. ChatGPTが具体的に書けない核心部分だけ、日本語の非Prompt置換札にする。
3. 置換札だけを提示してユーザーへタグ探索を丸投げしない。
4. 置換が必要な場合、Special2788参照辞書を使い、実在候補を併記する。
5. 候補は原則3パターン程度提示する。機械的な固定3種ではなく、対象内容に応じてPROMPT班が最適な3候補を選ぶ。
6. 各候補には、ユーザーが意味を判断できるよう**日本語名を必ず併記**する。
7. 候補には可能な限り以下を示す。
   - 日本語名
   - 英語Tag
   - Special ID
   - Layer（Core / Extended / Alias / Semantic）
   - post_count（ある場合）
   - Aliasの場合 canonical_target
   - その候補を選ぶ理由・用途を短く説明
8. 候補選定では、可能なら次の役割分担を優先する。
   - 候補1: 最も素直な第一候補。canonical + specificを優先。
   - 候補2: 代替候補。Alias、別canonical、近接specific等から選ぶ。
   - 候補3: 比較・補助候補。broad、Semantic、別強度・別表現等から目的に応じて選ぶ。
9. 上記3役は固定規則ではない。対象Specialのデータ状況に応じて、より良い3候補構成があればPROMPT班の判断で変更してよい。
10. canonical / Alias / Semanticを混同しない。
11. 複数の置換箇所がある場合は、A / B / Cのように部位・行為・状態を分ける。
12. Stage10の成人向けPromptでは未成年対象語を使用しない。

## 置換候補の標準出力形式

```text
【差し替えA：対象内容を日本語で説明】

候補1（第一候補）:
日本語: ...
Tag: ...
Special ID: ...
Layer: ...
post_count: ...
補足: ...

候補2（代替候補）:
日本語: ...
Tag: ...
Special ID: ...
Layer: ...
post_count: ...
canonical_target: ...   # Aliasの場合
補足: ...

候補3（比較・補助候補）:
日本語: ...
Tag: ...
Special ID: ...
Layer: ...
post_count: ...
補足: ...

推奨:
通常利用でどれを優先するか、何を比較する場合に候補2/3へ替えるかを短く説明する。
```

## 参照辞書

PROMPT班向け人間可読・GitHub検索可能な派生辞書:

- `data/special2788/prompt_reference/README.md`
- `data/special2788/prompt_reference/MANIFEST.txt`
- `data/special2788/prompt_reference/`
  - 01〜12はカテゴリ別ファイル
  - 13「その他・文脈」は1404件を8ファイルへ分割
  - 合計2788件

元のSpecial2788データを置き換える正本ではない。タグ探索・差し替え候補提示のための補助資料としてのみ使う。
