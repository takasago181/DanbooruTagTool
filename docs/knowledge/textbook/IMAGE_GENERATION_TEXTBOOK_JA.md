# 画像生成を構造から理解する
スマートフォンで読む日本語技術教科書 / #44 Knowledge Corpus view / v1

## 第0章 この本の読み方
### 暗記から、観察へ
タグを知ることは、画像を作れることと同じではありません。名前が正しくても、人物・部位・構図の結び付きが崩れることがあります。本書では「何を表す語か」「どの条件で使う知識か」「画像のどこを観察するか」を分けます。
まず第2章で既存Promptを読み、第4章で構造に分解します。生成後に困ったら第11章へ進んでください。モデルの設定を移す前には第1章を読み直します。
POINT: 本書は知識の読書用ビューです。知識の正本、製品仕様、生成結果の判定を置き換えません。
CLAIMS: K-GOV-001 K-GOV-002 K-BIND-001
### 生成までの見取り図
Promptは意図を表す入力文字列です。Checkpointは学習済みモデルの実体、LoRAはその挙動を変える追加の重みです。Forge Neoは入力処理と推論を実行する環境であり、モデル名ではありません。
Sampler、Steps、CFG、Seed、解像度は実験条件です。Weightは入力の強調処理、Negative Promptは避けたい方向の条件付けです。同じ語でも、モデルと実行環境が変われば結果を移せるとは限りません。
FIGURE: pipeline
CLAIMS: K-GOV-001 K-TOOL-006 K-TOOL-007 K-EVID-004
### 判定ラベルを読む
ACCEPTEDは、指定されたscopeで知識として採用されたことを表します。実画像の最適性まで確認されたとは限りません。SOURCE_CLASSとVALIDATION_STATEを一緒に読みます。
CANDIDATEは候補、HOLDは必要な確認が残る状態、CONFLICTは両立しない根拠の対立です。REJECTEDは採用しない主張、HISTORICALは歴史上の記録です。本書の基準Registryではactive CONFLICTはありません。
HOLD: 作者の推奨設定を読んだだけでは、プロジェクトの難しい表現で成功率が確認されたことにはなりません。
CLAIMS: K-GOV-003 K-GOV-004 K-EVID-002
### 基準日と根拠の辿り方
本書は2026年10月1日に編集した、2026年9月17日までのcorpus更新を基準とする版です。「現行」はこの固定版の範囲を意味します。外部モデルやWebページの最新状態を保証する表現には使いません。
本文のClaim IDをタップすると知識索引へ移動できます。索引には元の英語Claim、判定、適用範囲、検証状態、根拠、最終確認日を保持します。本文で統合した説明は新しいClaimではありません。
注意: ledgerに古いWAI優先表現が残る箇所があります。現在の運用優先度はhandoffとQuick Referenceを優先し、原行は改変せず追跡資料に残します。
CLAIMS: K-GOV-001 K-GOV-003

## 第1章 画像生成モデルの基礎
### モデルを比較する軸
「一番強いモデル」を決めるより、自分の課題を分けます。語彙を出したいのか、人物の属性を分けたいのか、空間関係を描きたいのか、LoRA資産を使いたいのかで比較条件が変わります。
本書の実践主軸はNoobAI XL 1.1 EPS、関係や複数人物の比較先はAnimaです。WAI Illustrious v17は既存の比較・検証条件を理解するために保持します。これは性能ランキングではありません。
MODEL DEPENDENT: family、version、profile、実ファイルhashを一組で記録します。派生Checkpointへ作者設定を無条件で移しません。
CLAIMS: K-GOV-001 K-REJECT-001
### NoobAI XL 1.1 EPS
タグ中心の入力を学ぶ主軸です。作者資料はDanbooruとe621のnative tag captionを説明しています。e621語彙は学習表面の仮説に役立ちますが、Danbooruの意味を再定義しません。
作者設定の出発点はEuler a、25〜30 Steps、CFG 5〜6、SDXLの約1MP相当です。推奨範囲は最適値の証明ではありません。
captionの構成は人数 → character → series → artist → special → general → other。人間が考える順序とは別です。モデル側の品質語もDanbooruの検索メタデータとは分けます。
HOLD: rare tagの反応、正確な人数、部位・人物のbinding、Aliasと旧表記の差は未解決です。
CLAIMS: K-MODEL-NOOB-001 K-MODEL-NOOB-002 K-MODEL-NOOB-004 K-MODEL-NOOB-005
### NoobAI V-Pred 1.0
EPSと別の推論レーンです。catalogに記録された作者設定はEuler、28〜35 Steps、CFG 4〜5。EPSのEuler a設定と混同しません。
出力がノイズになる場合、語句を増やす前にprediction方式、runtime対応、metadataを確認します。V-Predの画像をEPSの反復結果へ混ぜると比較条件が壊れます。
MODEL DEPENDENT: 「暗部やコントラストに有利」というcommunityの報告は仮説です。全用途での優位を採用していません。
CLAIMS: K-MODEL-NOOB-003 K-MODEL-NOOB-005 K-GOV-004
### Illustriousと派生Checkpoint
Illustrious early/baseはBooru指向の入力を説明し、重要な構図語を重ねすぎると衝突することを警告しています。close-upと別の画角指定を足すほど精密になる、と考えないことが出発点です。
研究が示す豊かなcaptionや文脈の価値は、派生Checkpointの具体的な反応を証明しません。baseにdefault styleがないという説明も、派生版の画風へ一般化できません。
POINT: 同じfamilyのLoRAは試す候補になっても、互換性の保証にはなりません。
CLAIMS: K-MODEL-ILL-001 K-MODEL-ILL-002 K-MODEL-ILL-003
### WAI Illustrious v17
作者資料の推奨はForge Neo、Euler a、15〜30 Steps、CFG 5〜7、統合VAEです。元画像の面積は1024×1024より大きく、1024×1344の例があります。
プロジェクトには25 Steps、CFG 5、補助処理OFFの分離用条件が残ります。これはhard targetの最適値ではありません。現在の実践主軸が変わっても、WAIのACCEPTED判定を変更しません。
長いquality列やNegative列への警告、Hiresによる手足の修復はWAI17の作者ガイドとして読みます。base画像と修復後画像は別の証拠です。
CLAIMS: K-MODEL-WAI-001 K-MODEL-WAI-002 K-MODEL-WAI-003 K-MODEL-WAI-004 K-MODEL-WAI-005 K-MODEL-WAI-006
### Animaの入力表面
Animaはタグ・自然文・混在入力を説明するfamilyです。作者資料は小文字と空白、必要に応じたGelbooru形、artistの@接頭辞を扱います。辞書のcanonical identityを変更する指示ではありません。
groupingは品質/meta/year/safety → 人数 → character → series → artist → general。section内の順序は任意とされます。NoobAIの構成と同じではありません。
HOLD: 自然文が使えることと、複数人物のbindingが解決することは別です。tag-onlyと短いhybrid文の優劣はprofile別の確認が必要です。
CLAIMS: K-MODEL-ANIMA-002 K-MODEL-ANIMA-003 K-MODEL-ANIMA-004 K-MODEL-ANIMA-005 K-SEM-005
### Anima Base・Aesthetic・Turbo
Base v1.0は柔軟性と多様性を重視し、作者がLoRA学習のbaseとするprofileです。catalogの通常生成ガイドには30〜50 Steps、CFG 4〜5が記録されています。
Aesthetic v1.1はquality tagをcaptionから除いて学習されています。positiveのquality tagは必須ではなく、作者はPositive/Negative双方のscore_*を避けるよう案内しています。
Turbo v1.1はCFG 1、8〜12 Stepsの蒸留profileです。速いだけのBaseと考えず、Negativeの役割や多様性も別条件として扱います。
MODEL DEPENDENT: 3 profileのhashは巻末version台帳から辿れます。community 2.9B/3.8B派生版は別のwatch対象です。
CLAIMS: K-MODEL-ANIMA-001 K-MODEL-ANIMA-006 K-GOV-001
### Forge Neoは実行環境
Forge Neoはモデルを読み込み、Prompt処理と推論、追加機能を実行します。名前だけでparser・weight・拡張機能の同一性を判断しません。local remoteとcommitも記録します。
corpusの2026年9月17日確認ではAnima系やregional/control機能の対応が記録されています。対応表は成功率の証明ではありません。
POINT: runtime、checkpoint、LoRA、control、postprocessを別々に記録すると、モデル変更と処理変更を区別できます。
CLAIMS: K-TOOL-007 K-TOOL-001 K-EVID-004

## 第2章 Danbooruタグを理解する
### 名前・別名・包含関係
canonical tagは辞書の基準identityです。Aliasはidentityの対応、Implicationは包含関係です。「一緒によく出る」だけのrelatedや共起とは区別します。
意味が同じAliasでも、Checkpointが同じ反応を返す保証はありません。学習時の古い語形、現在の語形、モデル固有triggerが離れている場合があります。
HOLD: 表記差を比較するとき、生成前に全部canonicalへ置換すると比較対象が消えます。比較用のraw surfaceは保持します。
CLAIMS: K-SEM-001 K-SEM-003 K-SEM-004
### categoryと役割を分ける
DanbooruのGeneral、Character、Copyright、Artist、Metaはタグ側の分類です。画像中でのSubject、Pose、Viewpoint、Relationといった説明役割とは別の軸です。
Artist identityは作者を示します。「この画風を適用する」というcanonical意味ではありません。モデルがartist表記へ反応することは、モデル固有の学習挙動として別に扱います。
POINT: 日本語で分かりやすく説明するために、英語identityを別概念へ変更しません。1つの語が複数の説明役割を持つこともあります。
CLAIMS: K-SEM-007 K-PROMPT-005 K-GOV-002
### カンマ区切りはすべてタグか
既存Promptにはcanonical、Alias、runtime構文、モデル慣習、自然文、未知の語が混在します。先にsurface typeを分類してから意味を付けます。
例としてstandingは姿勢を表す語、(standing:1.2)は姿勢語を強調するruntime表面、BREAKは処理構文です。score_7と検索用score:は別レイヤーです。
注意: 検索のfuzzy候補を、貼り付けたPromptの確定した意味に昇格しません。分からない語はunknown/ambiguousのまま保持します。
CLAIMS: K-GOV-005 K-GOV-006 K-SEM-008 K-TOOL-006
### post countは何を教えるか
post countはDanbooru上の利用を知る補助情報です。今の件数からCheckpointの学習量や概念知識の確率を直接計算できません。
学習datasetの時期、選別、caption表記が違うためです。rare tagが出ない場合も、語形、単独実現、複合条件、可視性の順で問題を分けます。
POINT: タグの意味を知る調査と、モデルで効くかを調べる実験を分けると、1枚の失敗で辞書の意味を否定せずに済みます。
CLAIMS: K-SEM-006 K-REJECT-003 K-EVID-001

## 第3章 Special・Supportという考え方
### 核と補助を分ける
Special Coreは選んだ概念のidentityです。Support Knowledgeはその概念を理解・観察・試行するための補助知識、Manual Auxiliaryはユーザーが明示して加える補助要素として読みます。
Specialを選んだだけで、人物のownership、必要な部位、見える画角が十分とは限りません。ただし関連タグを自動的に追加すればよい、という結論にもなりません。
FIGURE: support
CLAIMS: K-SUPPORT-001 K-PROMPT-001 K-GOV-002
### Supportの六つの役割
Meaningは意味の構成要素、Geometry/Kinematicは成立する配置や動き、Visibilityは判定に必要な画角と見え方です。
Resource disambiguationは人物・手・物体などの帰属を区別する役割です。古いresource parkingという語を見ても、canonical identityと混ぜません。
Aestheticは画風・光・表情などの仕上げ、Redundant decorationは意味や観察への価値が未確認の装飾です。六つを分けると、何を補うために追加したか説明できます。
CLAIMS: K-SUPPORT-001
### Supportが邪魔になるとき
意味として矛盾しない語も、画角、人数、ownership、Negativeとの競合によってanti-supportになり得ます。全身を示すfull bodyが、細部の観察を妨げる例を考えてください。
「広い概念＋具体的概念」はいつも補強でも、いつも冗長でもありません。specific-only、broad-only、combinedを分けて調べる必要があります。
HOLD: WAI17のrare targetでbroad+specificが助けるか、薄めるかは未確定です。
CLAIMS: K-SUPPORT-002 K-SUPPORT-003 K-SUPPORT-004 K-REJECT-002 K-REJECT-009

## 第4章 Promptの組み立て方
### 一つの文を役割へ分解する
誰を描くかがSubject、何をしているかがAction、誰と何が結び付くかがRelationです。Body siteは対象部位、Poseは身体配置、Viewpointは観察位置、Compositionは画面内の構成です。
Expression、Clothing、Environment、Quality/Styleは人物や場面を調整します。Negativeは別の条件付けchannelです。この分解は考えるための座標であり、モデル共通の入力順ではありません。
FIGURE: prompt
CLAIMS: K-PROMPT-003 K-PROMPT-005 K-NEG-003
### 短い非性的な練習例
ここでは成人1人が座っている場面を、構造の読み方の練習に使います。生成成功が検証された完成レシピではありません。
PROMPT Subject: 1girl
PROMPT Pose: sitting
PROMPT Viewpoint: from above
PROMPT Expression: smile
PROMPT Environment: simple background
Poseを変えれば姿勢、Viewpointを変えれば観察方向が変わることを意図します。実際の結果が意図どおりかは別に観察します。人数語は年齢を保証する語ではありません。
CLAIMS: K-PROMPT-005 K-GOV-003
### 人間の計画順とモデル順
人間は「誰が何をするか」から考えると不足条件を見つけやすくなります。一方、モデルにはcaptionのgroupingがあり、browseの入口にも別の分類があります。
タグを見つけた順に出力することが、全モデルで最適とは限りません。NoobAIとAnimaの作者ガイドだけでもgroupingが違います。
注意: Batch Nのscene skeletonは既存Claimの統合整理です。最適なクリック順も、万能なPrompt文法も確定していません。
CLAIMS: K-MODEL-NOOB-001 K-MODEL-ANIMA-005 K-REJECT-001
### 最小十分は最短ではない
残すのは意味の核です。identity、必要なrelation、部位、人数、道具など、目標を定義する条件を削ると別の画像になります。
整理するときは、無関係な装飾、重複語、同じ役割で衝突する画角、未確認の親概念から一つずつ比較します。意味の核まで一括削除して成功率を語らないようにします。
POINT: 長さだけでPromptを評価しません。短くても複数人物のownershipが絡むと難しく、長くても条件が両立する場合があります。
CLAIMS: K-PROMPT-001 K-PROMPT-002 K-REJECT-008

## 第5章 Weight
### 記法とモデル反応は別
tag、(tag)、(tag:1.2)は、同じ語を異なる強調表面で渡す例です。A1111由来のruntimeでは括弧によるattentionと数値weightを処理します。
これは辞書の意味を変えません。また、指定値を画像中の強さや成功率の倍率へ直接換算できません。local Forge Neoのparserやconfigが確認されるまで、A1111と完全同一ともみなしません。
MODEL DEPENDENT: 本書は全モデル共通の最適weightを提示しません。parser仕様の根拠と、実画像の効果の根拠を分けます。
CLAIMS: K-TOOL-006 K-TOOL-007 K-GOV-001
### 強調する前に構造を見る
対象が出ないとき、先に画角・geometry・ownership・競合を調べます。見えないものを強く要求しても、必要な関係が解決するとは限りません。
Weight変更後は対象だけでなく、人物の配置、他の属性、画風も観察します。過剰weightによるanatomy崩壊などの閾値はこのcorpusに確定していないため、数字を創作しません。
HOLD: semantic bleedやstyle dominanceを一律のweight値へ結び付ける根拠は不足しています。失敗の記録項目として扱います。
CLAIMS: K-PROMPT-002 K-SUPPORT-002 K-GOV-001
### Token・chunk・BREAK
Tokenは文字数やタグ数と同じではありません。Batch Dが参照するA1111の仕様では長いPromptを75-token chunkへ分け、BREAKは新しいchunkを開始します。
BREAKはDanbooruタグでも、人物のownershipを保証する命令でもありません。chunk先頭へ置くと必ず強くなる、75 token以内なら競合しない、といった結論は採用されていません。
注意: この仕組みはA1111のruntime説明です。Animaや各Forge実装へ、同じtoken処理を無条件で適用しません。
CLAIMS: K-TOOL-006 K-TOOL-007 K-PROMPT-002

## 第6章 Negative Prompt
### 掃除ではなく、条件への介入
Negativeは避ける方向を入力する条件付けです。quality、artifact、semanticな不要要素を同じ長い列へ足しても、無害な掃除にはなりません。
目標に必要な特徴とNegativeが重なると、対象を抑える可能性があります。Positiveだけを読んで原因を決めず、Negativeも意味の条件として読みます。
POINT: bad anatomyという一般的な語だけで、すべての身体・人数の問題を解決できるとは扱いません。
CLAIMS: K-NEG-001 K-REJECT-005 K-REJECT-010
### 作者レシピをそのまま移さない
WAI17は短いquality/Negativeの出発点と、長すぎる列への警告を持ちます。NoobAI作者例のNegativeにnsfwがあることも、意図に関係なく入れる理由にはなりません。
Anima Aestheticのscore_*回避やTurboのCFG1はprofile固有です。同じfamilyの名前があっても、Negativeの運用を同一にしません。
MODEL DEPENDENT: 作者ガイド、モデルの学習慣習、目標との意味的重なりを三つに分けて読みます。
CLAIMS: K-NEG-003 K-MODEL-WAI-002 K-MODEL-ANIMA-006 K-MODEL-ANIMA-001
### OFFとONを比較する
不要要素を抑えたい実験では、同じ条件のNegative OFF/ONを比較します。一度に多数の語を変えると、どの条件が対象と衝突したか分かりません。
成功画像だけでなく、両方失敗、同程度、判定不能も残します。意図した要素が消えたか、不要要素だけが減ったかを分けます。
HOLD: WAI17、NoobAI、Animaの特殊なanatomy/countに対する正確なON/OFF効果は未解決です。
CLAIMS: K-NEG-002 K-EVID-003

## 第7章 Pose・Viewpoint・Composition
### 身体配置と観察位置
standingやsittingはPoseの説明です。from aboveやfrom belowはViewpointです。身体がどちらを向くかというOrientationはさらに別です。
頭上から見ることと、人物が下を向くことを混同しないようにします。複数の役割を持つタグもありますが、役割の説明がcanonical identityを変更するわけではありません。
FIGURE: camera
CLAIMS: K-PROMPT-003 K-PROMPT-005
### Frameと見える範囲
full body、upper body、close-upは見せる範囲を考える語です。POVやmultiple viewsも単なる姿勢語とは分けて扱います。
全体配置を観察したいか、手元など局所関係を観察したいかで必要なFrameが違います。close-upと広い全身画角を無意識に積むと、目標が両立しなくなります。
注意: 本書は各タグの語義辞典を創作しません。細かな境界は現行Wikiとcanonical情報へ辿って確認します。
CLAIMS: K-PROMPT-003 K-MODEL-ILL-001 K-REJECT-009
### 順番だけでは解決しない問題
物体があるのに隠れている、手が対象に届かない、相対位置が成立しない場合、タグの順番以外にVisibilityとGeometryを調べます。
関係が間違っている状態で見栄えだけを修復すると、正しくなったように見える危険があります。観察できない条件は成功とも失敗とも断定しません。
POINT: Frame、Viewpoint、Orientation、Visibility、Relationを別欄で記録すると、衝突の場所が分かります。
CLAIMS: K-PROMPT-003 K-BIND-001 K-TOOL-001

## 第8章 複数人物
### 人物がいることと、関係が正しいこと
成人Aが成人Bへ本を渡す非性的な例を考えます。2人と本が描かれていても、渡す側、受け取る側、持っている手が正しいとは限りません。
Actorは行為の主体、Targetは相手や対象、Ownershipは物体や属性の帰属です。左右は視点との関係もあるため、Prompt内の距離だけで所属を判断しません。
FIGURE: binding
CLAIMS: K-BIND-001 K-MODEL-ANIMA-003
### 属性の混線を読む
Clothing leakageは衣服条件の混線、attribute leakageは髪色などの混線、identity mixingは人物identityの混合です。pose collisionは配置の競合、background intrusionは余分な人物の侵入として観察します。
これらの症状名だけから原因を一つに決めません。人数、見分ける特徴、ownership、geometry、背景を分けて実画像を読みます。
MODEL DEPENDENT: Animaの明示的な人物説明は作者ガイドにありますが、自然文で全混線が解決するというClaimはありません。
CLAIMS: K-BIND-001 K-MODEL-ANIMA-003 K-MODEL-ANIMA-005
### A_ONLY・B_ONLY・AB
単独条件AとBを別々に確認してから、組み合わせABを観察します。AもBも出るのにABだけ崩れるなら、概念が未知だと結論する前に競合・binding・geometryを疑います。
ここでA/Bは人物名とは限りません。例えば「座る」と「本を持つ」という概念条件のラベルにも使えます。Actor A/Bと実験条件A/Bを記録上で区別します。
FIGURE: experiment
CLAIMS: K-BIND-002 K-EVID-003
### 地域制御は補助レーン
短い明示的な関係説明でも空間の混線が残る場合、Forge CoupleやControlNetは外部補助の候補です。regionalは画面領域へ条件を分配する処理として扱います。
corpusのForge Couple説明では総人数を残し、Checkpointが構成を理解できることが前提です。領域を分ければどんな関係も描けるとはしていません。
HOLD: Prompt-onlyから補助処理へ進む普遍的な閾値はありません。補助で成功した画像はbase能力の証拠と分けます。
CLAIMS: K-TOOL-003 K-TOOL-004 K-TOOL-001

## 第9章 成人向け用語と構造監査
### この章の対象と読み方
成人向けの専門語も、臨床的な語義、canonical表面、資料の判定を分けて扱います。解剖、接触、行為、関係、体液、配置、可視性は同じ概念ではありません。
この章は意味と既存研究の監査構造を整理します。露骨な性行為画像を作る具体的Prompt、Support列、生成の最適化手順は収録しません。収録範囲の差は巻末gapsにも記録します。
POINT: 性的用語を伏字にせず、成人・合意という原資料のscopeと、モデル別HOLDを維持します。画像例は使用しません。
CLAIMS: K-HARD-001 K-GOV-001
### Anatomy・身体部位の語彙
nippleは乳頭、penisは陰茎を指す解剖学的名称です。pussyは外陰部を指す俗称の表面で、医学的なvagina（腟）と単純に同一化すると部位の説明がずれます。
胸部、口、舌、外性器などの部位語は、行為や接触をそれだけで表しません。body-siteは「どこか」、ownershipは「誰の部位か」という別の条件です。
注意: このページの日本語は臨床的な理解補助です。個々のタグの厳密なcanonical境界やAliasは現行Wikiで再確認する必要があり、生成効果を追加したClaimではありません。
CLAIMS: K-HARD-002 K-SEM-001 K-BIND-001
### Action・Contact・Relation
sexは性行為、fellatioは陰茎への口を用いる性的接触、paizuriは乳房を用いる性的行為を指す名称です。analとvaginalはそれぞれ肛門・腟に関わる表面で、単語だけから主体・対象・全状況を補いません。
行為名と、誰が誰へ関わるかというRelationは別です。原資料はsite、action、implement、count、ownershipを分離して監査しています。名称の存在を関係の正しさへ読み替えません。
MODEL DEPENDENT: WAI17やNoobAIの正確なbody-site/actor-target能力はHOLDです。本書は実際に生成できるという保証を加えません。
CLAIMS: K-HARD-002 K-HARD-007 K-MODEL-NOOB-004 K-BIND-001
### Fluid・体液の意味
cumは精液を指す俗称です。射精という出来事、精液という物質、付着した状態は区別します。onは表面、inは内部、fromは出所という関係を読む手掛かりですが、文字列だけでタグidentityを確定しません。
原資料はmaterial、source、destination、state、quantityを別の観察項目にします。物質が見えることだけでは、出所や付着先が合っているという判定になりません。
POINT: 他の体液や排泄物も物質名と関係・状態を分けるという監査原則の対象です。具体的な描写生成手順へは変換しません。
CLAIMS: K-HARD-006 K-BIND-001 K-GOV-005
### 用語カード cum_on_body
意味: 身体表面への精液付着を表すタグ表面です。ここでは語の理解補助として記載し、細かなWiki境界は再確認対象とします。
資料上の役割: Fluidの物質・付着先・状態を区別するための例です。行為そのものや、出所の人物が正しいことをこの表面だけで証明しません。
関連する概念: cum、destination、body-site、ownership、visible state。これらは関連概念であり、同義タグや推奨Prompt列ではありません。
典型的な判定誤り: 物質の存在だけで全関係を成功とすること。モデル依存性: 当該表面固有の成功率はRegistryにありません。Support候補と最適化値は本書の収録範囲外です。
CLAIMS: K-HARD-006 K-BIND-001 K-HARD-007
### 拘束・装置・非人間appendage
拘束はrope/cuffの存在と必要な接続topologyを分けます。装置はobjectの存在とfunctional relationを分けます。appendageはsource、ownership、roleを別に追跡します。
原資料にはBDSM、machine/device、tentacle/fantasyという研究入口があります。性癖の名称をまとめて一つの能力とせず、何を監査している資料かを区別するために保持します。
HOLD: WAI17でのtopology、装置関係、appendage ownershipの正確な限界は未確定です。資料があることを画像生成能力の実証と誤認しません。
CLAIMS: K-HARD-003 K-HARD-004 K-HARD-005 K-HARD-007
### Pose・Visibility・Multiple actors
身体配置とカメラ位置、見える部位と実際の関係は別です。複数人物では対象人物の逆転、部位ownershipの混線、人数違いが一括スコアの陰に隠れる可能性があります。
原資料はbody-site、exact count、source-destination、topologyを独立条件として扱います。成人向け資料でも同じ判定原則を使い、presenceだけで成功とはしません。
注意: rareな概念がTagger語彙外である場合、出力がないことは画像失敗の証明になりません。人間の観察と機械の表現能力も分けます。
CLAIMS: K-HARD-001 K-HARD-002 K-BIND-001 K-EVAL-005
### 失敗記録と不足情報
意味を間違えたのか、geometryが成立しないのか、bindingが逆なのか、見えないのかを分けて原資料を読みます。「poseだけ存在する」「物質だけ存在する」という結果は全目標の達成と同じではありません。
個々の性的用語の生成上の成功率、モデル比較、Support組み合わせの普遍的効能は本書では補いません。原研究にあるscopeとHOLDへ戻ります。
HOLD: scene planningを整理したBatch Nも、既存のmodel-effectiveness HOLDを閉じていません。成人向け章にも本文と同じ文字サイズ・行間を使用します。
CLAIMS: K-HARD-007 K-MODEL-NOOB-004 K-MODEL-ANIMA-004 K-EVAL-005

## 第10章 LoRAと補助処理
### LoRAは学習済みの介入
LoRAにはcharacter、style、pose、conceptなどの役割があります。望む特徴だけでなく、学習時の背景、画角、衣服、姿勢などの文脈を持ち込む場合があります。
名前、ファイル、weight、学習base、推論Checkpoint、triggerを記録します。triggerを書かずに読み込んだ状態も、baseと同じとは限りません。
POINT: LoRA strengthはadapterの介入量、Prompt weightは文字列条件の強調処理です。同じ数値でも同じ仕組みを意味しません。
CLAIMS: K-LORA-001 K-TOOL-006
### familyの互換性
Illustrious系LoRAをNoobAIで使うことは試す候補です。作者が宣言したbaseと、使うCheckpointの組み合わせを確認し、成功例だけから全面互換を宣言しません。
AnimaはSDXL/Illustrious/NoobAIと別familyです。officialの学習baseはAnima Baseであり、Base/Aesthetic/Turboで同じadapter挙動を前提にしません。
HOLD: プロジェクトのLoRA×Special/Support相互作用は未解決です。base、adapter A、adapter B、A+Bを分ける比較が必要です。
CLAIMS: K-LORA-001 K-LORA-002 K-GOV-001
### Hires・ADetailer・inpaint
Hiresは解像度だけの変更ではありません。形状や細部が修復・変更される場合があります。base画像とfinal画像を両方保存します。
ADetailerは検出 → mask → inpaintの後処理です。独自のPromptや設定を使う場合があり、人物の検出順はactorの意味的なauthorityではありません。
inpaintやimg2imgによる局所修復も編集補助の結果です。base失敗が修復で成功した場合、そのままbase Promptの能力とは扱いません。
FIGURE: intervention
CLAIMS: K-TOOL-001 K-TOOL-002 K-MODEL-WAI-003 K-REJECT-006

## 第11章 失敗画像の読み方
### F1〜F5を観察する
F1 Identity/exposure: 語形やtrigger、学習表面の問題を疑う区分です。F2 Unary realization: 単独条件として現れるかを分けます。
F3 Composition/competition: 組み合わせで消える問題です。F4 Binding/ownership: 属性、手、物体、主体と対象の帰属違いです。F5 Visibility/crop/occlusion: 隠れたり切れたりして判定できない問題です。
POINT: 失敗区分は原因を断定する名前ではありません。先に症状を分け、条件を比較して仮説を絞ります。
CLAIMS: K-BIND-001 K-BIND-002 K-SEM-004
### F6〜F10を観察する
F6 Prompt contradiction: 条件が衝突していないか。F7 Negative collision: 必要な意味を抑えていないか。F8 Family/settings mismatch: モデルと設定の組み合わせが正しいか。
F9 Postprocess/control confound: 補助が結果を変えたか。F10 Evaluator blindness: 機械評価が対象を表現できるか。この五つは、タグを増やす前に調べる別の経路です。
注意: 画像だけからruntime設定の誤りを確定しません。記録が足りなければTRACEABILITYから戻ります。
CLAIMS: K-NEG-001 K-TOOL-001 K-EVAL-005 K-EVID-004
### 診断の最初の四段階
まずCheckpoint/hash、runtime、実Prompt、Negative、Seed、補助ON/OFFを確認します。次にidentityと語形、単独概念、複合条件でのbindingを確認します。
それでも不明なら可視性・geometry、矛盾、Negative、density、LoRA、Seed、後処理、評価器へ進みます。原因が不明のまま一度に全部を変えません。
FIGURE: failure
CLAIMS: K-EVID-004 K-BIND-002 K-PROMPT-002 K-TOOL-001
### E0からE3へ
E0は少数のcase/debug。反例や仕組みの発見に役立ちますが、信頼性の推定ではありません。E1は予め決めたpaired seedsの反復で、全結果を残します。
E2は比較条件、サンプル、uncertainty、効果量、実用上の価値を明示した比較推論です。E3は複数の代表的意味条件とモデルscopeで一般化を検討します。
POINT: 「何seedなら証明」という万能の数はありません。結論の強さに合わせて証拠を設計します。
CLAIMS: K-EVID-001 K-EVID-002 K-EVID-003
### Taggerを正解判定器にしない
WD EVA02 v3はcommon/unaryの補助信号です。Kagami-24kは広い語彙の候補、CL Tagger v2はcalibration/threshold/OOD情報を持つ候補です。広い語彙はrare-tail精度の証明ではありません。
関係、人数、ownership、topologyを単独タグのscoreで代替しません。対象が語彙にあるか、semantic classが適切か、versionが固定か、人間観察と矛盾するかを確認します。
HOLD: K-EVAL-004の旧freeze前表現はRegistryのまま保持します。mainで辞書が進んだことから、knowledge側の判定を自動更新しません。
CLAIMS: K-EVAL-001 K-EVAL-002 K-EVAL-003 K-EVAL-004 K-EVAL-005 K-EVAL-006 K-EVAL-007 K-REJECT-007

## 第12章 実践ワークフロー
### 目的と核を先に決める
最初に画像の目的を短く書き、必須条件と装飾を分けます。SpecialやGeneralを発見したらcanonicalの意味を確認し、必要なSupportの役割だけを検討します。
人物、action/state、relation、部位、geometry、可視性を点検し、モデルの入力慣習へ合わせます。Weight、Negative、LoRAを増やす前に、条件が両立するかを読みます。
POINT: 読書用の順序は固定wizardでも自動Prompt構築でもありません。使う人の強いintentを出発点にします。
CLAIMS: K-PROMPT-001 K-PROMPT-003 K-SUPPORT-001 K-REJECT-001
### 生成と修正を一つの問にする
例えば非性的な「成人が椅子に座り、本を持つ」場面なら、最初に人数・姿勢・物体・ownershipが正しいかを観察します。光や画風が美しいだけで成功とはしません。
失敗区分を記録し、1回に一つの意味ある変更を試します。A/BでSeedと他の条件を揃え、両方の画像と実際の文字列を残します。random explorationと固定条件の診断を分けます。
CLAIMS: K-BIND-001 K-BIND-002 K-EVID-003 K-EVID-004
### 保存する実験カード
目的 / 必須条件 / 失敗区分を記録します。Checkpoint名とhash、runtime remote/commit、Sampler/Scheduler、Steps、CFG、解像度、Seedが中心条件です。
Positive/Negativeの実文字列、読み込んだLoRAとweight、Hires/ADetailer/control/regional状態、baseとfinal画像も残します。Dynamic Promptsなら展開後の文字列が必要です。
注意: Seedだけで環境を跨ぐ完全一致は保証されません。再現性のidentityと、複数Seedでの信頼性は別の軸です。
CLAIMS: K-EVID-004 K-TOOL-005 K-LORA-001
### 結果を勝敗だけにしない
A_ONLY_PASS、B_ONLY_PASS、BOTH_PASS、BOTH_FAILを区別します。同程度ならTIE、判断できなければUNCLEAR、条件が揃わなければBLOCKEDです。
相対的に良くなったことと、目標を絶対的に達成したことは別です。成功率の数字を出す場合は、失敗や判定不能をどう数えたかを明示します。
POINT: 新しい知識へ戻すのはscope付きの反復証拠です。単発の良い画像を全モデルのルールへ昇格しません。
CLAIMS: K-EVID-001 K-EVID-002 K-EVID-003

## 第13章 DanbooruTagToolでの活用
### 理解・発見・選択・出力
既存Promptを日本語とcanonical Englishで理解し、知らない表現を日本語・英語・混在検索やbrowseから発見します。意味を確認し、自分で追加・削除・並べ替えし、canonical Englishをコピーします。
本書は「この語が何を意味するか」「どの役割が不足しているか」を考える読書資料です。productionの分類や検索仕様を教科書の章立てへ変更しません。
POINT: Special/Generalの現行browseはmainのauthorityを使います。古いbranch-localの深い分類説明を現在のUIへそのまま適用しません。
CLAIMS: K-GOV-002 K-GOV-006 K-PROMPT-004
### ツールが自動では決めないこと
Supportの自動挿入、最小十分Promptの自動構築、Negativeの自動生成、モデルfamilyの自動rewrite、Promptだけからの失敗診断をv1の既定動作として説明しません。
候補を発見することと、画像での有効性を保証することは別です。未知の語や構造上の衝突を見つけても、ユーザーの明示的な選択なしに意味を変えません。
注意: Artistは現行UIで非表示、旧Character–Copyright関係UIは無効化された基準です。本書は関係修復や他laneの判断を取り込みません。
CLAIMS: K-PROMPT-004 K-GOV-006 K-GOV-002
### 知識が増えたとき
#44の新しいClaimとsourceを固定SHAで読み直し、inventoryとchapter mapを更新します。本文の説明、HOLD、scope、freshness、索引の参照切れを確認してから再生成します。
教科書の都合でRegistryを上書きしません。本文に足りない項目はKNOWLEDGE_GAPSへ残し、model-effectivenessの結論には指定された検証を別途必要とします。
POINT: このv1のstop pointは読書用成果物のreviewです。main merge、production反映、知識のGate PASSは宣言しません。
CLAIMS: K-GOV-001 K-GOV-003 K-GOV-004
