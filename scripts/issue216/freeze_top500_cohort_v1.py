from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"
BASELINE_COMMIT = "9c0db59c0f1dc56402c955e718a37d9de1849d7e"
MASTER = ROOT / "artifacts/issue180-v3/character_home_master_v3.csv"
POST_COUNTS = ROOT / "docs/issue70/data/source/character_copyright_evidence_full.csv.gz"
GRAPH = ROOT / "artifacts/issue180-v3/structure_graph_v3.csv"
EVIDENCE = ROOT / "artifacts/issue180-v3/evidence_ledger_v3.csv"
SOURCE_REVIEWS = ROOT / "docs/issue180/parallel/SOURCE_REVIEW_LEDGER_V2.csv"
OUT_DIR = ROOT / "docs/issue216"
COHORT = OUT_DIR / "TOP500_COHORT_V1.csv"
MANIFEST = OUT_DIR / "TOP500_COHORT_V1.json"

FIELDS = [
    "rank", "canonical_character", "post_count", "previous_state",
    "previous_unresolved_reason", "candidate_roots", "terminal_qualifier_surface",
    "base_character_candidates", "variant_relation_candidates",
    "existing_validated_relations", "accepted_source_reviews_at_candidate_roots",
    "proposed_home", "final_state", "authority_type", "source_url",
    "source_claim", "provenance", "review_status",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def stable(values: set[str] | list[str]) -> str:
    return " | ".join(sorted({value.strip() for value in values if value and value.strip()}))


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    if not MASTER.exists():
        raise SystemExit(f"frozen #180 master artifact is unavailable: {MASTER}")
    master_hash = sha256(MASTER)
    if master_hash != BASELINE_SHA256:
        raise SystemExit(f"#180 baseline master SHA mismatch: {master_hash}")

    master = rows(MASTER)
    unresolved = {
        row["canonical_tag"]: row
        for row in master
        if row["final_state"] == "HOME_UNRESOLVED"
    }
    if len(master) != 35890 or len(unresolved) != 13983:
        raise SystemExit("#180 frozen Character population/state counts do not match the issue baseline")

    post_counts: dict[str, int] = {}
    with gzip.open(POST_COUNTS, "rt", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            tag = row["character_tag"]
            if tag in unresolved:
                count = int(row["character_post_count"])
                post_counts[tag] = max(post_counts.get(tag, 0), count)
    ranked = sorted(post_counts.items(), key=lambda item: (-item[1], item[0]))
    cohort = ranked[:500]
    if len(post_counts) != 13881 or len(cohort) != 500:
        raise SystemExit("#180 unresolved/post-count join does not match the recorded snapshot coverage")

    graph_by_tag: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in rows(GRAPH):
        graph_by_tag[edge["subject_key"]].append(edge)
    evidence_by_tag: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in rows(EVIDENCE):
        if edge["review_state"] == "VALIDATED":
            evidence_by_tag[edge["subject_key"]].append(edge)
    accepted_by_root: dict[str, set[str]] = defaultdict(set)
    for source in rows(SOURCE_REVIEWS):
        if source["review_status"] == "ACCEPTED":
            accepted_by_root[source["home_root"]].add(source["source_review_id"])

    output: list[dict[str, str]] = []
    for rank, (tag, count) in enumerate(cohort, 1):
        graph = graph_by_tag.get(tag, [])
        roots = {
            edge["object_key"] for edge in graph
            if edge["relation_type"] in {"DISCOVERY_HINT", "MEMBER_OF"}
        }
        bases = {
            edge["object_key"] for edge in graph if edge["relation_type"] == "VARIANT_OF"
        }
        tag_match = re.search(r"_\(([^()]*)\)$", tag)
        qualifier = tag_match.group(1) if tag_match else ""
        validated = [
            f"{edge['relation_type']}:{edge['object_key']}:{edge['evidence_id']}"
            for edge in evidence_by_tag.get(tag, [])
        ]
        source_ids = {
            source_id for root in roots for source_id in accepted_by_root.get(root, set())
        }
        previous = unresolved[tag]
        output.append({
            "rank": str(rank),
            "canonical_character": tag,
            "post_count": str(count),
            "previous_state": previous["final_state"],
            "previous_unresolved_reason": previous["reason_code"],
            "candidate_roots": stable(roots),
            "terminal_qualifier_surface": qualifier,
            "base_character_candidates": stable(bases),
            "variant_relation_candidates": stable({
                f"{edge['relation_type']}:{edge['object_key']}:{edge['review_state']}"
                for edge in graph if edge["relation_type"] == "VARIANT_OF"
            }),
            "existing_validated_relations": stable(validated),
            "accepted_source_reviews_at_candidate_roots": stable(source_ids),
            "proposed_home": "",
            "final_state": "PENDING_REVIEW",
            "authority_type": "",
            "source_url": "",
            "source_claim": "",
            "provenance": f"Frozen #180 baseline {BASELINE_COMMIT}; post_count from Issue #70 extraction snapshot 2026-09-02; candidates are non-authoritative hints.",
            "review_status": "UNREVIEWED",
        })

    manifest: dict[str, object] = {
        "schema_version": "issue216-top500-cohort-v1",
        "baseline_issue": 180,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_master_sha256": master_hash,
        "baseline_character_population": len(master),
        "baseline_home_confirmed": sum(row["final_state"] == "HOME_CONFIRMED" for row in master),
        "baseline_home_unresolved": len(unresolved),
        "post_count_snapshot_date": "2026-09-02",
        "post_count_source": "docs/issue70/data/source/character_copyright_evidence_full.csv.gz; character_post_count is frequency only, not HOME authority",
        "post_count_file_sha256": sha256(POST_COUNTS),
        "post_count_joined_unresolved": len(post_counts),
        "post_count_missing_unresolved": len(unresolved) - len(post_counts),
        "top_100_cutoff_posts": cohort[99][1],
        "top_500_cutoff_posts": cohort[499][1],
        "cohort_size": len(output),
        "cohort_order": "post_count descending, then canonical Character ascending",
        "candidate_source_policy": "candidate roots/qualifiers are hints only; no candidate is a HOME without exact validated authority",
    }
    return output, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify the frozen cohort against current local baseline inputs")
    args = parser.parse_args()
    if args.check:
        if not COHORT.exists() or not MANIFEST.exists():
            raise SystemExit("frozen cohort output is missing")
        generated, manifest = build()
        with COHORT.open(encoding="utf-8-sig", newline="") as stream:
            actual = list(csv.DictReader(stream))
        stored_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if actual != generated or stored_manifest != manifest:
            raise SystemExit("frozen top-500 cohort differs from deterministic reconstruction")
        print("top-500 cohort reproducibility: PASS")
        return
    if COHORT.exists() or MANIFEST.exists():
        raise SystemExit("refusing to overwrite frozen cohort; use --check or review the existing files")
    output, manifest = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with COHORT.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"frozen cohort rows: {len(output)}; top100 cutoff={manifest['top_100_cutoff_posts']}; top500 cutoff={manifest['top_500_cutoff_posts']}")


if __name__ == "__main__":
    main()
