from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "artifacts/issue179-quality-census/quality_census.csv"
OUT = ROOT / "artifacts/issue179-display-cleanup"
OUT_CSV = OUT / "DISPLAY_CLEANUP_CANDIDATES_V1.csv"

PAREN_RE = re.compile(r"（([^）]*)）|\(([^()]*)\)")
LOWER_ASCII_RE = re.compile(r"[a-z]{3,}")

FIELDS = [
    "row_id", "canonical_tag", "category", "post_count",
    "old_display_ja", "proposed_display_ja", "reason",
    "source_search_term", "review_state", "review_note",
]

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower().replace("_", " ")
    return " ".join(value.split())

def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split("|") if x.strip()]

def base_surface(value: str) -> str:
    m = re.search(r"[（(]", value or "")
    return (value[:m.start()] if m else value).strip()

def groups(value: str) -> list[str]:
    return [next(g for g in m.groups() if g is not None) for m in PAREN_RE.finditer(value or "")]

def has_japanese(value: str) -> bool:
    return any("\u3040" <= c <= "\u30ff" or "\u3400" <= c <= "\u9fff" for c in value)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with CENSUS.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    display_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in rows:
        key = norm(r["display_ja"])
        if key:
            display_index[(r["category"], key)].add(r["row_id"])

    out: list[dict[str, str]] = []
    for r in rows:
        flags = set((r.get("risk_flags") or "").split("|"))
        display = r["display_ja"]
        search_terms = split_pipe(r["search_ja"])
        base = base_surface(display)

        # 1) Raw lowercase-English qualifier remains in Japanese display, but
        # an existing search surface already provides a same-base, same-depth
        # Japanese/styled qualifier. Reuse that exact existing surface.
        if "DISPLAY_MIXED_ASCII_QUALIFIER" in flags and base:
            old_groups = groups(display)
            candidates: list[str] = []
            for term in search_terms:
                if term == display or base_surface(term) != base:
                    continue
                gs = groups(term)
                if len(gs) != len(old_groups) or not gs:
                    continue
                if not has_japanese(term):
                    continue
                # Lowercase ASCII inside a qualifier is the problem being fixed.
                if any(LOWER_ASCII_RE.search(g) for g in gs):
                    continue
                candidates.append(term)
            candidates = list(dict.fromkeys(candidates))
            if len(candidates) == 1:
                out.append({
                    "row_id": r["row_id"],
                    "canonical_tag": r["canonical_tag"],
                    "category": r["category"],
                    "post_count": r["post_count"],
                    "old_display_ja": display,
                    "proposed_display_ja": candidates[0],
                    "reason": "EXISTING_SEARCH_HAS_LOCALIZED_QUALIFIER",
                    "source_search_term": candidates[0],
                    "review_state": "PROPOSED_SECOND_REVIEW",
                    "review_note": "",
                })
                continue

        # 2) Historical semantic fix added a context suffix to an unqualified
        # Character. If the suffix-free base already exists as a search surface
        # and no other Character currently uses that base as its display, it is
        # a safe candidate for over-disambiguation review.
        if "DISPLAY_ADDED_CONTEXT_UNQUALIFIED" in flags and r["category"] == "Character" and base:
            if base in search_terms:
                other = display_index.get(("Character", norm(base)), set()) - {r["row_id"]}
                if not other:
                    out.append({
                        "row_id": r["row_id"],
                        "canonical_tag": r["canonical_tag"],
                        "category": r["category"],
                        "post_count": r["post_count"],
                        "old_display_ja": display,
                        "proposed_display_ja": base,
                        "reason": "UNQUALIFIED_CANONICAL_CONTEXT_SUFFIX_NO_DISPLAY_COLLISION",
                        "source_search_term": base,
                        "review_state": "PROPOSED_SECOND_REVIEW",
                    "review_note": "",
                    })

    # One proposal per row. Prefer localized qualifier repair if both paths hit.
    dedup: dict[str, dict[str, str]] = {}
    for row in out:
        dedup.setdefault(row["row_id"], row)
    final = list(dedup.values())

    # Second-review safety gate. The proposal is accepted only when it cannot
    # create a new proposed-display collision and the current row is not already
    # in a display collision. Localized-qualifier repairs must also replace the
    # changed raw qualifier with a non-ASCII-letter surface; abbreviations such
    # as FGO/LCB/TF2 remain HOLD for individual review.
    proposed_counts: dict[str, int] = {}
    for row in final:
        proposed_counts[row["proposed_display_ja"]] = proposed_counts.get(row["proposed_display_ja"], 0) + 1

    census_by_id = {r["row_id"]: r for r in rows}
    for row in final:
        src = census_by_id[row["row_id"]]
        collision_free = int(src.get("display_collision_other_rows") or "0") == 0
        unique_proposal = proposed_counts[row["proposed_display_ja"]] == 1
        safe = collision_free and unique_proposal

        if row["reason"] == "EXISTING_SEARCH_HAS_LOCALIZED_QUALIFIER":
            old_g = groups(row["old_display_ja"])
            new_g = groups(row["proposed_display_ja"])
            changed = [n for o, n in zip(old_g, new_g) if o != n]
            if not changed or any(re.search(r"[A-Za-z]", g) for g in changed):
                safe = False

        if safe:
            row["review_state"] = "SECOND_REVIEW_ACCEPTED"
            row["review_note"] = "collision-safe conservative second review"
        else:
            row["review_state"] = "HOLD_INDIVIDUAL_REVIEW"
            row["review_note"] = "abbreviation/current-or-proposed collision requires individual review"

    final.sort(key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(final)

    reasons: dict[str, int] = {}
    states: dict[str, int] = {}
    for row in final:
        reasons[row["reason"]] = reasons.get(row["reason"], 0) + 1
        states[row["review_state"]] = states.get(row["review_state"], 0) + 1
    print(f"DISPLAY_CLEANUP_CANDIDATES rows={len(final)} reasons={reasons} states={states}")

if __name__ == "__main__":
    main()
