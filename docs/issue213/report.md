# Issue #213 — Practical ordinary-tag retrieval audit

## Executive result

207件（sexual 121 / general 86）をproduction runtime catalogと現行検索・UnifiedBrowse経路で評価した。最も効いた問題はtaxonomyの広さより、日本語の自然なintent表現を既存label/synonymへ結び付ける検索語彙の不足だった。
自然な日本語queryではsexual targetの検索-only発見率は1.7%、Search + Browse併用も1.7%。Browse/facetだけなら73.6%が何らかの順位で見つかるが、Top20は50.4%。一方、各canonicalの日本語表示labelをそのままqueryにする診断では121/121が検索できた。まず試すべきは少数の高頻度intent synonymとscenario regressionで、global taxonomy/ranking変更ではない。

Top20は結果上位のnon-target件数が多いscenarioを含む。Search-only/Browse-only/Search+Browseは独立評価。Overall GOOD/DISCOVERABLE等はtargetが見つかる最小cost経路を分類し、Search + Browse併用の状態を示す`combinedStatus`ではない。

## Whole-set summary

| set | total | sexual | general | GOOD | DISCOVERABLE | BURIED | NOISY | MISLEADING | DEAD_END | median cost | Top5 | Top10 | Top20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 全体 | 207 | 121 | 86 | 34 | 19 | 52 | 51 | 20 | 31 | 3 | 29.0% | 37.7% | 50.2% |
| 性的 | 121 | 121 | 0 | 27 | 19 | 28 | 15 | 20 | 12 | 4 | 29.8% | 38.0% | 50.4% |
| 一般 | 86 | 0 | 86 | 7 | 0 | 24 | 36 | 0 | 19 | 1 | 27.9% | 37.2% | 50.0% |

`GOOD/DISCOVERABLE/BURIED/NOISY/MISLEADING/DEAD_END`は最小cost経路とfilter除去probeで分類した。C経路が空でもB経路で見つかれば全体をDEAD_ENDにはしていない。MISLEADINGは選択route/facetでtargetが消え、route-only/body-only/ContentIntent解除では現れる場合に付ける（20件）。

## A/B/C route comparison

| set | path | target found | Top5 | Top10 | Top20 |
| --- | --- | --- | --- | --- | --- |
| 全体 | A 日本語検索のみ | 4.8% | 4.8% | 4.8% | 4.8% |
| 全体 | B Browse/facetのみ | 74.4% | 25.6% | 34.3% | 47.8% |
| 全体 | C 検索 + Browse/facet | 3.9% | 3.9% | 3.9% | 3.9% |
| 性的 | A 日本語検索のみ | 1.7% | 1.7% | 1.7% | 1.7% |
| 性的 | B Browse/facetのみ | 73.6% | 29.8% | 38.0% | 50.4% |
| 性的 | C 検索 + Browse/facet | 1.7% | 1.7% | 1.7% | 1.7% |
| 一般 | A 日本語検索のみ | 9.3% | 9.3% | 9.3% | 9.3% |
| 一般 | B Browse/facetのみ | 75.6% | 19.8% | 29.1% | 44.2% |
| 一般 | C 検索 + Browse/facet | 7.0% | 7.0% | 7.0% | 7.0% |

Search-only queryはscenarioの日本語自然語だけを入力した。Browse-onlyはscenario記載のroute/local/facet/content/deep stateを適用した使用数sort順。Search + Browseは日本語query hitを同じstateで絞った。

## Sexual set by family

複合intentは121件中84件。ここではrouteとBodySiteまたはThemeの併用を複合条件として数えた。

| family | n | GOOD | DISCOVERABLE | BURIED | NOISY | MISLEADING | DEAD_END | Top5 | Top10 | Top20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| action | 11 | 0 | 1 | 5 | 3 | 2 | 0 | 27.3% | 27.3% | 36.4% |
| anal | 9 | 4 | 1 | 2 | 0 | 2 | 0 | 44.4% | 44.4% | 55.6% |
| bdsm | 9 | 2 | 0 | 3 | 3 | 0 | 1 | 44.4% | 44.4% | 55.6% |
| breast | 13 | 3 | 0 | 5 | 4 | 1 | 0 | 38.5% | 53.8% | 53.8% |
| composition | 12 | 6 | 0 | 0 | 0 | 5 | 1 | 50.0% | 50.0% | 50.0% |
| female_genital | 9 | 2 | 2 | 2 | 0 | 3 | 0 | 22.2% | 33.3% | 44.4% |
| fluid | 9 | 4 | 0 | 0 | 4 | 1 | 0 | 55.6% | 66.7% | 88.9% |
| male_genital | 8 | 1 | 2 | 1 | 1 | 1 | 2 | 25.0% | 37.5% | 50.0% |
| multi_person | 9 | 0 | 0 | 3 | 0 | 0 | 6 | 0.0% | 0.0% | 0.0% |
| nonhuman | 6 | 1 | 2 | 3 | 0 | 0 | 0 | 16.7% | 16.7% | 50.0% |
| oral | 10 | 1 | 6 | 1 | 0 | 2 | 0 | 10.0% | 40.0% | 70.0% |
| pose | 10 | 0 | 5 | 3 | 0 | 1 | 1 | 0.0% | 20.0% | 50.0% |
| pregnancy_lactation | 6 | 3 | 0 | 0 | 0 | 2 | 1 | 50.0% | 50.0% | 50.0% |

Multi-person/actor-targetとPOV/compositionは特に弱い。multi-personは9件中3件だけ結果集合にtargetがあり、Top20到達0%。Compositionは6/12がdead endで、body focusと画角/一人称視点の関係をintent語彙とbrowse routeの両方で再点検する価値がある。

### General / Special sample comparison

| scenario set | catalog category | n | found | Top5 | Top10 | Top20 |
| --- | --- | --- | --- | --- | --- | --- |
| 性的 | Special | 117 | 75.2% | 30.8% | 39.3% | 52.1% |
| 性的 | General | 4 | 25.0% | 0.0% | 0.0% | 0.0% |
| 一般 | General | 86 | 77.9% | 27.9% | 37.2% | 50.0% |

sexual scenarioはSpecial 117件、General 4件であり、General側のsexual用途比較は小標本。全体のSpecial 117 / General 90でもscenario選定標本なのでpopulation quality estimateではない。

## Focused facet and interaction probes

| production state | result count | BodySite | Theme | sample top tags |
| --- | --- | --- | --- | --- |
| sexual-neutral | 2964 |  |  | breasts, cleavage, nipples, underwear, panties |
| sexual-deep-only | 1726 |  |  | open_clothes, penis, pussy, sex, spread_legs |
| sexual-body-breast | 270 | BREAST_NIPPLE |  | covered_nipples, sideboob, underboob, cleavage_cutout, grabbing_another's_breast |
| sexual-action-and-breast | 137 | BREAST_NIPPLE |  | grabbing_another's_breast, breast_press, paizuri, cum_on_breasts, nipple_stimulation |
| sexual-body-mouth | 118 | MOUTH_ORAL |  | oral, fellatio, cum_in_mouth, gag, gagged |
| sexual-action-and-mouth | 89 | MOUTH_ORAL |  | oral, fellatio, cum_in_mouth, licking_penis, breast_sucking |
| sexual-theme-bdsm | 273 |  | BDSM_RESTRAINT | bound, bondage, restrained, rape, cuffs |
| sexual-theme-reproduction | 28 |  | REPRO_PREGNANCY_LACTATION | lactation, impregnation, projectile_lactation, breastfeeding, lactation_through_clothes |
| sexual-theme-AND-bdsm-reproduction | 0 |  | BDSM_RESTRAINT, REPRO_PREGNANCY_LACTATION |  |
| sexual-breast-and-theme-AND | 0 | BREAST_NIPPLE | BDSM_RESTRAINT, REPRO_PREGNANCY_LACTATION |  |
| general-purpose-breast | 223 | BREAST_NIPPLE |  | large_breasts, medium_breasts, flat_chest, covered_nipples, sideboob |
| all-breast | 322 | BREAST_NIPPLE |  | large_breasts, medium_breasts, flat_chest, covered_nipples, sideboob |

- Browse indexの複数ThemeはANDで照合する。BDSM_RESTRAINT 273件、REPRO_PREGNANCY_LACTATION 28件に対し、両Theme ANDは0件。BREAST_NIPPLE + 両Themeも0件。複数themeを同一tagへ要求すると空集合になる。
- `DictionaryWorkspaceViewModel.ToggleTheme`は二つ目を加えた時AND件数が0なら、先のThemeを保持せず後から選んだThemeだけに切り替える。0件を防ぐが、AND選択を静かに置換する。評価JSONの`ThemeAndViewModel`に実行結果がある。
- BodySite BREAST_NIPPLEはAll 322件、Sexual 270件、GeneralPurpose 223件。`ACTION_CONTACT + BREAST_NIPPLE`はSexual 137件。body filterは候補を狭めるが、行為別探索にはaction routeとの併用が必要。
- Sexual neutral browseは2,964件、DeepOnlyで1,726件。DeepOnlyはSpecial deep discoveryを絞るが、targetを上位へ上げるrankerではない。
- local refinementを明示した8件では、school_uniformはCLOTHING/UNIFORMで1位。一方CLOTHING/EVERYDAYではblazer 125位、hoodie 73位、sweater 49位、apron 48位。localが意味を絞っても使用数sortの埋もれは残る。

### DeepOnly target effect

| DeepOnly scenarios | Top5 | Top10 | Top20 | found with DeepOnly | found when off | off Top20 |
| --- | --- | --- | --- | --- | --- | --- |
| 83 | 16.9% | 22.9% | 39.8% | 71.1% | 72.3% | 38.6% |

DeepOnlyはroute/facetで発見対象がSpecial deep identitiesになる場合に絞り込み用として使える。off側のfoundが多いcaseは、一般タグとしてのtargetや未分類tagをDeepOnlyで隠すtrade-offを示す。DeepOnly自体は順位改善ではない。

## Cause ranking — overall Top 20

| # | scenario IDs | affected target examples | observed behavior / root cause | family | frequency | safest next category |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | S047, S048, S049, S052, S053, S054, S055, S117, S118, S119 | sex, masturbation, frottage, foreplay, groping, guided_breast_grab, sex_toy, mutual_handjob, mutual_penetration, guided_handjob | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | action | 10 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 2 | S001, S002, S003, S004, S005, S006, S010, S011, S109, S110 | breast_sucking, paizuri, cooperative_paizuri, breast_sucking_through_clothes, breast_on_breast, nipple_stimulation, nipple_tweak, grabbing_another's_breast, sucking_own_breasts, nipple_tweak_through_clothes | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | breast | 10 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 3 | G019, G020, G021, G022, G023, G024, G025, G026, G027, G028 | school_uniform, sailor_senshi_uniform, blazer, hoodie, sweater, jacket, apron, kimono, police_uniform, necktie | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | clothing | 10 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 4 | G037, G038, G039, G040, G041, G042, G043, G044, G045, G046 | standing, sitting, kneeling, lying, walking, running, jumping, arms_up, hand_on_own_hip, looking_back | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | pose | 10 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 5 | S051, S087, S088, S089, S090, S091, S092, S093, S094 | group_masturbation, threesome, group_sex, ffm_threesome, mmf_threesome, gangbang, mutual_masturbation, multiple_penis_fellatio, male_spitroast | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | multi_person | 9 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 6 | G047, G048, G049, G050, G051, G052, G053, G054, G055 | holding_book, holding_sword, holding_umbrella, holding_flower, holding_phone, holding_cup, holding_bag, holding_weapon, holding_food | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | object | 9 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 7 | G048, G049, G050, G051, G052, G053, G054, G055 | holding_sword, holding_umbrella, holding_flower, holding_phone, holding_cup, holding_bag, holding_weapon, holding_food | route。選んだrouteの候補集合からtargetが外れる | object | 8 scenario | route ownerへ候補漏れを1件ずつ提示 |
| 8 | G073, G074, G075, G076, G077, G078, G079, G080 | close-up, upper_body, full_body, wide_shot, from_above, from_below, profile, silhouette | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | composition | 8 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 9 | G010, G012, G013, G014, G015, G016, G017, G018 | blush, frown, closed_eyes, looking_at_viewer, looking_to_the_side, open_mouth, tears, sweat | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | expression | 8 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 10 | G001, G002, G004, G005, G006, G007, G008, G009 | long_hair, short_hair, twintails, braid, messy_hair, hair_ornament, hair_ribbon, glasses | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | hair | 8 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 11 | G020, G021, G022, G023, G025, G026, G027, G028 | sailor_senshi_uniform, blazer, hoodie, sweater, apron, kimono, police_uniform, necktie | 使用数順。Browse結果にあるtargetが既定の使用数順で埋もれる | clothing | 8 scenario | 順位比較を固定fixtureで検証。global usage順変更は保留 |
| 12 | S064, S065, S067, S069, S070, S071, S072 | bondage, bound_wrists, shibari_over_clothes, predicament_bondage, self_bondage, spreader_bar, blindfold | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | bdsm | 7 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 13 | G029, G030, G032, G033, G034, G035, G036 | striped_clothes, polka_dot, floral_print, camouflage, gradient_background, monochrome, polka_dot_background | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | color_pattern | 7 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 14 | G065, G066, G068, G069, G070, G071, G072 | night, sunset, snowing, backlighting, spotlight, shadow, sunbeam | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | light | 7 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 15 | S087, S088, S089, S090, S091, S094 | threesome, group_sex, ffm_threesome, mmf_threesome, gangbang, male_spitroast | route。選んだrouteの候補集合からtargetが外れる | multi_person | 6 scenario | route ownerへ候補漏れを1件ずつ提示 |
| 16 | S046, S101, S103, S104, S106, S108 | penis_on_face, pov_crotch, pov, crotch_focus, close-up, imminent_penetration | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | composition | 6 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 17 | G057, G058, G061, G062, G063, G064 | outdoors, indoors, kitchen, street, forest, beach | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | scene | 6 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 18 | S032, S034, S036, S112, S114 | fingering, spread_pussy, labia_clamps, double_vaginal, clitoris_tweak | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | female_genital | 5 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 19 | S038, S082, S083, S084, S085 | pussy_juice, ejaculation, facial, bukkake, cum_string | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | fluid | 5 scenario | 日本語search synonym候補。test-only評価を先に追加 |
| 20 | G082, G083, G084, G085, G086 | dog, bird, butterfly, flower, tree | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | living | 5 scenario | 日本語search synonym候補。test-only評価を先に追加 |

Root-cause頻度はscenario×cause出現数で、相互排他的な件数ではない。全scenarioの197件にSEARCH_SYNONYMが付いた。failure familyの頻度と具体IDはscenario-results.csv / evaluation.jsonを正本にする。

## Sexual-only highest-impact issues

| # | scenario IDs | target examples | n | current behavior / cause | safest next category |
| --- | --- | --- | --- | --- | --- |
| 1 | S047, S048, S049, S052, S053, S054, S055, S117, S118, S119 | sex, masturbation, frottage, foreplay, groping, guided_breast_grab, sex_toy, mutual_handjob, mutual_penetration, guided_handjob | 10 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 2 | S001, S002, S003, S004, S005, S006, S010, S011, S109, S110 | breast_sucking, paizuri, cooperative_paizuri, breast_sucking_through_clothes, breast_on_breast, nipple_stimulation, nipple_tweak, grabbing_another's_breast, sucking_own_breasts, nipple_tweak_through_clothes | 10 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 3 | S051, S087, S088, S089, S090, S091, S092, S093, S094 | group_masturbation, threesome, group_sex, ffm_threesome, mmf_threesome, gangbang, mutual_masturbation, multiple_penis_fellatio, male_spitroast | 9 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 4 | S064, S065, S067, S069, S070, S071, S072 | bondage, bound_wrists, shibari_over_clothes, predicament_bondage, self_bondage, spreader_bar, blindfold | 7 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 5 | S087, S088, S089, S090, S091, S094 | threesome, group_sex, ffm_threesome, mmf_threesome, gangbang, male_spitroast | 6 | route。選んだrouteの候補集合からtargetが外れる | route ownerへ候補漏れを1件ずつ提示 |
| 6 | S046, S101, S103, S104, S106, S108 | penis_on_face, pov_crotch, pov, crotch_focus, close-up, imminent_penetration | 6 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 7 | S032, S034, S036, S112, S114 | fingering, spread_pussy, labia_clamps, double_vaginal, clitoris_tweak | 5 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 8 | S038, S082, S083, S084, S085 | pussy_juice, ejaculation, facial, bukkake, cum_string | 5 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 9 | S039, S041, S042, S044, S115 | handjob, testicle_sucking, prostate_milking, sounding, testicle_grab | 5 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |
| 10 | S059, S061, S062, S120, S121 | amazon_position, suspended_congress, mating_press, standing_doggystyle, reverse_squatting_cowgirl_position | 5 | 検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる | 日本語search synonym候補。test-only評価を先に追加 |

Top10の次点群にはanal/buttock、female genital、fluid、male genital、oral、pose、nonhumanが続く。multi-personは発見率33.3%、compositionは50.0%。

## Safe improvement candidates (no implementation in this audit)

| # | category | candidate | cause | risk |
| --- | --- | --- | --- | --- |
| 1 | Search synonym | 日常語・口語のintent→日本語検索語を少数のaccepted aliasとして追加する候補を作り、scenario回帰を先に置く | SEARCH_SYNONYM | 低 |
| 2 | Search ranking | exact label / approved synonym / phrase-intentの順位差だけを固定scenarioで比較する | SEARCH_RANKING | 低 |
| 3 | Route | 人物数・関係・行為・道具など、routeから外れた高価値例をowner別に整理してレビューする | ROUTE | 低 |
| 4 | Local refinement | localを選ぶ前後の結果件数と選択保持を検証する | LOCAL_REFINEMENT | 低 |
| 5 | Body facet | 高確度のactor/action/body-site例に限ってfacet membership候補をレビューする | BODY_FACET | 中 |
| 6 | Theme facet | BDSM / reproductionなどのtheme membershipを文脈別にレビューし、AND件数を併記する | THEME_FACET | 中 |
| 7 | ContentIntent | NonSexual/Contextual/Sexualの境界caseを個別に再点検する。default filterは変えない | CONTENT_INTENT | 中 |
| 8 | Usage order | usage順でTop20外となる実用tagを限定して報告する。global ranking改定は別検証にする | USAGE_SORT | 中 |
| 9 | Interaction | multi-theme追加時のAND countと現在のfacet自動置換をUI文言で明示する案を検討する | INTERACTION | 低 |
| 10 | Test only | この200件超のintent-first corpusをsearch/browse regression gateとして継続可能にする | NO_CHANGE | 低 |

## Changes to avoid

- この小さな固定scenario集合からGeneral/Special全体のtaxonomyを組み替えない。
- 使用数sortを全体で下げない。低頻度tagを上げる場合はexact/strong-intentに限った根拠と回帰testを求める。
- 複数themeのANDが0件だったことだけを理由にAND semanticsをORへ変えない。別tag同士の複合意図はtag選択workflowとして別に評価する。
- Sexual ContentIntentの既定値変更や、自動DeepOnlyはしない。妊娠などContextual/NonSexual境界を優先レビューする。
- タグのcanonical identity、Prompt出力、production catalogの意味情報をUX都合だけで変更しない。

## Measurement contract and limits

- Cost: query entry 1; primary route 1; local refinement 1; each BodySite/Theme facet 1; changing ContentIntent 1; enabling DeepOnly 1. For an empty query Browse path has no query cost. Classification knowledge steps count the selected route/local/facets/content/deep controls; it is a lower-bound proxy and does not model user hesitation or reading time.
- Rank: A and C use current search output order. B uses UnifiedBrowseIndex.Browse ordered with the exact DictionaryWorkspaceViewModel default `OrderByDescending(Usage)` behavior. The report separately records mode result counts/ranks and best-cost path.
- GOOD: best path Top5, cost <= 5, and not noisy; DISCOVERABLE: target Top20; BURIED: target exists but rank >20; NOISY: Top20 includes >=15 non-acceptable rows and result set >100; MISLEADING: chosen route/facet/content/deep filters hide a target present after removing one of those filters; DEAD_END: no target in A/B/C or the matched broader filter probes.
- Noise is a conservative count of rows outside the acceptable target set, not human semantic annotation. Related tags may still be useful; NOISY is therefore a provisional upper-bound label. `ConfusingSimilarTags` records visible examples for review.
- Search-only 10/207; Browse-only 154/207; combined 8/207; exact Japanese label diagnostic 207/207. Tag label availability did not imply that a user phrase matched it.
- The scenario set is curated, intent-first, and fixed; it is not a random population sample. Expected tags are verified against the production catalog. Single-target ground truths dominate, so semantic equivalence for ambiguous prompts remains a review limit.
- No images were generated. Native desktop automation was not used. 17 representative flows compared actual DictionaryWorkspaceViewModel results against the corresponding catalog/search/index results; all 17 matched. This is logic-level integration, not visual WPF control validation.
- Source authority: origin/main `a90f5b652d4239709005d020417a236ea9d97ebb`. Runtime manifest provenance matches that SHA. Production catalog SHA-256 `5759156FF79D794DDC70DD5459AF9B80F8CB204C4527BE16FD368FF40BE9F141`.

## Reproduction

Set `DTT_ISSUE213_CATALOG` to the read-only runtime catalog, then run `python scripts/issue213/build_scenario_corpus.py`; it verifies every canonical target exists. Run the focused test with `DTT_ISSUE213_CATALOG`, `DTT_ISSUE213_SCENARIOS`, and `DTT_ISSUE213_REPORT` set to the catalog, scenario JSON, and output JSON paths. `python scripts/issue213/render_report.py` writes this report and the flat CSV.

Scenario source: `scenarios.json`. Full per-scenario output: `evaluation.json`. Flat ledger: `scenario-results.csv`.
