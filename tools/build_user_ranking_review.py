"""Format existing Stage 6 evidence for a user's qualitative review.

This script reads only saved evaluation output and the static Special2788 CSV;
it does not open the runtime index or calculate any new ranking/statistics.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "benchmarks/stage6/ranking_evaluation.json"
SPECIAL = ROOT / "data/special2788/illustrious_tag_knowledge_base_2788.csv"
LINKAGE = ROOT / "data/derived/special2788_VERIFIED_LINKAGE.csv"
OUTPUT = ROOT / "docs/stage_reports/USER_RANKING_REVIEW.md"
CASES = ("two_special_medium", "five_special_small", "five_special_medium")
METHODS = (("conditional_rate", "Conditional Rate"), ("raw_lift", "Raw Lift"))


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def support(count: int) -> str:
    if count == 1:
        return "1"
    if count <= 5:
        return "2–5"
    if count <= 10:
        return "6–10"
    if count <= 99:
        return "11–99"
    return "100以上"


def special_records():
    with SPECIAL.open(encoding="utf-8-sig", newline="") as stream:
        special = {row["ID"]: row for row in csv.DictReader(stream)}
    with LINKAGE.open(encoding="utf-8-sig", newline="") as stream:
        linkage = {row["ID"]: row for row in csv.DictReader(stream)}
    by_canonical: dict[str, list[dict[str, str]]] = {}
    for special_id, row in special.items():
        link = linkage[special_id]
        canonical = link["ChosenCanonicalTag"]
        if canonical:
            by_canonical.setdefault(canonical, []).append({
                "id": special_id, "term": row["Tag"], "japanese": row["日本語"],
            })
    return by_canonical


def japanese_for_candidate(canonical: str, by_canonical) -> str:
    """Only show Japanese wording that exists in Special2788; otherwise blank."""
    labels = list(dict.fromkeys(item["japanese"] for item in by_canonical.get(canonical, ()) if item["japanese"]))
    return " / ".join(labels) if labels else "—"


def candidate_table(rows, by_canonical) -> list[str]:
    output = [
        "| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |",
        "|---:|---|---|---:|---|---:|---:|---:|---|---|",
    ]
    for rank, row in enumerate(rows, 1):
        checks = "[ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要"
        output.append(
            f"| {rank} | `{esc(row['canonical'])}` | {esc(japanese_for_candidate(row['canonical'], by_canonical))} "
            f"| {row['co_count']:,} | {support(row['co_count'])} | {row['conditional_rate']:.2%} | "
            f"{row['raw_lift']:.2f} | {row['runtime_global_count']:,} | {esc(row['role']) if row.get('role') else '—'} | {checks} |"
        )
    return output


def ids_for_core(canonical: str, by_canonical) -> str:
    records = by_canonical.get(canonical, ())
    if not records:
        return "—"
    return "<br>".join(f"{esc(item['id'])}: `{esc(item['term'])}` — {esc(item['japanese'])}" for item in records)


def difference_table(rate_rows, lift_rows) -> list[str]:
    rate = {item["canonical"] for item in rate_rows}
    lift = {item["canonical"] for item in lift_rows}
    categories = (
        ("両方のtop20", sorted(rate & lift)),
        ("Conditional Rateだけ", [item["canonical"] for item in rate_rows if item["canonical"] not in lift]),
        ("Raw Liftだけ", [item["canonical"] for item in lift_rows if item["canonical"] not in rate]),
    )
    output = ["| 区分 | 候補 |", "|---|---|"]
    for name, candidates in categories:
        output.append(f"| {name} | {', '.join(f'`{esc(candidate)}`' for candidate in candidates) if candidates else '—'} |")
    return output


def main():
    data = json.loads(EVALUATION.read_text(encoding="utf-8"))
    by_canonical = special_records()
    lines = [
        "# Stage 6 ユーザー実用評価 — Ranking比較資料",
        "",
        "この資料は保存済みの `ranking_evaluation.json` と静的Special2788辞書だけを整形したものです。再集計、parameter変更、ランキング変更はしていません。",
        "",
        f"統計snapshot: `{data['snapshot_id']}`  ",
        f"統計母集団: {data['total_posts']:,} posts",
        "",
        "SpecialのPrompt identityとstatistics canonicalは別です。評価データはstatistics canonicalのCoreしか保存しておらず、選択されたSpecial IDは保存していません。Core表には、そのcanonicalへ既存辞書で対応するSpecial2788エントリを全件載せます。",
        "",
        "候補の日本語訳は、同じcanonicalへ対応する既存Special2788の日本語がある場合のみ表示します。`—`は今回参照した既存データには日本語訳がないことを示します。`role`は保存済み評価値のみで、全件 `other` です。",
        "",
        "support区分: `1` / `2–5` / `6–10` / `11–99` / `100以上`。supportが小さいことは、候補の意味や有用性を決めるものではありません。",
        "",
    ]
    for case_name in CASES:
        case = data["cases"][case_name]
        rate_rows = case["methods"]["conditional_rate"]["top20"]
        lift_rows = case["methods"]["raw_lift"]["top20"]
        lines += [f"## {case_name}", "", "### 1. Core内容", "", f"base_count: **{case['base_count']:,}**", "",
                  "| statistics canonical | 対応する既存Special2788エントリ（ID: Prompt identity — 日本語） |",
                  "|---|---|"]
        lines += [f"| `{esc(canonical)}` | {ids_for_core(canonical, by_canonical)} |" for canonical in case["core"]]
        for method_key, title in METHODS:
            lines += ["", f"### {title} top20", ""] + candidate_table(case["methods"][method_key]["top20"], by_canonical)
        lines += ["", "### 差分", ""] + difference_table(rate_rows, lift_rows)
        lines += ["", "### Support確認", "",
                  "候補表のsupport列で確認できます。Conditional Rate / Raw Lift別のtop20内件数は以下です。", "",
                  "| 方式 | 1 | 2–5 | 6–10 | 11–99 | 100以上 |",
                  "|---|---:|---:|---:|---:|---:|"]
        for key, title in METHODS:
            rows = case["methods"][key]["top20"]
            counts = [sum((value == "1" if label == "1" else value == label) for value in (support(row["co_count"]) for row in rows))
                      for label in ("1", "2–5", "6–10", "11–99", "100以上")]
            lines.append(f"| {title} | " + " | ".join(map(str, counts)) + " |")
        lines += ["", "---", ""]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
