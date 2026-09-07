# RAW_SOURCE_SCHEMA.md

## danbooru-2026-09-02.csv

重要: HEADERなし。

各行4列:

0. `tag`
1. `category`
2. `post_count`
3. `aliases`

例の読み方:
`1girl,0,8363808,"sole_female,1girls"`

category mapping:
- 0 = General
- 1 = Artist
- 3 = Copyright
- 4 = Character
- 5 = Meta

注意:
- 1行目をheaderとして消費しない。
- `post_count` はタグ使用件数。
- モデル学習強度ではない。
- aliasesはカンマを含むquoted CSV fieldになり得る。
- raw canonicalはunderscore形式。
- Prompt出力時のみspace形式へ変換。

pytestで必ず:
- headerlessとして4列読める
- 124,016 canonical rows
- categoryが既知集合内
を確認する。
