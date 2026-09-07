# AUXILIARY_TAG_ROLE_POLICY.md

## 目的

Core Tag Setだけでは固定しにくい生成要素を、
Danbooru全体と実共起から補う。

## Auxiliary Tagの例示的role

- composition
- pose
- expression
- clothing
- background
- situation
- detail
- body
- action
- other

これはUI整理用。
統計値を変えるための分類ではない。

## body / action / pose / composition の境界

- `body`: 身体特徴、体型、身体部位、外見的身体属性の受け皿
- `action`: 主体が行っている行為、またはinteractionの受け皿
- `pose`: 身体の姿勢、配置の受け皿
- `composition`: カメラ、画角、フレーミングの受け皿

`body`と`action`は成人向け専用roleではない。
既存roleと意味が重なるタグは無理に移動せず、判断できない場合は`other`とする。
`device`、`restraint`、`fluid`、`contact`、anatomy-specific subrole、
fetish-specific roleなどの細分化は追加しない。

## v1分類方針

全124,016タグを先に完全分類しない。

1. Recommendation上位に頻出するGeneralタグから分類
2. 未分類は `other`
3. 無理に分類しない
4. role辞書は独立データとして段階的に育てる
5. Codexが先に全タグ分類作業へ脱線しない

roleは推薦候補へ後付けする独立metadataであり、検索結果metadata、runtime index、
canonical overlay、統計値、既存保存データのschemaを変更しない。
したがって、全30,743 General tagsを事前に分類する必要はない。
未分類tagは引き続き`other`（または将来の内部`unclassified`相当）として安全に扱う。

## 「相性が悪い」の禁止

低共起だけで非互換・相性不良と断定しない。

使ってよい表現:
- 共起が少ない
- このsnapshotでは一緒に使われる例が少ない
- supportが少ない
- 参考値

使わない表現:
- 相性が悪い
- 組み合わせ不可
- 生成できない
- 競合する

実際のモデル生成上の競合はDanbooru共起だけでは証明できない。

## Recommendationの役割

「関連タグTop50」を出すだけではなく、
可能な範囲でrole別に整理する。

ただしrole未分類でも推薦対象から除外しない。
