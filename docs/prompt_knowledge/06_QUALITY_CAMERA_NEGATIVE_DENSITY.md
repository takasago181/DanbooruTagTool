# 06 Quality, camera, Negative and density

Owner: PROMPT / Issue #5
Status: cross-cutting prompt knowledge. Not production specification.

## 目的

高品質化のための操作を、target semanticそのものと分けて扱う。

禁止する短絡:
- quality tagを増やすほど高品質
- Negativeを長くするほど破綻減少
- camera supportはtargetへ副作用なし
- weightを上げればfidelity向上
- Promptは短いほど良い

## Quality / Meta

高品質判定はquality tag数ではなく:
- target fidelity
- anatomy/coherence
- composition/readability
- identity consistency
- visual cleanliness
- style/aesthetic quality
- artifact rate
- binding correctness
を分けて見る。

### WAI17
作者側:
- `masterpiece, best quality, amazing quality`例
- quality/aesthetic過積載を警告

候補:
- lean minimumから開始
- expanded qualityは別A/B

### NoobAI 1.1
- official quality/date/prefix構造あり
- official prefixをbaselineとするがhard-target optimumではない

### Illustrious
- exact version dependent
- WAI derivativeのlean ruleをbaseへ自動継承しない

### Anima
- Base/Aesthetic/Turbo/derivative分離
- Aestheticはquality-light候補
- score_*過積載の副作用を公式が示す

## Negative

Negativeは単なるpass-throughや「多いほど安全」ではない。

分類:
1. artifact/quality Negative
2. domain/style Negative
3. scene-conflict Negative
4. target-neighbor collision risk

原則:
- target conceptや近接semanticを機械的にNegativeへ入れない
- family baselineから必要なfailure-specific追加だけ行う候補
- anatomy-sensitive targetではgeneric `bad anatomy / extra limbs / extra arms` 等がsemanticと衝突する可能性をHOLD

### WAI17
作者がoverly long Negativeでquality低下/blurを警告。

候補:
- minimal author family
- expanded Negativeを別A/B
- adult-target testで`nsfw`をNegativeのglobal defaultにしない

### NoobAI / Anima / Illustrious
- official examplesはbaseline
- adult hard-targetではsafety/meta tokenのcontext collisionを別評価

## Camera / framing / visibility

役割を分ける。

### Frame
- full body
- medium/upper/cowboy等のsubject scale

### Viewpoint
- front/side/back/overhead等の観測方向

### Orientation / Geometry
- body orientation
- pose-relative direction

### Visibility
- target regionがframe内・occlusionなしで判定可能か

原則:
- Frame / Viewpoint / Orientationを原則一系統ずつ
- same-role camera語の過積載を避ける
- `full body`を万能supportにしない
- local/body-site Specialではsubject size低下で判定性が落ちる可能性
- visibility support追加でpose/relationが変わるため、透明な補助と仮定しない

Stage10で記録:
- target visibility
- subject scale
- pose fidelity
- relation fidelity
- unintended composition drift

## Prompt density

単なるtoken数ではない。

測る候補:
- Special count
- relation count
- support block count
- same-role camera/pose count
- object count
- actor count
- aesthetic block count
- Negative concepts

テスト曲線:
`under-supported -> sufficient -> over-supported`

目的は最小文字数ではなく**minimum sufficient structure**。

## Weighting

### Syntax
A1111/Forge parserのweighting syntax自体はruntime/parser scopedで有効。

### 値
具体的な1.x/2.x等はmodel-specific。

現状:
- automatic weightingなし維持
- communityの成功weightをglobal defaultへしない
- 実画像で必要性が示されたtargetだけneutral vs one controlled weight

Animaはofficialにweightingが機能し、典型的SDXLより強いweight例があるが、これもglobal値にはしない。

## Quality vs target fidelity trade-off

別軸で記録する。

例:
- Q上昇 / target低下
- visibility上昇 / composition低下
- artifact減少 / Special retention低下

「綺麗になったので勝ち」を禁止。

## Hires / postprocess

Hiresはfinish/intervention。

- semantic baseline A/BはHires OFFを原則候補
- promising PromptだけHires confirmation
- baseとpost-Hiresを別評価

ADetailer等も同じくpre/post分離。

## LoRA

現在のPROMPT general rule:
- baseline recognition/grammar testではLoRA OFF
- LoRAを使う実験は独立variable
- LoRAがSpecial、style、bindingへ与えるinteractionはHOLD
- assisted/personalized successをbase checkpoint Prompt successへ混ぜない

## 詳細資料

- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
- `docs/stages/STAGE_10_PROMPT_HIGH_QUALITY_HARD_IMAGE_CONTRACT_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_REVALIDATION_BACKLOG_20260909.md`
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
