# PRODUCT_GOAL_LOCK.md

## 目的をここで固定する

このプロジェクトの第一目的は、検索機能そのもの、統計分析そのもの、辞書編集そのもの、または自動Prompt生成そのものではない。

> 画像生成初心者かつ英語・Danbooruタグ知識が十分でないユーザーでも、
> 今のPromptを日本語で理解し、知らないタグを日本語検索やジャンル閲覧から発見し、
> Special / General の意味を見ながら自分で選択して、
> 最終的に canonical English Prompt として生成環境へ渡せるようにする。

プロダクトの中核操作は **理解 -> 発見 -> 選択 -> 出力** とする。

この目的は、2026-09-12 の原点再確認によって旧「Special -> 共起補助 -> Prompt」を主目的とする定義から更新した。
今後の再定義は、実利用または検証でこの前提が崩れた場合に限る。

## 想定ユーザーと原点

- 画像生成の初心者
- 英語が強くない
- Danbooruタグ名を事前に知らない
- とくにニッチな表現について「何というタグか」「どういう意味か」を知りたい
- 既存Promptに何が書かれているかを日本語で理解したい
- 見つけたタグを自分で追加・削除して試したい

「ニッチなタグが実際の生成で効くか知りたい」という動機は保持するが、モデル別成功判定・A/B実験管理・ローカル結果記録は v1 必須機能にはしない。生成効果の実証は将来の独立レーンで扱う。

## 主従

### 主役 1: Special Core Dictionary

Special Core Dictionary は、検索語そのものを知らないニッチ・複雑な概念を発見するための深い辞書とする。

- Japanese-first display
- Japanese / English / canonical / approved Alias 検索
- ジャンル / サブジャンル閲覧
- 必要な複数閲覧経路
- canonical English identity の追跡可能性

現在のproduction snapshot/corpusは、互換上 `Special2788` として保持する。

### 主役 2: General Japanese overlay population

production Japanese overlay の 30,629 canonical entries は、通常タグを日本語で理解・検索・発見するための実用辞書として扱う。

Specialと同じ深さの意味ontologyは要求しない。Generalは Prompt 作業で役立つ浅い実用ジャンル分類を別sidecarとして持ち、初心者が「どんなタグが存在するか」をジャンルから発見できるようにする。

例:
- 人物・人数
- 身体・部位
- 髪・顔
- 表情・感情
- ポーズ・動き
- 構図・画角
- 視線・向き
- 衣装
- 着脱・露出
- 行為・接触
- 道具・小物
- 場所・背景
- 光・時間・天候
- 色
- 画風・品質

最終taxonomyは実データを見て確定する。分類は UI discovery index であり canonical semantic authority ではない。

### 補助 / 裏方

以下は主役ではなく、検索・候補提示・将来拡張を支える内部資産または任意機能とする。

- Alias
- 日本語 search synonyms
- Semantic Bridge
- Danbooru usage count
- true multi-tag AND / co-occurrence
- Candidate Aggregation
- Generation Profile
- generation knowledge corpus
- Recommendation
- Prompt support knowledge
- LoRA / control / evaluator knowledge

存在する内部機構を、作ったという理由だけで v1 UI に露出しない。

## v1 でユーザーが本当にしたいこと

1. 既存Promptを貼る、または空のPromptから始める
2. Prompt中の既知タグを日本語 + canonical Englishで理解する
3. 不要なタグを外す
4. 日本語または英語でSpecial / Generalを検索する
5. Specialをジャンルから深く発見する
6. Generalを実用ジャンルから広く発見する
7. 欲しいタグを自分でPromptへ追加・削除・並べ替えする
8. canonical English Promptをコピーして生成環境へ渡す

## v1 で必須にしないもの

以下は将来候補または開発/検証用資産であり、v1完成条件にはしない。

- モデル別のタグ検証状態表示
- 類似タグ比較専用UI
- A/B Prompt実験管理
- ニッチタグ効果の自動判定
- ローカル成功/失敗結果の記録機能
- 自動support挿入
- 自動minimum-sufficient Prompt生成
- 自動conflict解決
- 自動Negative生成
- 自動model-family Prompt rewrite
- 自動失敗診断
- evaluator confidenceのユーザー向け成功率化
- Raw Lift / recommendation scoreを中心にしたUI
- Generation Profile / knowledge dashboardの全面露出
- 11M投稿・約3GB full statistics indexを通常利用の必須条件にすること
- Forge / ComfyUIへの直接生成連携をv1必須にすること

## やらない主従逆転

- 10万件超の全Danbooru検索を主画面にしない
- 共起ランキング自体を目的にしない
- 統計指標を初心者に理解させることを前提にしない
- autocompleteの豪華さを最優先にしない
- Special Core Dictionaryを単なるbadge付き候補に格下げしない
- General 30,629件をSpecialと同じ深さで過剰監修しない
- 高度な自動化のために「自分で意味を理解して選べる」という原点を壊さない

## 完成時の最小操作

既存Promptを貼る / 空から開始
-> 日本語で内容を理解する
-> 日本語・英語検索またはジャンル閲覧でタグを発見する
-> Special / Generalを自分で選ぶ
-> Promptへ追加・削除する
-> canonical English Promptをコピーする

## Stage10 / generation-effectiveness の位置づけ

Stage10やgeneration knowledgeは捨てない。
ただし、v1が「モデルごとの成功率」「自動最適Prompt」「効く/効かない判定」を約束しない限り、Stage10 production A/Bをv1完成の必須Gateにはしない。

将来、モデル別有効性表示、support提案、A/B支援、失敗診断などを製品へ追加する場合に、必要な狭い検証だけを独立して行う。
