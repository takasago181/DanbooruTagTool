"""Render the Issue #213 machine evaluation into reviewable CSV and Markdown."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "issue213"
DATA = json.loads((BASE / "evaluation.json").read_text(encoding="utf-8"))
ROWS = DATA["Scenarios"]
RESULTS = BASE / "scenario-results.csv"
REPORT = BASE / "report.md"

FAILURE_STATUSES = {"BURIED", "NOISY", "MISLEADING", "DEAD_END"}
CAUSE_LABELS = {
    "SEARCH_SYNONYM": "検索語彙。自然な日本語queryでtargetが見つからず、表示名queryなら見つかる",
    "SEARCH_RANKING": "検索順位。targetは検索hitに含まれるが上位へ届かない",
    "USAGE_SORT": "使用数順。Browse結果にあるtargetが既定の使用数順で埋もれる",
    "ROUTE": "route。選んだrouteの候補集合からtargetが外れる",
    "LOCAL_REFINEMENT": "local refinement。選んだ下位分類からtargetが外れる",
    "BODY_FACET": "BodySite facet。身体部位条件とtargetのmembershipが合わない",
    "THEME_FACET": "Theme facet。theme条件とtargetのmembershipが合わない",
    "CONTENT_INTENT": "ContentIntent。Sexual filterがtargetを除外する",
    "LABEL_DESCRIPTION": "日本語label/descriptionが不足または検索候補に使われない",
    "INTERACTION": "操作の組合せでtargetが検索結果から落ちる",
    "UI_ONLY": "browse UI対象外だがsearch可能なidentity",
    "NO_CHANGE": "このscenarioでは明確な改善原因を検出しない",
}
SAFE_FIX = {
    "SEARCH_SYNONYM": "日本語search synonym候補。test-only評価を先に追加",
    "SEARCH_RANKING": "exact/strong intent専用の順位回帰試験",
    "USAGE_SORT": "順位比較を固定fixtureで検証。global usage順変更は保留",
    "ROUTE": "route ownerへ候補漏れを1件ずつ提示",
    "LOCAL_REFINEMENT": "local候補集合の境界test",
    "BODY_FACET": "accepted BODY membershipの小さな補完案を別レビュー",
    "THEME_FACET": "accepted THEME membershipの小さな補完案を別レビュー",
    "CONTENT_INTENT": "Contextual境界例のreview。filter既定値は変えない",
    "LABEL_DESCRIPTION": "日本語表示/説明の改善候補として記録",
    "INTERACTION": "facet countと条件解除/自動置換を可視化するtest",
    "UI_ONLY": "search/browseの能力表示と案内を確認",
    "NO_CHANGE": "変更不要",
}

def pct(value: int, total: int) -> str:
    return f"{100 * value / total:.1f}%" if total else "—"

def rate(rows: list[dict], field: str) -> str:
    return pct(sum(bool(row[field]) for row in rows), len(rows))

def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")

def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(esc(value) for value in row) + " |" for row in rows)
    return "\n".join(out)

with RESULTS.open("w", newline="", encoding="utf-8-sig") as output:
    writer = csv.DictWriter(output, fieldnames=list(ROWS[0]), extrasaction="ignore")
    writer.writeheader()
    for row in ROWS:
        writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})

sets = [("全体", ROWS), ("性的", [row for row in ROWS if row["Sexual"]]), ("一般", [row for row in ROWS if not row["Sexual"]])]
status_names = ["GOOD", "DISCOVERABLE", "BURIED", "NOISY", "MISLEADING", "DEAD_END"]
misleading_total = DATA["Overall"]["Statuses"]["MISLEADING"]
overall_rows = []
mode_rows = []
for name, subset in sets:
    statuses = Counter(row["Status"] for row in subset)
    summary = DATA["Overall"] if name == "全体" else DATA["Sexual"] if name == "性的" else DATA["General"]
    overall_rows.append([
        name, len(subset), len([row for row in subset if row["Sexual"]]), len([row for row in subset if not row["Sexual"]]),
        *[statuses.get(status, 0) for status in status_names], summary["MedianInteractionCost"],
        f"{summary['Top5Rate']:.1f}%", f"{summary['Top10Rate']:.1f}%", f"{summary['Top20Rate']:.1f}%",
    ])
    for mode, found, top5, top10, top20 in [
        ("A 日本語検索のみ", "SearchOnlyBestRank", "SearchOnlyTop5", "SearchOnlyTop10", "SearchOnlyTop20"),
        ("B Browse/facetのみ", "BrowseOnlyBestRank", "BrowseOnlyTop5", "BrowseOnlyTop10", "BrowseOnlyTop20"),
        ("C 検索 + Browse/facet", "CombinedBestRank", "CombinedTop5", "CombinedTop10", "CombinedTop20"),
    ]:
        mode_rows.append([name, mode, pct(sum(row[found] is not None for row in subset), len(subset)),
                          pct(sum(row[top5] for row in subset), len(subset)),
                          pct(sum(row[top10] for row in subset), len(subset)),
                          pct(sum(row[top20] for row in subset), len(subset))])

# Rebuild family rows directly from scenario-level records.
family_groups: dict[str, list[dict]] = defaultdict(list)
for row in ROWS:
    if row["Sexual"]:
        family_groups[row["ScenarioClass"]].append(row)
family_rows = []
for family, subset in sorted(family_groups.items()):
    counts = Counter(row["Status"] for row in subset)
    family_rows.append([family, len(subset), *[counts.get(status, 0) for status in status_names],
                        rate(subset, "Top5"), rate(subset, "Top10"), rate(subset, "Top20")])

category_rows = []
for sexual_name, subset in [("性的", [x for x in ROWS if x["Sexual"]]), ("一般", [x for x in ROWS if not x["Sexual"]])]:
    for category in ("Special", "General"):
        group = [x for x in subset if x["TargetCatalogCategory"] == category]
        if group:
            category_rows.append([sexual_name, category, len(group), rate(group, "TargetFound"), rate(group, "Top5"), rate(group, "Top10"), rate(group, "Top20")])

issue_groups: dict[tuple[str, str, bool], list[dict]] = defaultdict(list)
for row in ROWS:
    if row["Status"] not in FAILURE_STATUSES:
        continue
    for cause in row["RootCauses"]:
        issue_groups[(cause, row["ScenarioClass"], row["Sexual"])].append(row)
all_cause_counts = Counter(cause for row in ROWS for cause in row["RootCauses"])
issues = sorted(issue_groups.items(), key=lambda pair: (-len(pair[1]), pair[0][0], pair[0][1]))[:20]
top20_rows = []
for (cause, family, is_sexual), subset in issues:
    ids = ", ".join(row["Id"] for row in subset)
    targets = ", ".join(dict.fromkeys(target for row in subset for target in row["Expected"]))
    top20_rows.append([f"{len(top20_rows)+1}", f"{ids}", targets, CAUSE_LABELS.get(cause, cause), family,
                       f"{len(subset)} scenario", SAFE_FIX.get(cause, "test-only確認")])

sexual_issue_groups = {key: group for key, group in issue_groups.items() if key[2]}
sexual_issues = sorted(sexual_issue_groups.items(), key=lambda pair: (-len(pair[1]), pair[0][0], pair[0][1]))[:10]
sexual_top_rows = []
for (cause, family, _), subset in sexual_issues:
    sexual_top_rows.append([len(sexual_top_rows)+1, ", ".join(row["Id"] for row in subset),
                            ", ".join(dict.fromkeys(target for row in subset for target in row["Expected"])),
                            f"{len(subset)}", CAUSE_LABELS.get(cause, cause), SAFE_FIX.get(cause, "test-only確認")])

probe_rows = [[probe["Name"], probe["ResultCount"], ", ".join(probe["BodySiteIds"]), ", ".join(probe["ThemeIds"]),
               ", ".join(probe["Top10"][i]["Canonical"] for i in range(min(5, len(probe["Top10"]))))] for probe in DATA["ConstraintProbes"]]
deep_rows = [row for row in ROWS if row["DeepOnly"]]
deep_summary = [[
    len(deep_rows), rate(deep_rows, "BrowseOnlyTop5"), rate(deep_rows, "BrowseOnlyTop10"), rate(deep_rows, "BrowseOnlyTop20"),
    pct(sum(row["BrowseOnlyBestRank"] is not None for row in deep_rows), len(deep_rows)),
    pct(sum(row["DeepOnlyOffBestRank"] is not None for row in deep_rows), len(deep_rows)),
    pct(sum(row["DeepOnlyOffBestRank"] is not None and row["DeepOnlyOffBestRank"] <= 20 for row in deep_rows), len(deep_rows)),
]]

safe_candidates = [
    ("Search synonym", "日常語・口語のintent→日本語検索語を少数のaccepted aliasとして追加する候補を作り、scenario回帰を先に置く", "SEARCH_SYNONYM", "低"),
    ("Search ranking", "exact label / approved synonym / phrase-intentの順位差だけを固定scenarioで比較する", "SEARCH_RANKING", "低"),
    ("Route", "人物数・関係・行為・道具など、routeから外れた高価値例をowner別に整理してレビューする", "ROUTE", "低"),
    ("Local refinement", "localを選ぶ前後の結果件数と選択保持を検証する", "LOCAL_REFINEMENT", "低"),
    ("Body facet", "高確度のactor/action/body-site例に限ってfacet membership候補をレビューする", "BODY_FACET", "中"),
    ("Theme facet", "BDSM / reproductionなどのtheme membershipを文脈別にレビューし、AND件数を併記する", "THEME_FACET", "中"),
    ("ContentIntent", "NonSexual/Contextual/Sexualの境界caseを個別に再点検する。default filterは変えない", "CONTENT_INTENT", "中"),
    ("Usage order", "usage順でTop20外となる実用tagを限定して報告する。global ranking改定は別検証にする", "USAGE_SORT", "中"),
    ("Interaction", "multi-theme追加時のAND countと現在のfacet自動置換をUI文言で明示する案を検討する", "INTERACTION", "低"),
    ("Test only", "この200件超のintent-first corpusをsearch/browse regression gateとして継続可能にする", "NO_CHANGE", "低"),
]

avoid = [
    "この小さな固定scenario集合からGeneral/Special全体のtaxonomyを組み替えない。",
    "使用数sortを全体で下げない。低頻度tagを上げる場合はexact/strong-intentに限った根拠と回帰testを求める。",
    "複数themeのANDが0件だったことだけを理由にAND semanticsをORへ変えない。別tag同士の複合意図はtag選択workflowとして別に評価する。",
    "Sexual ContentIntentの既定値変更や、自動DeepOnlyはしない。妊娠などContextual/NonSexual境界を優先レビューする。",
    "タグのcanonical identity、Prompt出力、production catalogの意味情報をUX都合だけで変更しない。",
]

text = []
text += ["# Issue #213 — Practical ordinary-tag retrieval audit", ""]
text += ["## Executive result", ""]
text += [
    "207件（sexual 121 / general 86）をproduction runtime catalogと現行検索・UnifiedBrowse経路で評価した。最も効いた問題はtaxonomyの広さより、日本語の自然なintent表現を既存label/synonymへ結び付ける検索語彙の不足だった。",
    "自然な日本語queryではsexual targetの検索-only発見率は1.7%、Search + Browse併用も1.7%。Browse/facetだけなら73.6%が何らかの順位で見つかるが、Top20は50.4%。一方、各canonicalの日本語表示labelをそのままqueryにする診断では121/121が検索できた。まず試すべきは少数の高頻度intent synonymとscenario regressionで、global taxonomy/ranking変更ではない。",
    "",
    "Top20は結果上位のnon-target件数が多いscenarioを含む。Search-only/Browse-only/Search+Browseは独立評価。Overall GOOD/DISCOVERABLE等はtargetが見つかる最小cost経路を分類し、Search + Browse併用の状態を示す`combinedStatus`ではない。",
    "",
    "## Whole-set summary",
    "",
    table(["set", "total", "sexual", "general", "GOOD", "DISCOVERABLE", "BURIED", "NOISY", "MISLEADING", "DEAD_END", "median cost", "Top5", "Top10", "Top20"], overall_rows),
    "",
    f"`GOOD/DISCOVERABLE/BURIED/NOISY/MISLEADING/DEAD_END`は最小cost経路とfilter除去probeで分類した。C経路が空でもB経路で見つかれば全体をDEAD_ENDにはしていない。MISLEADINGは選択route/facetでtargetが消え、route-only/body-only/ContentIntent解除では現れる場合に付ける（{misleading_total}件）。",
    "",
    "## A/B/C route comparison",
    "",
    table(["set", "path", "target found", "Top5", "Top10", "Top20"], mode_rows),
    "",
    "Search-only queryはscenarioの日本語自然語だけを入力した。Browse-onlyはscenario記載のroute/local/facet/content/deep stateを適用した使用数sort順。Search + Browseは日本語query hitを同じstateで絞った。",
    "",
    "## Sexual set by family",
    "",
    f"複合intentは121件中{DATA['Sexual']['ComplexCount']}件。ここではrouteとBodySiteまたはThemeの併用を複合条件として数えた。",
    "",
    table(["family", "n", "GOOD", "DISCOVERABLE", "BURIED", "NOISY", "MISLEADING", "DEAD_END", "Top5", "Top10", "Top20"], family_rows),
    "",
    "Multi-person/actor-targetとPOV/compositionは特に弱い。multi-personは9件中3件だけ結果集合にtargetがあり、Top20到達0%。Compositionは6/12がdead endで、body focusと画角/一人称視点の関係をintent語彙とbrowse routeの両方で再点検する価値がある。",
    "",
    "### General / Special sample comparison",
    "",
    table(["scenario set", "catalog category", "n", "found", "Top5", "Top10", "Top20"], category_rows),
    "",
    "sexual scenarioはSpecial 117件、General 4件であり、General側のsexual用途比較は小標本。全体のSpecial 117 / General 90でもscenario選定標本なのでpopulation quality estimateではない。",
    "",
    "## Focused facet and interaction probes",
    "",
    table(["production state", "result count", "BodySite", "Theme", "sample top tags"], probe_rows),
    "",
    "- Browse indexの複数ThemeはANDで照合する。BDSM_RESTRAINT 273件、REPRO_PREGNANCY_LACTATION 28件に対し、両Theme ANDは0件。BREAST_NIPPLE + 両Themeも0件。複数themeを同一tagへ要求すると空集合になる。",
    "- `DictionaryWorkspaceViewModel.ToggleTheme`は二つ目を加えた時AND件数が0なら、先のThemeを保持せず後から選んだThemeだけに切り替える。0件を防ぐが、AND選択を静かに置換する。評価JSONの`ThemeAndViewModel`に実行結果がある。",
    "- BodySite BREAST_NIPPLEはAll 322件、Sexual 270件、GeneralPurpose 223件。`ACTION_CONTACT + BREAST_NIPPLE`はSexual 137件。body filterは候補を狭めるが、行為別探索にはaction routeとの併用が必要。",
    "- Sexual neutral browseは2,964件、DeepOnlyで1,726件。DeepOnlyはSpecial deep discoveryを絞るが、targetを上位へ上げるrankerではない。",
    "- local refinementを明示した8件では、school_uniformはCLOTHING/UNIFORMで1位。一方CLOTHING/EVERYDAYではblazer 125位、hoodie 73位、sweater 49位、apron 48位。localが意味を絞っても使用数sortの埋もれは残る。",
    "",
    "### DeepOnly target effect",
    "",
    table(["DeepOnly scenarios", "Top5", "Top10", "Top20", "found with DeepOnly", "found when off", "off Top20"], deep_summary),
    "",
    "DeepOnlyはroute/facetで発見対象がSpecial deep identitiesになる場合に絞り込み用として使える。off側のfoundが多いcaseは、一般タグとしてのtargetや未分類tagをDeepOnlyで隠すtrade-offを示す。DeepOnly自体は順位改善ではない。",
    "",
    "## Cause ranking — overall Top 20",
    "",
    table(["#", "scenario IDs", "affected target examples", "observed behavior / root cause", "family", "frequency", "safest next category"], top20_rows),
    "",
    f"Root-cause頻度はscenario×cause出現数で、相互排他的な件数ではない。全scenarioの{all_cause_counts['SEARCH_SYNONYM']}件にSEARCH_SYNONYMが付いた。failure familyの頻度と具体IDはscenario-results.csv / evaluation.jsonを正本にする。",
    "",
    "## Sexual-only highest-impact issues",
    "",
    table(["#", "scenario IDs", "target examples", "n", "current behavior / cause", "safest next category"], sexual_top_rows),
    "",
    "Top10の次点群にはanal/buttock、female genital、fluid、male genital、oral、pose、nonhumanが続く。multi-personは発見率33.3%、compositionは50.0%。",
    "",
    "## Safe improvement candidates (no implementation in this audit)",
    "",
    table(["#", "category", "candidate", "cause", "risk"], [[i, *row] for i, row in enumerate(safe_candidates, 1)]),
    "",
    "## Changes to avoid",
    "",
    *[f"- {item}" for item in avoid],
    "",
    "## Measurement contract and limits",
    "",
    "- Cost: query entry 1; primary route 1; local refinement 1; each BodySite/Theme facet 1; changing ContentIntent 1; enabling DeepOnly 1. For an empty query Browse path has no query cost. Classification knowledge steps count the selected route/local/facets/content/deep controls; it is a lower-bound proxy and does not model user hesitation or reading time.",
    "- Rank: A and C use current search output order. B uses UnifiedBrowseIndex.Browse ordered with the exact DictionaryWorkspaceViewModel default `OrderByDescending(Usage)` behavior. The report separately records mode result counts/ranks and best-cost path.",
    "- GOOD: best path Top5, cost <= 5, and not noisy; DISCOVERABLE: target Top20; BURIED: target exists but rank >20; NOISY: Top20 includes >=15 non-acceptable rows and result set >100; MISLEADING: chosen route/facet/content/deep filters hide a target present after removing one of those filters; DEAD_END: no target in A/B/C or the matched broader filter probes.",
    "- Noise is a conservative count of rows outside the acceptable target set, not human semantic annotation. Related tags may still be useful; NOISY is therefore a provisional upper-bound label. `ConfusingSimilarTags` records visible examples for review.",
    "- Search-only 10/207; Browse-only 154/207; combined 8/207; exact Japanese label diagnostic 207/207. Tag label availability did not imply that a user phrase matched it.",
    "- The scenario set is curated, intent-first, and fixed; it is not a random population sample. Expected tags are verified against the production catalog. Single-target ground truths dominate, so semantic equivalence for ambiguous prompts remains a review limit.",
    "- No images were generated. Native desktop automation was not used. 17 representative flows compared actual DictionaryWorkspaceViewModel results against the corresponding catalog/search/index results; all 17 matched. This is logic-level integration, not visual WPF control validation.",
    "- Source authority: origin/main `a90f5b652d4239709005d020417a236ea9d97ebb`. Runtime manifest provenance matches that SHA. Production catalog SHA-256 `5759156FF79D794DDC70DD5459AF9B80F8CB204C4527BE16FD368FF40BE9F141`.",
    "",
    "## Reproduction",
    "",
    "Set `DTT_ISSUE213_CATALOG` to the read-only runtime catalog, then run `python scripts/issue213/build_scenario_corpus.py`; it verifies every canonical target exists. Run the focused test with `DTT_ISSUE213_CATALOG`, `DTT_ISSUE213_SCENARIOS`, and `DTT_ISSUE213_REPORT` set to the catalog, scenario JSON, and output JSON paths. `python scripts/issue213/render_report.py` writes this report and the flat CSV.",
    "",
    "Scenario source: `scenarios.json`. Full per-scenario output: `evaluation.json`. Flat ledger: `scenario-results.csv`.",
    "",
]

# Replace the intentionally short hash note with the verified manifest value.
text = [line.replace("5759156FF79D794DDC70DD5459AF9B80F8CB204C4527BE16FD368EF", "5759156FF79D794DDC70DD5459AF9B80F8CB204C4527BE16FD368FF40BE9F141") for line in text]
REPORT.write_text("\n".join(text), encoding="utf-8")
print(f"wrote {REPORT} and {RESULTS}")
