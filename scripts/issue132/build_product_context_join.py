from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path

EXPECTED = 31_003


def norm(value: str) -> str:
    return "_".join((value or "").strip().lower().replace("_", " ").split())


def has_japanese_text(value: str) -> bool:
    return any("\u3040" <= ch <= "\u30ff" or "\u3400" <= ch <= "\u9fff" for ch in value)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def parse_surfaces(value: str) -> list[str]:
    if not value:
        return []
    for parser in (json.loads,):
        try:
            parsed = parser(value)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
    return [x.strip(" []'\"") for x in re.split(r"[|;]", value) if x.strip(" []'\"")]


def json_list(value: str) -> list[str]:
    parsed = json.loads(value or "[]")
    if not isinstance(parsed, list) or any(not isinstance(x, str) for x in parsed):
        raise ValueError("expected JSON string array")
    return parsed


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--effective-ledger", required=True)
    ap.add_argument("--current-audit", required=True)
    ap.add_argument("--intent", required=True)
    ap.add_argument("--catalog-db", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    effective_path = Path(args.effective_ledger)
    current_path = Path(args.current_audit)
    intent_path = Path(args.intent)
    db_path = Path(args.catalog_db)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pass_a_manifest_path = Path("docs/issue132/parallel/pass_a_contract_manifest_v1.json")
    finalizer_report_path = Path("docs/issue132/final-audit/FINALIZER_REPORT.json")
    final_apply_path = Path("docs/issue132/final-audit/FINAL_APPLY_REPORT.json")
    pass_a_manifest = json.loads(pass_a_manifest_path.read_text(encoding="utf-8"))
    finalizer_report = json.loads(finalizer_report_path.read_text(encoding="utf-8"))
    final_apply = json.loads(final_apply_path.read_text(encoding="utf-8"))
    if pass_a_manifest.get("population") != EXPECTED or pass_a_manifest.get("neutral", {}).get("identity_count") != EXPECTED:
        raise SystemExit("frozen Pass-A manifest does not pin the complete identity population")
    if finalizer_report.get("status") != "PASS" or finalizer_report.get("semantic_final_audit") != "PASS":
        raise SystemExit("final semantic audit is not PASS")
    if final_apply.get("final_semantic_qa_status") != "FINAL_SEMANTIC_QA_PASSED" or final_apply.get("full_structural_validator", {}).get("accepted") != EXPECTED:
        raise SystemExit("final semantic application report is incomplete")

    runtime_manifest_path = db_path.parent.parent / "runtime-manifest.json"
    if not runtime_manifest_path.is_file():
        raise SystemExit("current runtime-manifest.json is missing next to the catalog")
    runtime_manifest = json.loads(runtime_manifest_path.read_text(encoding="utf-8"))
    actual_db_sha256 = file_sha(db_path)
    if runtime_manifest.get("catalog_sha256", "").lower() != actual_db_sha256:
        raise SystemExit("runtime catalog hash does not match runtime-manifest.json")
    exe_path = runtime_manifest_path.parent / "DanbooruTagTool.exe"
    if not exe_path.is_file() or runtime_manifest.get("exe_sha256", "").lower() != file_sha(exe_path):
        raise SystemExit("runtime executable hash does not match runtime-manifest.json")

    # The reconciliation helper lives on the completed research branch; assert
    # every tracked product input it consumes is byte-identical to fetched live main.
    source_paths = {
        "docs/issue64/production_candidate/effective_sidecar.csv",
        "docs/issue64/production_candidate/general_taxonomy.json",
        "docs/issue118/production_candidate/sexual_intent_v2.csv",
        "src/DanbooruTagTool.Core/UnifiedBrowse.cs",
        "src/DanbooruTagTool.Core/SpecialBrowseV2.cs",
        "src/DanbooruTagTool.Data/UnifiedBrowseData/special_route_overrides_v1.csv",
        "src/DanbooruTagTool.Data/Issue56Inputs.cs",
        "src/DanbooruTagTool.Data/Issue76Data/issue76_chastity_control_patch_v0_4.csv",
        "src/DanbooruTagTool.Data/Issue76Data/issue76_v1_unresolved_audit_v0_5.csv",
        "src/DanbooruTagTool.Data/Issue76Data/issue76_practical_generation_patch_v0_6.csv",
        "docs/issue96/special_expansion_promotion_proposal_v1.csv",
        "docs/issue107/promotion_metadata_v1.csv",
    }
    issue56_inputs = Path("src/DanbooruTagTool.Data/Issue56Inputs.cs").read_text(encoding="utf-8")
    source_paths.update(re.findall(r'\["([^\"]+\.csv)"\]\s*=\s*"[0-9a-f]+"', issue56_inputs))
    main_blobs = {}
    for rel in sorted(source_paths):
        local_blob = subprocess.run(["git", "hash-object", "--", rel], check=True, capture_output=True, text=True).stdout.strip()
        remote_blob = subprocess.run(["git", "rev-parse", f"origin/main:{rel}"], check=True, capture_output=True, text=True).stdout.strip()
        if local_blob != remote_blob:
            raise SystemExit(f"product input differs from fetched live origin/main: {rel}")
        main_blobs[rel] = remote_blob

    semantic = read_jsonl(effective_path)
    current = read_csv(current_path)
    intent = read_csv(intent_path)
    for name, rows in (("semantic", semantic), ("current product audit", current), ("#118 intent", intent)):
        if len(rows) != EXPECTED:
            raise SystemExit(f"{name} population mismatch: {len(rows)} != {EXPECTED}")
    sem_by = {r["identity_key"]: r for r in semantic}
    cur_by = {r["identity_key"]: r for r in current}
    int_by = {r["identity_key"]: r for r in intent}
    if any(len(x) != EXPECTED for x in (sem_by, cur_by, int_by)):
        raise SystemExit("duplicate identity_key in an input")
    if sem_by.keys() != cur_by.keys() or sem_by.keys() != int_by.keys():
        raise SystemExit("the semantic, product, and #118 identity sets do not match")
    for key in sem_by:
        current_intent = int_by[key].get("sexual_intent", "") or "UNCLASSIFIED"
        if sem_by[key].get("issue118_content_intent", "") != current_intent:
            raise SystemExit(f"Pass-A/#118 content-intent mismatch at {key}")
        if sem_by[key].get("semantic_contract_id") != "issue132-pass-a-semantic-contract-v2":
            raise SystemExit(f"frozen Pass-A semantic contract mismatch at {key}")

    # Runtime catalog is opened read-only and only its serialized catalog table is read.
    connection = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    catalog_by_surface: dict[str, list[dict]] = defaultdict(list)
    catalog_count = 0
    runtime_source_hashes = {}
    metadata_row = connection.execute("SELECT provenance FROM metadata LIMIT 1").fetchone()
    if metadata_row is None:
        raise SystemExit("runtime catalog provenance metadata is missing")
    try:
        runtime_source_hashes = json.loads(metadata_row["provenance"])
    except Exception as e:
        raise SystemExit(f"runtime catalog provenance is invalid: {e}")
    expected_source_hashes = {
        "docs/issue64/production_candidate/effective_sidecar.csv": "a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9",
        "docs/issue118/production_candidate/sexual_intent_v2.csv": "d2966dbc3c70617af2a985a94f81650785a29c1668b40b582d3c213ef2a68bc0",
        "data/runtime/japanese_overlay.json": "999b42fa76e036ad79f68ef7cd3ff958c94bd42c08ab00dd0394898d0205de76",
        "data/generation/special2788_generation_profile.csv": "1f954cea fc8c87cd44ecde8ff74218de33e63124e002c7e9031a8edf3c00bd9e".replace(" ", ""),
    }
    for source, expected in expected_source_hashes.items():
        if runtime_source_hashes.get(source, "").lower() != expected:
            raise SystemExit(f"runtime catalog provenance mismatch at {source}")
    for row in connection.execute("SELECT canonical,payload FROM entries"):
        payload = json.loads(row["payload"])
        if payload.get("EffectiveCategory") not in {"General", "Special"}:
            continue
        catalog_count += 1
        # Reference-only Special rows intentionally have no runtime Canonical;
        # their stable search surface is the source English name.
        key = norm(payload.get("Canonical") or payload.get("English") or row["canonical"] or "")
        if key:
            catalog_by_surface[key].append(payload)
    connection.close()

    product_by: dict[str, dict] = {}
    missing_catalog = []
    for key, intent_row in int_by.items():
        surfaces = {norm(key)} | {norm(x) for x in parse_surfaces(intent_row.get("source_identities", ""))}
        entries: dict[str, dict] = {}
        for surface in surfaces:
            for payload in catalog_by_surface.get(surface, []):
                entries[payload.get("Id", payload.get("Canonical", ""))] = payload
        if not entries:
            missing_catalog.append(key)
            continue
        values = list(entries.values())
        names = sorted({x for p in values for x in [str(p.get("Canonical", "")), str(p.get("English", ""))] if x})
        japanese = sorted({str(p.get("Japanese", "")).strip() for p in values if str(p.get("Japanese", "")).strip()})
        japanese_search = sorted({str(x).strip() for p in values for x in p.get("JapaneseSearch", []) if str(x).strip()})
        japanese_search_native = [x for x in japanese_search if has_japanese_text(x)]
        aliases = sorted({str(x).strip() for p in values for x in p.get("Aliases", []) if str(x).strip()})
        usage = sorted({int(p.get("Usage", 0) or 0) for p in values})
        product_by[key] = {
            "catalog_entry_ids": sorted(entries),
            "catalog_backing_count": len(entries),
            "catalog_can_browse": any(bool(p.get("CanBrowse")) for p in values),
            "catalog_can_search": any(bool(p.get("CanSearch")) for p in values),
            "canonical_surfaces": names,
            "display_ja": japanese,
            "search_ja": japanese_search,
            "aliases": aliases,
            "usage_values": usage,
            "search_surface_count": len(set(names + japanese + japanese_search + aliases)),
            "has_japanese_display": any(has_japanese_text(x) for x in japanese),
            "has_japanese_search": bool(japanese_search_native),
            "japanese_search_native": japanese_search_native,
            "has_alias": bool(aliases),
        }
    if missing_catalog:
        raise SystemExit(f"runtime catalog join missing {len(missing_catalog)} identities: {missing_catalog[:20]}")

    # Freeze the original deterministic Pass-B builder's exact population join.
    pass_a_fields = [
        "review_seq", "identity_key", "manual_seen", "semantic_summary_ja", "discovery_mode",
        "route_1_id", "route_1_strength", "route_1_reason_ja", "route_2_id", "route_2_strength",
        "route_2_reason_ja", "route_3_id", "route_3_strength", "route_3_reason_ja",
        "local_refinement_ids", "body_site_ids", "theme_ids", "route_vocabulary_gap",
        "route_vocabulary_gap_note", "review_depth", "evidence_urls", "uncertainty_note",
    ]
    flat_path = out / "effective_semantic_map_for_pass_b.csv"
    with flat_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=pass_a_fields, lineterminator="\n")
        writer.writeheader()
        for row in semantic:
            routes = [(x, "CORE") for x in row["core_routes"]] + [(x, "SUPPORTING") for x in row["supporting_routes"]]
            if len(routes) > 3:
                raise SystemExit(f"{row['identity_key']}: effective route count exceeds frozen contract")
            out_row = {name: "" for name in pass_a_fields}
            out_row.update({
                "review_seq": str(row["review_seq"]),
                "identity_key": row["identity_key"],
                "discovery_mode": row["discovery_mode"],
                "local_refinement_ids": json.dumps(row["local_refinements"], ensure_ascii=False, separators=(",", ":")),
                "body_site_ids": json.dumps(row["body_facets"], ensure_ascii=False, separators=(",", ":")),
                "theme_ids": json.dumps(row["theme_facets"], ensure_ascii=False, separators=(",", ":")),
                "route_vocabulary_gap": row["route_vocabulary_gap"],
                "review_depth": row["review_depth"],
            })
            for idx, (route, strength) in enumerate(routes, 1):
                out_row[f"route_{idx}_id"] = route
                out_row[f"route_{idx}_strength"] = strength
            writer.writerow(out_row)
    with flat_path.open("r", encoding="utf-8-sig", newline="") as f:
        parsed = list(csv.DictReader(f))
    if len(parsed) != EXPECTED or {r["identity_key"] for r in parsed} != sem_by.keys():
        raise SystemExit("Pass-B CSV serialization round-trip failed")

    import sys
    builder = Path(__file__).with_name("build_pass_b_diff.py")
    diff_path = out / "pass_b_full_diff.csv"
    summary_path = out / "pass_b_summary.json"
    subprocess.run([
        sys.executable, str(builder), "--pass-a", str(flat_path), "--current-audit", str(current_path),
        "--out", str(diff_path), "--summary", str(summary_path),
    ], check=True)

    with diff_path.open("r", encoding="utf-8-sig", newline="") as f:
        diff_rows = list(csv.DictReader(f))
    diff_by = {r["identity_key"]: r for r in diff_rows}
    product_fields = [
        "identity_key", "discovery_mode", "issue118_content_intent", "is_general", "is_special",
        "membership", "browseable_before", "current_routes", "luna_core_routes", "luna_supporting_routes",
        "missing_core_routes", "missing_supporting_routes", "current_routes_not_reproduced",
        "general_paths", "current_local_refinements", "missing_local_refinements",
        "current_body_sites", "missing_body_sites", "current_themes", "missing_themes",
        "route_vocabulary_gap", "diff_flags", "catalog_entry_ids", "catalog_backing_count",
        "display_ja", "search_ja", "aliases", "canonical_surfaces", "usage_values",
        "has_japanese_display", "has_japanese_search", "has_alias", "search_surface_level",
        "search_surface_count", "bucket", "review_signals",
        "provisional_disposition", "provisional_reason",
    ]
    ledger_path = out / "product_reconciliation_ledger.csv"
    with ledger_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=product_fields, lineterminator="\n")
        writer.writeheader()
        for key in sem_by:
            sem = sem_by[key]
            cur = cur_by[key]
            intent_row = int_by[key]
            prod = product_by[key]
            d = diff_by[key]
            general = intent_row.get("is_general", "NO") == "YES"
            special = intent_row.get("is_special", "NO") == "YES"
            membership = "OVERLAP" if general and special else "GENERAL_ONLY" if general else "SPECIAL_ONLY" if special else "NEITHER"
            missing_routes = json_list(d["missing_core_routes"]) + json_list(d["missing_supporting_routes"])
            browseable = bool(
                json_list(d["current_routes"])
                or json_list(d["current_body_sites"])
                or json_list(d["current_themes"])
            ) and prod["catalog_can_browse"]
            flags = json_list(d["diff_flags"])
            if sem["discovery_mode"] == "SEMANTIC_UNRESOLVED":
                disposition, reason = "SEMANTIC_UNRESOLVED", "Pass-A state is explicitly unresolved."
            elif sem["discovery_mode"] == "SEARCH_ORIENTED":
                disposition, reason = "SEARCH_ONLY", "Pass-A says this identity is search-oriented."
            elif not browseable and missing_routes:
                disposition, reason = "UPSTREAM_REVIEW", "Identity is not browseable in the current product; #132 cannot add its first route."
            elif d["missing_local_refinements"] != "[]":
                disposition, reason = "UPSTREAM_REVIEW", "Local refinement ownership remains with #64."
            elif d["current_routes_not_reproduced"] != "[]":
                disposition, reason = "UPSTREAM_REVIEW", "Current primary/secondary route authority needs owner review."
            elif sem["route_vocabulary_gap"] == "YES":
                disposition, reason = "UPSTREAM_REVIEW", "Route-vocabulary gaps are default-deny for the #132 overlay."
            elif missing_routes:
                disposition, reason = "PENDING_PRODUCT_VALUE_REVIEW", "Browseable identity has missing natural route(s); assess search redundancy, alternate paths, narrowing, and shelf coherence."
            else:
                disposition, reason = "SEARCH_ONLY", "No eligible missing route remains after the deterministic diff."
            writer.writerow({
                "identity_key": key,
                "discovery_mode": sem["discovery_mode"],
                "issue118_content_intent": intent_row.get("sexual_intent", "") or "UNCLASSIFIED",
                "is_general": intent_row.get("is_general", ""),
                "is_special": intent_row.get("is_special", ""),
                "membership": membership,
                "browseable_before": "YES" if browseable else "NO",
                "current_routes": d["current_routes"],
                "luna_core_routes": d["luna_core_routes"],
                "luna_supporting_routes": d["luna_supporting_routes"],
                "missing_core_routes": d["missing_core_routes"],
                "missing_supporting_routes": d["missing_supporting_routes"],
                "current_routes_not_reproduced": d["current_routes_not_reproduced"],
                "general_paths": cur.get("general_paths", ""),
                "current_local_refinements": d["current_local_refinements"],
                "missing_local_refinements": d["missing_local_refinements"],
                "current_body_sites": d["current_body_sites"],
                "missing_body_sites": d["missing_body_sites"],
                "current_themes": d["current_themes"],
                "missing_themes": d["missing_themes"],
                "route_vocabulary_gap": sem["route_vocabulary_gap"],
                "diff_flags": d["diff_flags"],
                "catalog_entry_ids": json.dumps(prod["catalog_entry_ids"], ensure_ascii=False, separators=(",", ":")),
                "catalog_backing_count": prod["catalog_backing_count"],
                "display_ja": json.dumps(prod["display_ja"], ensure_ascii=False, separators=(",", ":")),
                "search_ja": json.dumps(prod["search_ja"], ensure_ascii=False, separators=(",", ":")),
                "aliases": json.dumps(prod["aliases"], ensure_ascii=False, separators=(",", ":")),
                "canonical_surfaces": json.dumps(prod["canonical_surfaces"], ensure_ascii=False, separators=(",", ":")),
                "usage_values": json.dumps(prod["usage_values"], separators=(",", ":")),
                "has_japanese_display": "YES" if prod["has_japanese_display"] else "NO",
                "has_japanese_search": "YES" if prod["has_japanese_search"] else "NO",
                "has_alias": "YES" if prod["has_alias"] else "NO",
                "search_surface_level": (
                    "JAPANESE_AND_ALIAS" if prod["has_japanese_search"] and prod["has_alias"] else
                    "JAPANESE" if prod["has_japanese_search"] else
                    "ALIAS" if prod["has_alias"] else "CANONICAL_ENGLISH_ONLY"
                ),
                "search_surface_count": prod["search_surface_count"],
                "bucket": cur.get("bucket", ""),
                "review_signals": cur.get("review_signals", ""),
                "provisional_disposition": disposition,
                "provisional_reason": reason,
            })

    manifest = {
        "schema_version": "issue132-product-context-join-v1",
        "population": EXPECTED,
        "semantic_head": "d74352be827c52a24888fbfc8bf71b8982627130",
        "live_main_head": "e5d0f7d954ff491c1a5661a0652e6142f2b0d08d",
        "runtime_catalog_main_commit": "45919734f6b03cb64e2269153e63f9a378b62691",
        "runtime_manifest_sha256": file_sha(runtime_manifest_path),
        "runtime_executable_sha256": file_sha(exe_path),
        "runtime_catalog_sha256": actual_db_sha256,
        "runtime_catalog_source_hashes": {key: runtime_source_hashes[key] for key in expected_source_hashes},
        "live_main_source_blob_ids": main_blobs,
        "live_main_source_count": len(main_blobs),
        "runtime_manifest_main_commit": runtime_manifest.get("main_commit"),
        "semantic_effective_ledger_sha256": file_sha(effective_path),
        "current_audit_path_sha256": file_sha(current_path),
        "issue118_sha256": file_sha(intent_path),
        "runtime_catalog_entries_read": catalog_count,
        "join_rule": "identity_key plus normalized #118 source_identities; exact catalog canonical match",
        "catalog_open_mode": "read-only",
        "missing_catalog_identity_count": len(missing_catalog),
        "product_decision_policy": "ownership constraints are deterministic; pending product-value rows require Pass C judgment",
    }
    (out / "product_context_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
