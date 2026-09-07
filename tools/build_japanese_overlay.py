"""Build the local-only Stage 6.5 Japanese overlay from pinned source files."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.japanese_overlay import JapaneseOverlay, JapaneseTerm, TERM_COLUMNS
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.normalization import normalize_lookup


SOURCES = ROOT / "data/japanese/japanese_sources.json"
TERMS = ROOT / "data/japanese/japanese_terms.csv"
OVERLAY = ROOT / "data/runtime/japanese_overlay.json"
AUDIT = ROOT / "benchmarks/stage6_5/japanese_import_audit.json"
EXAMPLES = ROOT / "benchmarks/stage6_5/japanese_import_examples.csv"

KANA = re.compile(r"[\u3040-\u30ff]")
HANGUL = re.compile(r"[\uac00-\ud7af]")
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
USAGE_PRIORITY = {"display": 0, "search": 1, "candidate": 2, "rejected": 3}
EXAMPLE_LIMITS = {
    ("exact_canonical", "search"): 20,
    ("exact_canonical", "candidate"): 20,
    ("exact_canonical", "rejected"): 10,
    ("alias_only", "rejected"): 10,
    ("unmatched", "rejected"): 10,
    ("ambiguous", "search"): 10,
    ("ambiguous", "candidate"): 10,
    ("ambiguous", "rejected"): 10,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _external_canonical(value: str) -> str:
    return normalize_lookup(value).replace(" ", "_")


def _usage_for_alias(value: str) -> str:
    if KANA.search(value):
        return "search"
    if HANGUL.search(value):
        return "rejected"
    if CJK.search(value):
        return "candidate"
    return "rejected"


def _source_rows(source: dict):
    path = ROOT / source["source_file"]
    if not path.exists() or _sha256(path) != source["sha256"]:
        raise ValueError(f"Pinned Japanese source hash mismatch: {source['source_id']}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if source["source_id"] == "newtextdoc1111_alias_fdf2772":
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["tag", "category", "count", "alias"]:
                raise ValueError("Unexpected newtextdoc1111 source columns")
            for row in reader:
                yield row["tag"], row["alias"].split(",") if row["alias"] else []
        else:
            for row in csv.reader(stream):
                if len(row) != 2:
                    raise ValueError(f"Unexpected two-column source row: {source['source_id']}")
                yield row[0], [row[1]]


def _record_source(source: dict, knowledge: TagKnowledgeCore):
    report = Counter()
    category_matches = Counter()
    terms = []
    special_canonicals = {
        canonical for special in knowledge.special.values()
        for canonical in special.canonical_candidates
    }
    matched_canonicals = set()
    examples = []
    for external_tag, values in _source_rows(source):
        report["source_row_count"] += 1
        normalized = _external_canonical(external_tag)
        if normalized in knowledge.canonical:
            report["exact_canonical_match_count"] += 1
            matched_canonicals.add(normalized)
            category_matches[str(knowledge.canonical[normalized].category)] += 1
            if normalized in special_canonicals:
                report["special_canonical_overlap_count"] += 1
            if knowledge.canonical[normalized].category == 0 and normalized not in special_canonicals:
                report["non_special_general_match_count"] += 1
            for value in values:
                value = value.strip()
                if not value:
                    continue
                usage = ("candidate" if source["source_id"] != "newtextdoc1111_alias_fdf2772"
                         else _usage_for_alias(value))
                terms.append(JapaneseTerm(normalized, value, usage, source["source_id"]))
                examples.append((source["source_id"], normalized, value, usage,
                                 "exact_canonical"))
        elif normalize_lookup(external_tag) in knowledge.aliases:
            report["alias_only_count"] += 1
            examples.append((source["source_id"], external_tag, "", "rejected", "alias_only"))
        else:
            report["unmatched_count"] += 1
            examples.append((source["source_id"], external_tag, "", "rejected", "unmatched"))
    report["normalized_row_count"] = len(matched_canonicals)
    report["exact_canonical_match_rate"] = (
        report["exact_canonical_match_count"] / report["source_row_count"]
        if report["source_row_count"] else 0
    )
    report["project_category_match_counts"] = dict(sorted(category_matches.items()))
    report["kana_search_auto_adopt_count"] = sum(term.usage == "search" for term in terms)
    report["kanji_only_candidate_count"] = sum(
        term.usage == "candidate" and bool(CJK.search(term.ja_term)) and not bool(KANA.search(term.ja_term))
        for term in terms
    )
    report["source_term_usage_counts"] = {
        usage: sum(term.usage == usage for term in terms)
        for usage in ("display", "search", "candidate", "rejected")
    }
    return terms, report, examples


def _deduplicate(terms: list[JapaneseTerm]):
    selected = {}
    duplicates = 0
    for term in sorted(terms, key=lambda item: (
        item.canonical_tag, item.ja_term, USAGE_PRIORITY[item.usage], item.source_id
    )):
        key = (term.canonical_tag, term.ja_term)
        if key in selected:
            duplicates += 1
            continue
        selected[key] = term
    return tuple(selected.values()), duplicates


def _write_csv(path: Path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    source_manifest = json.loads(SOURCES.read_text(encoding="utf-8"))
    if set(source_manifest) != {"sources"} or not isinstance(source_manifest["sources"], list):
        raise ValueError("Unexpected Japanese source manifest")
    knowledge = TagKnowledgeCore.load(ROOT, japanese_overlay_path=ROOT / "missing-overlay.json")
    terms = []
    reports = {}
    examples = []
    for source in source_manifest["sources"]:
        required = {"source_id", "source_type", "repository", "revision", "source_file",
                    "retrieved_at", "sha256", "license", "note"}
        if set(source) != required:
            raise ValueError("Unexpected Japanese source manifest entry")
        source_terms, report, source_examples = _record_source(source, knowledge)
        terms.extend(source_terms)
        reports[source["source_id"]] = dict(report)
        examples.extend(source_examples)
    terms_by_japanese = defaultdict(set)
    for term in terms:
        terms_by_japanese[term.ja_term].add(term.canonical_tag)
    ambiguous_terms = {term for term, canonicals in terms_by_japanese.items()
                       if len(canonicals) > 1}
    examples = [
        (source_id, canonical_tag, term, usage,
         "ambiguous" if disposition == "exact_canonical" and term in ambiguous_terms else disposition)
        for source_id, canonical_tag, term, usage, disposition in examples
    ]
    terms, duplicates = _deduplicate(terms)
    overlay = JapaneseOverlay.from_terms(terms, knowledge.canonical)
    OVERLAY.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY.write_text(json.dumps(overlay.to_document(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
    _write_csv(TERMS, (dict(canonical_tag=term.canonical_tag, ja_term=term.ja_term,
                            usage=term.usage, source_id=term.source_id)
                       for term in terms), TERM_COLUMNS)
    runtime_terms = [term for term in terms if term.usage in {"display", "search"}]
    search_targets = defaultdict(set)
    for term in runtime_terms:
        search_targets[term.ja_term].add(term.canonical_tag)
    audit = {
        "format_version": 1,
        "sources": reports,
        "terms": {usage: sum(term.usage == usage for term in terms)
                  for usage in ("display", "search", "candidate", "rejected")},
        "runtime": {"canonical_count": len(overlay.search_by_canonical),
                    "term_count": len(runtime_terms)},
        "duplicate_canonical_ja_term_count": duplicates,
        "ambiguous_japanese_term_count": sum(len(values) > 1 for values in search_targets.values()),
        "source_manifest_sha256": _sha256(SOURCES),
        "runtime_overlay_sha256": _sha256(OVERLAY),
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    selected_examples = []
    for bucket, limit in EXAMPLE_LIMITS.items():
        selected_examples.extend(
            sorted((row for row in examples if (row[4], row[3]) == bucket),
                   key=lambda row: row)[:limit]
        )
    _write_csv(EXAMPLES, (dict(source_id=source_id, canonical_tag=canonical_tag, ja_term=term,
                                usage=usage, disposition=disposition)
                          for source_id, canonical_tag, term, usage, disposition in
                          sorted(selected_examples, key=lambda row: (row[4], row[3], row))),
               ("source_id", "canonical_tag", "ja_term", "usage", "disposition"))
    print(json.dumps({"terms": len(terms), "runtime_terms": len(runtime_terms),
                      "overlay_canonicals": len(overlay.search_by_canonical)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
