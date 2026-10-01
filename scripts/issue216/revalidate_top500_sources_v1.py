#!/usr/bin/env python3
"""Revalidate and import the exact first-party source subset already checked in #216."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from authority_coverage import (
    DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id, read_csv,
)

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
COHORT = ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv"
DECISIONS = ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"
SOURCES = ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv"
MEMBERS = ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"
TOP500_LEDGER = ISSUE216 / "HIGH_FREQUENCY_RESCUE_LEDGER_V1.csv"
REVIEWED_AT = "2026-09-30"
REVIEWER = "Codex independent first-party source review"


def _source(url: str, home: str, source_type: str, owner: str, members: list[str], claim: str,
            scope: str, notes: str = "") -> dict[str, str]:
    source_id = deterministic_source_id(url, owner, scope)
    return {
        "source_id": source_id, "_member_tags": "|".join(members),
        "copyright_canonical": home, "source_url": url,
        "source_type": source_type, "authority_owner": owner, "source_status": "ACCEPTED",
        "source_scope": scope, "exact_roster_available": "true", "reviewed_at": REVIEWED_AT,
        "source_claim": claim, "provenance": f"Independent review of official first-party source on {REVIEWED_AT}; exact members: {', '.join(members)}.",
        "reusable": "true" if len(members) > 1 else "false", "notes": notes,
    }


SOURCES_DATA = [
    _source("https://www.evangelion.jp/news/eva_bdboxse/", "neon_genesis_evangelion", "OFFICIAL_SERIES_DIRECTORY", "EVANGELION official site", ["souryuu_asuka_langley"], "The official page identifies the TV series and explicitly lists 惣流・アスカ・ラングレー in its cast.", "One cast member; original TV series cast, not film appearance."),
    _source("https://frieren-anime.jp/character/chara_group1/1-1/", "sousou_no_frieren", "OFFICIAL_CHARACTER_PROFILE", "Frieren anime production committee", ["frieren"], "The official character profile names フリーレン and identifies the Sousou no Frieren series site.", "One dedicated character profile."),
    _source("https://spy-family.net/tvseries/", "spy_x_family", "OFFICIAL_CHARACTER_PROFILE", "SPY×FAMILY TV anime official site", ["yor_briar"], "The official TV series page gives the English/Japanese name YOR FORGER / ヨル・フォージャー and her character profile.", "One dedicated character profile within the TV series."),
    _source("https://anime.bang-dream.com/avemujica/character/mutsumi/", "bang_dream!", "OFFICIAL_CHARACTER_PROFILE", "Bushiroad / BanG Dream! Project", ["wakaba_mutsumi"], "The official profile identifies 若葉 睦 / Mutsumi Wakaba as an Ave Mujica member.", "One Ave Mujica character profile; root normalization Ave Mujica -> bang_dream! is explicit in Issue #180 AUTHORITY_POLICY_V1."),
    _source("https://anime.bang-dream.com/avemujica/character/uika/", "bang_dream!", "OFFICIAL_CHARACTER_PROFILE", "Bushiroad / BanG Dream! Project", ["misumi_uika"], "The official profile identifies 三角 初華 / Uika Misumi as an Ave Mujica member.", "One Ave Mujica character profile; root normalization Ave Mujica -> bang_dream! is explicit in Issue #180 AUTHORITY_POLICY_V1."),
    _source("https://anime.bang-dream.com/avemujica/character/umiri/", "bang_dream!", "OFFICIAL_CHARACTER_PROFILE", "Bushiroad / BanG Dream! Project", ["yahata_umiri"], "The official profile identifies 八幡 海鈴 / Umiri Yahata as an Ave Mujica member.", "One Ave Mujica character profile; root normalization Ave Mujica -> bang_dream! is explicit in Issue #180 AUTHORITY_POLICY_V1."),
    _source("https://csassets.nintendo.com/noaext/image/private/t_KA_PDF/Metroid_Samus_Returns_EN?_a=DATAg1AAZAA0", "metroid", "OFFICIAL_GAME_ROSTER", "Nintendo Co., Ltd.", ["samus_aran"], "The official Samus Returns manual explicitly labels Samus Aran as a Metroid Series character.", "One named character; official game manual and series label."),
    _source("https://limbuscompany.com/", "limbus_company", "OFFICIAL_GAME_ROSTER", "Project Moon (official Limbus Company site)", ["don_quixote_(project_moon)", "ishmael_(project_moon)", "faust_(project_moon)", "hong_lu_(project_moon)", "sinclair_(project_moon)", "ryoshu_(project_moon)", "yi_sang_(project_moon)"], "The official Sinner Owner's Manual names Don Quixote, Ishmael, Faust, Hong Lu, Sinclair, Ryōshū, and Yi Sang as Limbus Company Sinners.", "Exactly seven explicitly named Sinners; no inference from other Project Moon works.", "The source is partial to these exact mapped members; absence of other tags is not evidence."),
    _source("https://game.capcom.com/residentevil/en/exfile-2-17.html", "resident_evil", "OFFICIAL_CHARACTER_PROFILE", "CAPCOM CO., LTD.", ["leon_s._kennedy"], "Capcom's Resident Evil Portal extra file is a dedicated Leon S. Kennedy profile and describes his Resident Evil appearances.", "One dedicated character profile."),
    _source("https://spice-and-wolf.com/", "spice_and_wolf", "OFFICIAL_CHARACTER_ROSTER", "Spice and Wolf anime official site", ["holo"], "The official site lists ホロ in its character section, identifies her role in the series, and names the source light-novel franchise.", "One named character; adaptation site supports the stable Spice and Wolf root."),
    _source("https://uy-allstars.com/character/", "urusei_yatsura", "OFFICIAL_CHARACTER_PROFILE", "Urusei Yatsura anime official site", ["lum"], "The official character directory names ラム / LUM and gives her character profile.", "One named character in the official series directory."),
    _source("https://persona.atlus.com/p3r/index.html?lang=enbuy", "persona", "OFFICIAL_CHARACTER_PROFILE", "ATLUS", ["aigis_(persona)"], "The official Persona 3 Reload site lists Aigis with a dedicated character profile and identifies the title as part of the Persona series.", "One character profile; Persona 3 Reload is normalized to its stable Persona series root."),
    _source("https://game.capcom.com/residentevil/en/umbrella-20230920180000.html", "resident_evil", "OFFICIAL_SERIES_DIRECTORY", "CAPCOM CO., LTD.", ["ada_wong"], "Capcom's official article names Ada Wong and explicitly discusses her appearances across Resident Evil titles.", "One named recurring character; the article distinguishes appearances while keeping the Resident Evil series context."),
]

ALIASES = {
    "souryuu_asuka_langley": "惣流・アスカ・ラングレー -> exact named series cast member",
    "frieren": "フリーレン -> reviewed canonical name mapping to frieren",
    "yor_briar": "ヨル・フォージャー / YOR FORGER -> reviewed canonical name mapping to yor_briar",
    "wakaba_mutsumi": "若葉 睦 / Mutsumi Wakaba -> reviewed canonical name mapping to wakaba_mutsumi",
    "misumi_uika": "三角 初華 / Uika Misumi -> reviewed canonical name mapping to misumi_uika",
    "yahata_umiri": "八幡 海鈴 / Umiri Yahata -> reviewed canonical name mapping to yahata_umiri",
    "samus_aran": "Samus Aran -> reviewed canonical name mapping to samus_aran",
    "don_quixote_(project_moon)": "Don Quixote -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "ishmael_(project_moon)": "Ishmael -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "faust_(project_moon)": "Faust -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "hong_lu_(project_moon)": "Hong Lu -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "sinclair_(project_moon)": "Emil Sinclair -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "ryoshu_(project_moon)": "Ryōshū -> reviewed exact Sinner identity; romanization/diacritic equivalence reviewed",
    "yi_sang_(project_moon)": "Yi Sang -> reviewed exact Sinner identity; project_moon qualifier retained as identity disambiguation",
    "leon_s._kennedy": "Leon S. Kennedy -> reviewed canonical name mapping to leon_s._kennedy",
    "holo": "ホロ -> reviewed canonical name mapping to holo",
    "lum": "ラム / LUM -> reviewed canonical name mapping to lum",
    "aigis_(persona)": "Aigis -> reviewed exact Persona 3 Reload character; persona qualifier retained as identity disambiguation",
    "ada_wong": "Ada Wong -> reviewed canonical name mapping to ada_wong",
}


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cohort = read_csv(COHORT)
    cohort_by_tag = {row["canonical_character"]: row for row in cohort}
    original_ledger = {row["canonical_character"]: row for row in read_csv(TOP500_LEDGER)}
    current_decisions = read_csv(DECISIONS)
    decisions_by_tag = {row["canonical_character"]: row for row in current_decisions}
    current_sources = read_csv(SOURCES)
    current_members = read_csv(MEMBERS)

    expected_tags = set(ALIASES)
    if len(expected_tags) != 19 or not expected_tags <= set(cohort_by_tag):
        raise SystemExit("expected 19 exact source-checked Top500 Characters in frozen full cohort")
    for tag in expected_tags:
        source_check = original_ledger.get(tag)
        if not source_check or source_check["review_status"] != "EXACT_MEMBER_SOURCE_CHECKED":
            raise SystemExit(f"Top500 source-check lineage missing for {tag}")
        if source_check["proposed_home"] != next(s["copyright_canonical"] for s in SOURCES_DATA
                                                 if tag in s["_member_tags"].split("|")):
            raise SystemExit(f"source/root mapping mismatch with the frozen #216 proposal: {tag}")
        if decisions_by_tag[tag]["research_state"] not in {"UNRESEARCHED", "HOME_CONFIRMED"}:
            raise SystemExit(f"refusing to replace a conflicting terminal decision: {tag}")

    sources = sorted(({field: row[field] for field in SOURCE_FIELDS} for row in SOURCES_DATA),
                     key=lambda row: row["source_id"])
    source_for_tag = {tag: source for source in SOURCES_DATA for tag in source["_member_tags"].split("|")}
    members: list[dict[str, str]] = []
    for tag in sorted(expected_tags):
        source = source_for_tag[tag]
        members.append({
            "source_id": source["source_id"], "canonical_character": tag,
            "matched_surface": ALIASES[tag].split(" -> ", 1)[0], "mapping_method": "REVIEWED_NAME_MAPPING",
            "mapping_evidence": ALIASES[tag], "reviewed_at": REVIEWED_AT, "reviewer": REVIEWER,
            "mapping_status": "EXACT_COVERED",
        })

    for tag in sorted(expected_tags):
        original = original_ledger[tag]
        source = source_for_tag[tag]
        decision = decisions_by_tag[tag]
        decision.update({
            "research_state": "HOME_CONFIRMED", "home_copyright": original["proposed_home"],
            "authority_type": source["source_type"], "source_ids": source["source_id"],
            "source_claim": original["source_claim"],
            "provenance": (
                f"Independent Issue #216 revalidation on {REVIEWED_AT}; exact first-party member mapping recorded in "
                f"AUTHORITY_SOURCE_MEMBERS_V1.csv. Canonical root checked against source scope and Issue #180 root policy. "
                f"Source URL: {source['source_url']}"
            ),
            "reviewed_at": REVIEWED_AT, "reason_code": "FIRST_PARTY_EXACT_MEMBER_AND_HOME_ROOT",
            "reason_detail": source["source_claim"] + " Existing #180 unresolved reason had no competing validated HOME; HOME is additive in this coverage layer.",
            "validated_home_candidates": "",
        })

    members = sorted(members, key=lambda row: (row["source_id"], row["canonical_character"]))
    if current_sources and current_sources != sources:
        raise SystemExit("existing source registry differs from deterministic #216 source revalidation")
    if current_members and current_members != members:
        raise SystemExit("existing exact-member ledger differs from deterministic #216 source revalidation")
    expected_decisions = [decisions_by_tag[row["canonical_character"]] for row in cohort]
    if current_sources == sources and current_members == members and current_decisions == expected_decisions:
        print("Top500 source revalidation reproducibility: PASS (19 members / 13 sources)")
        return
    if any(decisions_by_tag[tag]["research_state"] == "HOME_CONFIRMED" and
           decisions_by_tag[tag]["source_ids"] != source_for_tag[tag]["source_id"] for tag in expected_tags):
        raise SystemExit("an existing #216 decision conflicts with the reviewed source mapping")
    write_rows(SOURCES, SOURCE_FIELDS, sources)
    write_rows(MEMBERS, MEMBER_FIELDS, members)
    write_rows(DECISIONS, DECISION_FIELDS, expected_decisions)
    print(f"revalidated exact first-party HOME decisions: {len(expected_tags)}; distinct sources: {len(sources)}")


if __name__ == "__main__":
    main()
