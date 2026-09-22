#!/usr/bin/env python3
"""Build complete Japanese human review for Issue #180 master v2."""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
MASTER = D / "CHARACTER_HOME_MASTER_V2.csv"
LEDGER = D / "APPLIED_AUTHORITY_LEDGER_V2.csv"
UNQUALIFIED = D / "UNQUALIFIED_WORK_QUEUE_V2.csv"
VARIANTS = D / "REMAINING_VARIANT_WORK_V2.csv"
DECISIONS_COMPAT = R / "docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
DECISIONS_DIR = R / "docs/issue180/autonomous/decisions"
OUT = A / "ISSUE180_ALL_35890_USER_REVIEW_V2.txt"
SUM = A / "issue180_all_35890_user_review_v2_summary.json"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def read_decisions():
    paths = [DECISIONS_COMPAT] if DECISIONS_COMPAT.exists() else []
    if DECISIONS_DIR.exists():
        paths.extend(sorted(DECISIONS_DIR.glob("*.csv")))
    rows = []
    for path in paths:
        for row in read(path):
            if not any((v or "").strip() for v in row.values()):
                continue
            rows.append({**row, "__source_file": str(path.relative_to(R))})
    return rows


def ja_reason(code: str) -> str:
    code = code or ""
    exact = {
        "DIRECT_CHARACTER_AUTHORITY": "Character単位のauthorityで本家HOMEを確認",
        "REUSABLE_FAMILY_QUALIFIER_AUTHORITY": "確認済みの作品qualifier family authorityを再利用してHOMEを確認",
        "REVIEWED_VARIANT_INHERITANCE": "公式variantとして確認し、base CharacterのHOMEを継承",
        "CONFLICTING_AUTHORITY": "強いauthority同士が矛盾しているため未確定",
        "EXPLICIT_CHARACTER_BLOCK": "明示的な保留指定があるため未確定",
        "VARIANT_BASE_HOME_NOT_CONFIRMED": "variantのbase Character側HOMEが未確定",
        "BASE_HOME_READY_OFFICIALITY_REVIEW": "base HOMEは確認済みだがvariant公式性の確認が必要",
        "BASE_EXISTS_HOME_PENDING": "base Characterは存在するがbase HOMEが未確定",
        "BASE_NOT_FOUND_OR_NONTRIVIAL": "安全にbase Characterを一意に決められない",
        "DIRECT_OFFICIALITY_REVIEW_REQUIRED": "#179で公式性が未確定のためCharacter単位の公式性確認が必要",
        "OFFICIALITY_REVIEW_REQUIRED_ISSUE179": "#179で公式性が未確定のためHOMEを自動確定しない",
        "ROSTER_DISCOVERY": "qualifierがないため公式/curated rosterによる所属確認が必要",
        "DIRECT_ROSTER_REVIEW": "roster候補があるためCharacter単位の確認が必要",
        "POLICY_DECISION_REQUIRED_PIAPRO": "Piapro/VOCALOIDのcanonical HOME policyが未決定",
        "HIGHER_REASONING_BROAD": "umbrella/広域familyのため追加のorigin/root確認が必要",
        "HIGHER_REASONING_NON_HOME_SEMANTICS": "コラボ/企画等でHOMEとして扱えない可能性が高いため追加確認が必要",
        "FAST_REVALIDATE_NORMALIZATION": "旧normalized rootを短時間で再確認する必要がある",
        "FAST_ROOT_POLICY_REVIEW": "個別作品とfranchise rootのどちらをHOMEにするか再確認が必要",
        "REVIEW_NORMALIZATION": "Copyright root normalizationの確認が必要",
        "DISCOVERY_RESEARCH": "安全なCopyright root候補の調査が必要",
        "NO_ACCEPTED_HOME_AUTHORITY": "受理可能なHOME authorityがまだない",
        "SECOND_REVIEWED_NOT_OFFICIAL": "second review済みの非公式Character判定",
    }
    if code in exact:
        return exact[code]
    if code.startswith("OFFICIALITY_REVIEW_REQUIRED_ISSUE179:"):
        return "#179で公式性が未確定/非公式系のため、family authorityだけではHOMEを付けない"
    if code.startswith("NEEDS_HIGHER_REASONING:"):
        return "上位reasoningでの追加確認が必要"
    return code or "理由未記録"


def decision_context(row):
    ref = (row.get("evidence_url") or "").strip()
    claim = (row.get("evidence_claim") or "").strip()
    if not ref and claim.startswith("REPO:"):
        ref = claim
    return {
        "scope": (row.get("scope") or "").strip(),
        "state": (row.get("validation_state") or "").strip(),
        "evidence_ref": ref or (row.get("__source_file") or "-"),
        "evidence_claim": claim or "-",
        "notes": (row.get("notes") or "").strip() or "-",
        "source_file": row.get("__source_file") or "-",
    }


def main():
    catalog = read(CAT)
    chars = {r["canonical_tag"]: r for r in catalog if r.get("category_name") == "Character"}
    copyrights = {r["canonical_tag"]: r for r in catalog if r.get("category_name") == "Copyright"}
    master = read(MASTER)
    ledger_rows = read(LEDGER)
    ledger = {r["canonical_tag"]: r for r in ledger_rows}
    unqualified = {r["canonical_tag"]: r for r in read(UNQUALIFIED)}
    variants = {r["canonical_tag"]: r for r in read(VARIANTS)}

    char_context = {}
    family_context = {}
    discovery_context = {}
    pattern_context = {}
    for d in read_decisions():
        scope = (d.get("scope") or "").strip()
        state = (d.get("validation_state") or "").strip()
        key = (d.get("key") or "").strip()
        if not key or state == "PENDING":
            continue
        ctx = decision_context(d)
        if scope == "FAMILY_QUALIFIER" and state in {"UNRESOLVED", "NEEDS_HIGHER_REASONING"}:
            family_context[key.lower()] = ctx
        elif scope == "DISCOVERY_GROUP" and state in {"UNRESOLVED", "NEEDS_HIGHER_REASONING"}:
            discovery_context[key.lower()] = ctx
        elif scope == "VARIANT_PATTERN" and state in {"UNRESOLVED", "NEEDS_HIGHER_REASONING"}:
            pattern_context[key] = ctx
        elif scope in {"DIRECT_CHARACTER", "VARIANT_CHARACTER", "BLOCK_CHARACTER"}:
            if state in {"UNRESOLVED", "NEEDS_HIGHER_REASONING", "PASS"}:
                char_context[key] = ctx

    review_context_count = 0
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("Issue #180 Character→本家Copyright 全35,890件 フリーズ前確認 v2\n")
        fh.write("research-only / production未変更 / HOMEは最大1件 / 未確定は推測で埋めない\n")
        fh.write("※ #179 origin と #180 HOME authority を分離表示。最終freezeにはユーザー確認が必要。\n")
        fh.write("※ 未確定でもgroup/pattern/family監査済みの場合は、その監査証拠をreview contextとして表示する。\n\n")
        for i, row in enumerate(master, 1):
            tag = row["canonical_tag"]
            cr = chars[tag]
            home = row.get("home_copyright", "")
            authority = ledger.get(tag, {})
            ja = (cr.get("display_ja") or tag).strip()
            home_ja = (copyrights.get(home, {}).get("display_ja") or home or "【未確定】").strip()
            state = row["final_state"]
            origin_class = row.get("origin_class", "") or "未監査"
            officiality = authority.get("officiality_state", "") or (
                origin_class if origin_class in {"OFFICIAL_IDENTITY", "OFFICIAL_ALIAS", "OFFICIAL_VARIANT"} else "未確定"
            )
            reason_code = row.get("decision_reason", "")
            evidence_ref = authority.get("evidence_url") or authority.get("source_provenance") or "-"
            evidence_claim = authority.get("evidence_claim") or "-"
            review_scope = "-"
            review_state = "-"
            review_note = "-"

            if state == "HOME_UNRESOLVED":
                ctx = char_context.get(tag)
                fam = (row.get("final_qualifier") or "").strip().lower()
                if ctx is None and fam:
                    ctx = family_context.get(fam)
                if ctx is None and tag in unqualified:
                    uq = unqualified[tag]
                    group = (
                        (uq.get("discovery_primary_root_hint") or "").strip()
                        or (uq.get("discovery_primary_raw") or "").strip()
                        or "__NO_DISCOVERY_HINT__"
                    )
                    ctx = discovery_context.get(group.lower())
                if ctx is None and tag in variants:
                    vr = variants[tag]
                    base_home = (vr.get("base_home_candidate") or "").strip()
                    outer = (vr.get("outer_ip_qualifier") or "").strip() or "-"
                    variant_q = (vr.get("variant_qualifier") or "").strip()
                    pattern_id = f"{base_home}::{outer}::{variant_q}"
                    ctx = pattern_context.get(pattern_id)
                if ctx is not None:
                    review_context_count += 1
                    review_scope = ctx["scope"]
                    review_state = ctx["state"]
                    review_note = ctx["notes"]
                    evidence_ref = ctx["evidence_ref"]
                    evidence_claim = ctx["evidence_claim"]

            unresolved = "-" if state != "HOME_UNRESOLVED" else reason_code
            fh.write(
                f"{i:05d}. {ja}\n"
                f"  Danbooru: {tag}\n"
                f"  qualifier/family: {row.get('final_qualifier') or '【なし】'}\n"
                f"  本家作品: {home_ja}\n"
                f"  Copyright tag: {home or '【未確定】'}\n"
                f"  判定: {state}\n"
                f"  #179 origin: {origin_class}\n"
                f"  公式性: {officiality}\n"
                f"  authority: {authority.get('authority_scope', '-')} / {authority.get('authority_type', '-')}\n"
                f"  理由: {ja_reason(reason_code)} [{reason_code}]\n"
                f"  review context: {review_scope} / {review_state}\n"
                f"  review note: {review_note}\n"
                f"  証拠参照: {evidence_ref}\n"
                f"  証拠内容: {evidence_claim}\n"
                f"  未確定理由: {unresolved}\n\n"
            )

    master_summary = json.load((D / "character_home_master_v2_summary.json").open(encoding="utf-8"))
    summary = {
        "character_rows": len(master),
        "states": master_summary["states"],
        "origin_class_counts": dict(Counter((r.get("origin_class") or "UNREVIEWED") for r in master)),
        "authority_scope_counts": dict(Counter(r.get("authority_scope", "") for r in ledger_rows)),
        "unresolved_rows_with_review_context": review_context_count,
        "user_review_required_before_freeze": True,
        "accepted_source_modified": False,
        "production_modified": False,
    }
    SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
