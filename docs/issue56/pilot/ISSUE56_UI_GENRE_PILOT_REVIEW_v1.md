# Issue #56 Special UI Genre Pilot Review v1

Status: **FORMAL_150_REVIEW_COMPLETE / ISSUE59_REQUIRED_FIXES_APPLIED / REAUDIT_REQUIRED**

This document records the formal, reproducibly selected UI-browsing taxonomy pilot for the frozen 2,788-entry Special Core Dictionary and the minimal remediation required by Issue #59.

It is **not** a semantic revalidation of Special identity and does not mutate production/canonical data.

## 1. Evidence / reproducibility

Feature branch:
- `dev/issue56-special-dict-ui-taxonomy`

Selector:
- `tools/issue56_ui_genre_pilot_selector.py`
- selector version: `issue56-ui-pilot-v1`

Formal generated artifact metadata:
- source rows: **2,788**
- unique Special IDs: **2,788**
- formal pilot rows: **150**
- unique pilot IDs: **150**
- generated pilot CSV SHA-256: `3b970c6ec0d600087aaf89df642e669cd1744cc78a402e75027f9501f215a23e`
- materialized source CSV SHA-256: `d61b3ef93609db8d51f2e6ab4125bab86577a27ae95211dfc09523f49c1a9472`

Pre-audit GitHub Actions:
- run `34658973866`: selector/test/build/upload **SUCCESS**
- run `34659459056`: reviewed-map + taxonomy Japanese-label consistency tests **SUCCESS**

The formal global high-usage stratum is derived only after all current prompt-reference parts are materialized. The earlier exploratory part01 block is not treated as the global top-50.

## 2. Formal sample composition

| Stratum | Rows |
|---|---:|
| Global high-usage from old `その他・文脈` | 50 |
| Alias | 15 |
| Alias canonical controls | 15 |
| Body / exposure boundary | 6 |
| Activity / contact boundary | 6 |
| Tools / BDSM boundary | 6 |
| Role / meta / context boundary | 6 |
| Injury / body / BDSM boundary | 6 |
| Rare numeric | 10 |
| Rare non-count | 10 |
| Deterministic pseudo-random | 20 |
| **Total** | **150** |

The formal global high-usage 50 spans multiple old `その他` files:
- part01: 24
- part06: 13
- part05: 6
- part07: 6
- part03: 1

## 3. Human review result

Classification state before the Issue #59 remediation:

| Status | Rows |
|---|---:|
| `HUMAN_REVIEWED` | 124 |
| `AUTO_INHERITED_ALIAS` | 24 |
| `REVIEW_REQUIRED` | 2 |
| `AMBIGUOUS` | 0 |

Unresolved rows remain intentionally unresolved:
1. Special ID 1084 `arm slave (mecha)`
2. Special ID 1227 `cum on fourth wall`

The remediation does not force either row into a visible shelf.

## 4. Primary-genre distribution in the formal pilot

| Japanese UI genre | Rows |
|---|---:|
| 身体・解剖 | 31 |
| 裸体・衣服・露出 | 28 |
| 性行為・性的刺激 | 19 |
| 体液・排泄・汚損 | 11 |
| 拘束・BDSM・支配 | 10 |
| 属性・関係・役割 | 9 |
| メタ・レーティング | 8 |
| 道具・性具・機械 | 7 |
| 接触・挿入・部位行為 | 6 |
| 異形・非人間・触手・変形 | 6 |
| 損傷・R18G | 6 |
| 状況・場面 | 4 |
| ポーズ・体位・構図 | 3 |
| 未確定 | 2 |

The Issue #59 remediation changes only subgenre placement, not these top-level counts.

`生殖・妊娠・授乳` received zero formal selector rows. The earlier direct 14-row source inspection remains sufficient to keep the top-level concept as a candidate, while final membership remains subject to the later 01–12 cross-audit/full-distribution audit.

## 5. Secondary-path pressure

Before remediation:
- 0 paths: **86**
- 1 path: **60**
- 2 paths: **4**
- 3+ paths: **0**

The remediation removes duplicate body-part secondary paths from IDs 739 and 742 after merging `ABSENCE_VARIANT` into their natural body-part shelves. It does not introduce new secondary paths.

## 6. Top-level taxonomy decision

The 14 top-level genres remain unchanged:

1. 身体・解剖
2. 裸体・衣服・露出
3. ポーズ・体位・構図
4. 性行為・性的刺激
5. 接触・挿入・部位行為
6. 道具・性具・機械
7. 拘束・BDSM・支配
8. 体液・排泄・汚損
9. 生殖・妊娠・授乳
10. 異形・非人間・触手・変形
11. 損傷・R18G
12. 属性・関係・役割
13. メタ・レーティング
14. 状況・場面

`SITUATION_SCENE / 状況・場面` remains a narrow situation-first browsing genre, never a fallback for difficult rows. Its catch-all pressure must be checked again after the full 2,788 mapping.

## 7. Issue #59 required per-subgenre decision pass

Issue #59 returned `PASS_WITH_REQUIRED_FIXES`. FIX-1 required an explicit `ADOPT / MERGE / RENAME / DROP` evidence pass rather than blanket-keeping every candidate. FIX-2 required removal of visible `OTHER_BODY_SITE / その他部位`.

Decision rule:
- the UI question is whether a Japanese user would actually press the button as a first browsing route;
- zero/singleton Pilot support is not enough by itself;
- a zero/singleton candidate may remain only when the current 2,788 source contains a coherent recurring browse cluster;
- no third hierarchy is introduced;
- no visible `その他` shelf is allowed.

The current source evidence used for low-Pilot-count decisions includes:
- `01_身体・解剖.txt`: cross-section / x-ray / internal-view cluster and repeated cutout examples;
- `04_性行為・性的刺激.txt`: masturbation, oral activity, before/after, implied, rubbing and cooperative families;
- `05_挿入・性具・機械.txt`: generic/deep/multiple insertion and a 17-row urethral cluster;
- `06_拘束・BDSM・支配.txt`: named bondage positions, restraint devices, gags, chastity, dominance/submission and force/non-consent clusters.

| 大分類 | 副ジャンル | Pilot 主/副 | 代表例 | 判定 | UI価値・根拠 |
|---|---|---:|---|---|---|
| 身体・解剖 | `BREAST_NIPPLE` / 乳房・乳首 | 10/19 | 726, 2754, 725(sec) | **ADOPT** | Pilot頻度・副経路とも高く、身体部位として最初に押し分ける価値が明確。 |
| 身体・解剖 | `FEMALE_GENITAL` / 女性器 | 2/5 | 1248, 509, 728(sec) | **ADOPT** | 主経路は少数でも副経路需要が反復し、自然な身体部位棚。 |
| 身体・解剖 | `MALE_GENITAL` / 男性器 | 4/8 | 1246, 578, 730(sec) | **ADOPT** | 主・副とも反復し、自然な身体部位棚。 |
| 身体・解剖 | `BUTTOCK_ANUS` / 臀部・肛門 | 3/0 | 2359, 1580, 1 | **ADOPT** | 独立した閲覧意図が複数確認できる。 |
| 身体・解剖 | `INTERNAL_ANATOMY` / 体内・断面 | 0/0 | source IDs 2003–2012 | **ADOPT** | Pilot外だが現行sourceに cross-section / x-ray / internal view 等の連続した反復群があり、専用棚で一覧短縮効果がある。 |
| 身体・解剖 | `BODY_FORM_STATE` / 身体特徴・状態 | 1/0 | 2381 | **DROP** | 1件のみで定義も残余型。可視棚にせず `身体・解剖` 親へ置く。 |
| 身体・解剖 | `ABSENCE_VARIANT` / 欠損・非表示 | 2/0 | 739, 742 | **MERGE** | 欠損自体より対象部位を最初に探す方が自然。739→乳房・乳首、742→女性器へ統合。 |
| 身体・解剖 | `BODY_ADORNMENT_MARK` / 装飾・印 | 5/0 | 731, 2766, 744 | **ADOPT** | 装飾・穿孔・印を一つにまとめることで、部位別ピアス棚の乱立を防げる。 |
| 身体・解剖 | `PUBIC_HAIR` / 陰毛 | 4/1 | 2745, 2758, 2388(sec) | **ADOPT** | 反復件数があり、日本語ユーザーが独立して探しやすい。 |
| 裸体・衣服・露出 | `NUDITY_LEVEL` / 裸体・半裸 | 4/0 | 2386, 2389, 2400 | **ADOPT** | 全裸・半裸など全体露出レベルを押し分ける価値がある。 |
| 裸体・衣服・露出 | `UNDRESSING_ADJUSTMENT` / 脱衣・着崩し | 2/0 | 2063, 2053 | **ADOPT** | 脱衣・ずらし系は部分露出とは操作意図が異なり、まとまりがある。 |
| 裸体・衣服・露出 | `PARTIAL_EXPOSURE` / 部分露出 | 10/0 | 728, 1727, 2387 | **ADOPT** | Pilotで強い反復があり、閲覧短縮効果が明確。 |
| 裸体・衣服・露出 | `COVERED_CONCEALED` / 隠し・覆い | 4/2 | 725, 2385, 748(sec) | **ADOPT** | 隠す・覆う状態は主副とも反復し、自然な入口。 |
| 裸体・衣服・露出 | `THROUGH_CLOTHING_VISIBILITY` / 透け・衣服越し | 3/2 | 2384, 2768, 1056(sec) | **ADOPT** | 透けだけでなく衣服越し形状を含む再命名後の範囲がPilotで支持された。 |
| 裸体・衣服・露出 | `CUTOUT_OPENING` / 開口・カットアウト | 1/0 | 2072; source IDs 516, 2169, 2172 | **ADOPT** | Pilotは1件だがsourceに pussy/breast/cleavage cutout の反復群があり、衣装構造として自然な棚。 |
| 裸体・衣服・露出 | `UNDERWEAR_LINGERIE` / 下着・ランジェリー | 3/2 | 2505, 2637, 2521(sec) | **ADOPT** | 主副とも反復し、露出系の閲覧入口として有用。 |
| 裸体・衣服・露出 | `REVEALING_OUTFIT` / 露出衣装 | 1/0 | 2526 | **DROP** | 1件のみで衣装一般へ拡張しやすい。専用棚を作らず親ジャンルへ置く。 |
| 性行為・性的刺激 | `GENERAL_SEX_ACT` / 性交・性行為 | 5/3 | 546, 541, 1517(sec) | **ADOPT** | 広い行為群の基礎棚として主副とも利用される。 |
| 性行為・性的刺激 | `MASTURBATION` / 自慰 | 0/1 | 660(sec); source IDs 84–99 | **ADOPT** | Pilot主経路0でもsourceに after/implied/mutual/through clothes 等の大きな連続群があり、独立閲覧価値が明確。 |
| 性行為・性的刺激 | `ORAL_ACTIVITY` / 口淫 | 0/0 | source IDs 100–116 | **ADOPT** | fellatio/anilingus/deepthroat/implied/cooperative 等の大きな反復群があり、親に埋めるより押し分ける価値が高い。 |
| 性行為・性的刺激 | `HAND_FOOT_BODY_STIMULATION` / 手・足・身体刺激 | 4/0 | 743, 1235, 44 | **ADOPT** | 複数の身体部位刺激を一棚にまとめ、細分化を防ぎつつ探しやすい。 |
| 性行為・性的刺激 | `RUBBING_GRINDING` / 擦り・挟み・こすり | 1/0 | 937; source IDs 32, 60, 85 | **ADOPT** | frottage / thigh sex / crotch rub 等の摩擦系がsourceで反復し、手足刺激とは別の自然な意図。 |
| 性行為・性的刺激 | `LOCAL_STIMULATION` / 局所刺激 | 4/1 | 727, 1241, 165(sec) | **ADOPT** | 局所刺激が主副で反復し、挿入トポロジーとは別に探す価値がある。 |
| 性行為・性的刺激 | `ORGASM_RESPONSE` / 絶頂・反応 | 2/0 | 729, 734 | **ADOPT** | 絶頂・反応を細かく分けず一棚に統合する現在案を維持。 |
| 性行為・性的刺激 | `BEFORE_AFTER_ACT` / 直前・事後 | 1/0 | 1236; source IDs 8–10, 84, 100, 146 | **ADOPT** | 直前・事後は複数行為に横断してsource反復があり、時間軸入口として有用。 |
| 性行為・性的刺激 | `IMPLIED_GESTURE` / 示唆・仕草 | 1/1 | 745, 1236(sec); source IDs 41, 42, 87, 105 | **ADOPT** | 示唆・仕草は複数行為で反復し、実行済み行為とは別に探す意図がある。 |
| 性行為・性的刺激 | `COOPERATIVE_MULTI_ACT` / 協力・複数行為 | 1/3 | 256, 808(sec), 1234(sec) | **ADOPT** | 主1でも副経路が3回反復し、複数・協力行為の横断入口として機能。 |
| 接触・挿入・部位行為 | `GENERAL_INSERTION` / 挿入全般 | 0/3 | 492(sec), 332(sec), 491(sec); source IDs 170–195 | **ADOPT** | 主経路0でも副経路反復とsourceの大きな挿入群があり、親直下の基礎棚として必要。 |
| 接触・挿入・部位行為 | `ANAL_SITE` / 肛門・直腸 | 1/1 | 165, 168(sec); source IDs 146–149 | **ADOPT** | 肛門・直腸は反復する明確な部位検索意図。 |
| 接触・挿入・部位行為 | `FEMALE_GENITAL_SITE` / 女性器 | 1/3 | 848, 546(sec), 541(sec) | **ADOPT** | 主副合わせ4回で、部位行為の入口として十分な反復。 |
| 接触・挿入・部位行為 | `ORAL_SITE` / 口・口内 | 0/0 | none | **DROP** | Pilot需要なし。口淫とのUI重複も強いため、named actは口淫、その他の口部位トポロジーは親へ置く。 |
| 接触・挿入・部位行為 | `URETHRAL_SITE` / 尿道 | 0/0 | source IDs 207–223 | **ADOPT** | Pilot外だがsourceに17件規模の連続した尿道群があり、希少1概念ではなく独立棚の価値がある。 |
| 接触・挿入・部位行為 | `NIPPLE_SITE` / 乳首 | 0/0 | source ID 196 | **DROP** | 専用棚を作るほど反復せず、部位別ボタン乱立を避けて親へ置く。 |
| 接触・挿入・部位行為 | `OTHER_BODY_SITE` / その他部位 | 1/0 | 1517 | **DROP** | Issue #59 FIX-2。残余定義の `その他部位` は禁止し、1517は親ジャンル直下へ戻す。 |
| 接触・挿入・部位行為 | `EXTERNAL_CONTACT` / 外部接触 | 2/1 | 2382, 2383, 747(sec) | **ADOPT** | 非挿入の外部接触が主副で反復し、挿入群との区別にUI価値がある。 |
| 接触・挿入・部位行為 | `MULTIPLE_DEEP_INSERTION` / 深部・多重挿入 | 1/0 | 1483; source IDs 172–206 | **ADOPT** | deep/double/triple/multiple/large 系がsourceで反復し、一つの広い棚に統合する価値がある。 |
| 拘束・BDSM・支配 | `BONDAGE_STATE` / 拘束状態 | 2/0 | 1924, 2504 | **ADOPT** | 拘束そのものを探す基礎棚として反復。 |
| 拘束・BDSM・支配 | `BONDAGE_POSITION` / 緊縛姿勢 | 0/0 | source IDs 1912, 1914, 1915, 1926, 1932, 1937 | **ADOPT** | box tie/frogtie/hogtie/reverse prayer等の反復群があり、単なる生成Poseではなく緊縛名として探す自然な棚。 |
| 拘束・BDSM・支配 | `RESTRAINT_DEVICE` / 拘束具 | 1/0 | 634; source IDs 1822, 1828, 1838–1840, 1935 | **ADOPT** | cuffs/handcuffs/shackles/spreader bar/stocks等の反復群があり、道具の用途が拘束で一貫。 |
| 拘束・BDSM・支配 | `GAG_MOUTH_RESTRAINT` / 口枷 | 2/0 | 2511, 2507; source IDs 1814, 1815, 1820, 1825–1841 | **ADOPT** | 口枷の反復群が大きく、日本語で独立して探す価値が高い。 |
| 拘束・BDSM・支配 | `CHASTITY_CONTROL` / 貞操管理 | 1/0 | 1845; source IDs 633, 1818, 1819 | **ADOPT** | cage/belt/braの反復があり、アクセス制限という一貫した用途。 |
| 拘束・BDSM・支配 | `PAIN_TORTURE` / 苦痛・拷問 | 3/0 | 625, 630, 1077 | **ADOPT** | Pilotで反復し、損傷そのものとは別のBDSM意図でまとまる。 |
| 拘束・BDSM・支配 | `DOMINATION_SUBMISSION` / 支配・服従 | 0/0 | source IDs 1913, 1933, 2181, 2182 | **ADOPT** | dominator/slave/dominatrix/femdom 等が反復し、関係性として自然な閲覧棚。 |
| 拘束・BDSM・支配 | `FORCE_NONCONSENT` / 強制・非合意 | 1/0 | 1398; source IDs 426–451 | **ADOPT** | sourceに大きな反復群があり、UI分類はPrompt適格性とは別レイヤーとして保持。 |
| 拘束・BDSM・支配 | `MENTAL_CONTROL_IMPAIRMENT` / 精神支配・意識低下 | 0/0 | source IDs 434, 1805, 1807 | **DROP** | 精神操作と意識低下を一棚に束ねる根拠が弱く、Pilot需要も0。親ジャンルへ置き、全件分布後に必要なら再提案。 |

### Remediation delta

Visible subgenres change from **45 candidates to 38**.

Removed or merged:
- `BODY_FORM_STATE` -> DROP to `身体・解剖` parent
- `ABSENCE_VARIANT` -> MERGE into natural body-part shelf
- `REVEALING_OUTFIT` -> DROP to `裸体・衣服・露出` parent
- `ORAL_SITE` -> DROP to `接触・挿入・部位行為` parent; named oral acts remain under `口淫`
- `NIPPLE_SITE` -> DROP to `接触・挿入・部位行為` parent
- `OTHER_BODY_SITE` -> DROP; visible “その他部位” is eliminated
- `MENTAL_CONTROL_IMPAIRMENT` -> DROP to `拘束・BDSM・支配` parent pending full-distribution evidence

Formal 150-row map changes:
- ID 2381: `BODY_FORM_STATE` -> `BODY_ANATOMY` parent
- ID 739: `ABSENCE_VARIANT` -> `BREAST_NIPPLE`
- ID 742: `ABSENCE_VARIANT` -> `FEMALE_GENITAL`
- ID 2526: `REVEALING_OUTFIT` -> `NUDITY_CLOTHING_EXPOSURE` parent
- ID 1517: `OTHER_BODY_SITE` -> `CONTACT_INSERTION_BODY_SITE` parent

No Special ID, canonical English identity, Alias relationship, Layer/source provenance, #32/#43 validation/freeze state, or production-promoted Special data is changed.

## 8. Alias result

Default remains:

```text
resolved canonical + no presentation conflict -> AUTO_INHERITED_ALIAS
otherwise -> REVIEW_REQUIRED
```

The formal 15 Alias/canonical control pairs remain compatible with inheritance. Issue #59 remediation changes only browsing-path sidecar structure; it does not rewrite canonical Alias relationships.

## 9. Japanese-first UI contract

Fixed contract:
- internal genre/subgenre IDs: stable English/ASCII;
- every visible genre/subgenre: mandatory Japanese label;
- normal genre/subgenre UI: Japanese only;
- Special result row: Japanese + English tag;
- long classification reasoning: audit/detail only.

The taxonomy file remains:
- `docs/issue56/pilot/issue56_ui_genre_taxonomy_candidate_v1_2.json`

The reviewed Pilot map remains:
- `docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv`

## 10. Generation Profile / eligibility separation

UI taxonomy remains a browsing sidecar only.

It does not take authority from `docs/GENERATION_PROFILE_SCHEMA.md`, which remains responsible for generation-structure fields such as GenerationFamily, GenerationRole, actor/bodypart/implement/pose/camera/spatial requirements.

Reference-only age-restricted identities remain dictionary-classifiable without becoming Prompt-eligible. UI placement cannot override existing eligibility/safety state.

## 11. Issue #59 remediation Gate state

Current decision:

**`ISSUE59_REQUIRED_FIXES_APPLIED / REAUDIT_REQUIRED`**

Do **not** expand to all 2,788 from this document alone.

Required next sequence:
1. run selector/taxonomy/map consistency tests on the remediated branch;
2. return the compacted taxonomy delta to Issue #59 for re-audit;
3. only after an acceptable re-audit verdict, freeze the Pilot-approved taxonomy;
4. classify old `その他・文脈`;
5. cross-audit old categories 01–12;
6. produce the full 2,788 UI mapping and final distribution/unresolved-pool audit;
7. only after #56 completion may routing proceed toward #42 under the current project Gate rules.

Stage10 production A/B remains **NOT STARTED**.
