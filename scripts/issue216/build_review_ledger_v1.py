#!/usr/bin/env python3
"""Build a separate, additive high-frequency HOME_UNRESOLVED audit ledger."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COHORT = ROOT / "docs/issue216/TOP500_COHORT_V1.csv"
UNITS = ROOT / "artifacts/issue180-v3/research_units_v3.csv"
REVIEWS = ROOT / "docs/issue180/v3/research_unit_terminal_reviews_v3.csv"
LINKAGE = ROOT / "docs/issue216/TOP500_RESEARCH_UNIT_LINKAGE_V1.csv"
OUT = ROOT / "docs/issue216/HIGH_FREQUENCY_RESCUE_LEDGER_V1.csv"

# These are bounded, exact-member checks against first-party character/roster
# pages. No broader franchise hint is promoted into evidence by this map.
CHECKED: dict[str, tuple[str, str, str, str]] = {
    "souryuu_asuka_langley": (
        "neon_genesis_evangelion", "https://www.evangelion.jp/news/eva_bdboxse/",
        "Official Evangelion material names 惣流・アスカ・ラングレー in the original series cast.", "official_series_cast",
    ),
    "frieren": (
        "sousou_no_frieren", "https://frieren-anime.jp/character/chara_group1/1-1/",
        "Official character profile names Frieren under the Sousou no Frieren anime site.", "official_character_profile",
    ),
    "yor_briar": (
        "spy_x_family", "https://spy-family.net/tvseries/",
        "Official TV anime page identifies YOR FORGER / ヨル・フォージャー as a Spy x Family character.", "official_character_profile",
    ),
    "samus_aran": (
        "metroid", "https://csassets.nintendo.com/noaext/image/private/t_KA_PDF/Metroid_Samus_Returns_EN?_a=DATAg1AAZAA0",
        "Nintendo manual identifies Samus Aran as a Metroid Series character.", "official_game_manual",
    ),
    "leon_s._kennedy": (
        "resident_evil", "https://game.capcom.com/residentevil/en/exfile-2-17.html",
        "Capcom's official Resident Evil character profile names Leon S. Kennedy.", "official_character_profile",
    ),
    "holo": (
        "spice_and_wolf", "https://spice-and-wolf.com/",
        "Official Spice and Wolf anime site lists Holo in its character section.", "official_character_roster",
    ),
    "lum": (
        "urusei_yatsura", "https://uy-allstars.com/character/",
        "Official Urusei Yatsura character page lists Lum / ラム.", "official_character_profile",
    ),
    "aigis_(persona)": (
        "persona", "https://persona.atlus.com/p3r/index.html?lang=enbuy",
        "ATLUS's official Persona 3 Reload character page has a dedicated Aigis profile and identifies the title as part of the Persona series.", "official_character_profile",
    ),
    "ada_wong": (
        "resident_evil", "https://game.capcom.com/residentevil/en/umbrella-20230920180000.html",
        "Capcom's official Resident Evil Portal article names Ada Wong and describes her appearances across Resident Evil titles.", "official_series_character_article",
    ),
    "don_quixote_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Don Quixote as a Sinner.", "official_character_roster",
    ),
    "ishmael_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Ishmael as a Sinner.", "official_character_roster",
    ),
    "faust_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Faust as a Sinner.", "official_character_roster",
    ),
    "hong_lu_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Hong Lu as a Sinner.", "official_character_roster",
    ),
    "sinclair_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Sinclair as a Sinner.", "official_character_roster",
    ),
    "ryoshu_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Ryōshū as a Sinner.", "official_character_roster",
    ),
    "yi_sang_(project_moon)": (
        "limbus_company", "https://limbuscompany.com/",
        "Official Limbus Company Sinner Owner's Manual lists Yi Sang as a Sinner.", "official_character_roster",
    ),
    "wakaba_mutsumi": (
        "bang_dream!", "https://anime.bang-dream.com/avemujica/character/mutsumi/",
        "Official Ave Mujica character roster lists 若葉睦 / Mutsumi Wakaba.", "official_character_roster",
    ),
    "misumi_uika": (
        "bang_dream!", "https://anime.bang-dream.com/avemujica/character/uika/",
        "Official Ave Mujica character roster lists 三角初華 / Uika Misumi.", "official_character_roster",
    ),
    "yahata_umiri": (
        "bang_dream!", "https://anime.bang-dream.com/avemujica/character/umiri/",
        "Official Ave Mujica character roster lists 八幡海鈴 / Umiri Yahata.", "official_character_roster",
    ),
}

FIELDS = [
    "rank", "canonical_character", "post_count", "baseline_state", "baseline_reason",
    "candidate_roots_hint", "research_unit_ids", "research_unit_fingerprints",
    "existing_terminal_states", "audit_lane", "audit_disposition", "proposed_home",
    "authority_type", "source_url", "source_claim", "review_provenance", "review_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def freeze_linkage(cohort: list[dict[str, str]]) -> list[dict[str, str]]:
    if LINKAGE.exists():
        return read_csv(LINKAGE)
    units = read_csv(UNITS)
    reviews = {r["unit_id"]: r for r in read_csv(REVIEWS)}
    rows: list[dict[str, str]] = []
    for unit in units:
        members = json.loads(unit["member_ids/tags"])
        fingerprint = sha256_text("\n".join(sorted(members)))
        review = reviews.get(unit["unit_id"], {})
        terminal = review.get("terminal_status") or unit["status"]
        for item in cohort:
            if item["canonical_character"] in members:
                rows.append({
                    "rank": item["rank"], "canonical_character": item["canonical_character"],
                    "unit_id": unit["unit_id"], "member_ids_sha256": fingerprint,
                    "terminal_status": terminal,
                })
    linked = {r["canonical_character"] for r in rows}
    for item in cohort:
        if item["canonical_character"] not in linked:
            rows.append({"rank": item["rank"], "canonical_character": item["canonical_character"],
                         "unit_id": "", "member_ids_sha256": "", "terminal_status": ""})
    rows.sort(key=lambda r: (int(r["rank"]), r["unit_id"]))
    with LINKAGE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "canonical_character", "unit_id", "member_ids_sha256", "terminal_status"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    cohort = read_csv(COHORT)
    linkage = freeze_linkage(cohort)
    unit_for_tag: dict[str, list[tuple[str, str, str]]] = {}
    for row in linkage:
        if row["unit_id"]:
            unit_for_tag.setdefault(row["canonical_character"], []).append(
                (row["unit_id"], row["member_ids_sha256"], row["terminal_status"])
            )

    rows: list[dict[str, str]] = []
    for item in cohort:
        tag = item["canonical_character"]
        related = unit_for_tag.get(tag, [])
        check = CHECKED.get(tag)
        if check:
            home, url, claim, authority = check
            lane, disposition, status = "HIGH_FREQUENCY_SOURCE_CHECK", "PROPOSED_HOME_CONFIRMED", "EXACT_MEMBER_SOURCE_CHECKED"
            provenance = "Independent Issue #216 review of a first-party source; source names exact member and identifies the title/series. Does not alter the frozen Issue #180 master."
        else:
            home = url = claim = authority = ""
            if int(item["rank"]) <= 100:
                lane, disposition, status = "TOP_100_DETERMINISTIC_REVIEW", "REMAINS_HOME_UNRESOLVED", "NO_NEW_SOURCE_CHECK"
                provenance = "Reviewed frozen #180 state/reason, candidate hints, existing relation/source-review pointers, and current Research Unit terminal record. No exact safe HOME path recorded in this bounded pass."
            else:
                lane, disposition, status = "RANK_101_500_DETERMINISTIC_SAMPLE", "REMAINS_HOME_UNRESOLVED", "NOT_EXTERNALLY_RESEARCHED"
                provenance = "Deterministic triage only: reviewed frozen #180 state/reason, candidate hints, existing relation/source-review pointers, and current Research Unit terminal record. External source research intentionally limited to highest-frequency first 100."
        rows.append({
            "rank": item["rank"], "canonical_character": tag, "post_count": item["post_count"],
            "baseline_state": item["previous_state"], "baseline_reason": item["previous_unresolved_reason"],
            "candidate_roots_hint": item["candidate_roots"],
            "research_unit_ids": " | ".join(x[0] for x in related),
            "research_unit_fingerprints": " | ".join(x[1] for x in related),
            "existing_terminal_states": " | ".join(x[2] for x in related),
            "audit_lane": lane, "audit_disposition": disposition, "proposed_home": home,
            "authority_type": authority, "source_url": url, "source_claim": claim,
            "review_provenance": provenance, "review_status": status,
        })

    if len(rows) != 500 or len({r["canonical_character"] for r in rows}) != 500:
        raise SystemExit("cohort must contain 500 unique characters")
    if OUT.exists():
        if read_csv(OUT) != rows:
            raise SystemExit("frozen audit ledger differs from deterministic rebuild")
        print(f"audit ledger reproducibility: PASS ({len(rows)} rows)")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} audit rows; exact-source checked {len(CHECKED)}; unresolved {500-len(CHECKED)}")


if __name__ == "__main__":
    main()
