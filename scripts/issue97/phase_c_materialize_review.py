#!/usr/bin/env python3
"""Materialize the bounded human/product review for Issue #97 Phase C.

The mechanical queue is intentionally broader than the final set. This pass rejects trivial
independent tag stacking and keeps only combinations where components materially share a
body-site, topology, target/destination, actor relation, or pose/equipment structure.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

DIRECT = {"APPROVED_STATIC", "APPROVED_CORRECTION_METADATA"}
KEEP_RAW = {"C008", "C009"}

# Additional structural combinations identified while reviewing the first-pass queue.
# All components must resolve to direct accepted Special surfaces; semantic-support-only
# surfaces are not emitted as Prompt recipes.
SUPPLEMENTAL = [
    ("S001", "アナルフックを使いながら肛門を開いた状態にする", "ANAL_RECTAL", ["anal hook", "spread anus"], "same body-site implement + visible body-state"),
    ("S002", "バットプラグを付けながら肛門を開いた状態にする", "ANAL_RECTAL", ["butt plug", "spread anus"], "same body-site implement + visible body-state"),
    ("S003", "肛門内バイブと開いた肛門を同時に見せる", "ANAL_RECTAL", ["vibrator in anus", "spread anus"], "same body-site implement placement + visible body-state"),
    ("S004", "触手に体を掴まれながら口にも触手が入っている", "NONHUMAN_TENTACLE", ["grabbed by tentacles", "tentacle in mouth"], "shared non-human actor with two explicit target relations"),
    ("S005", "機械触手に体を掴まれている", "NONHUMAN_TENTACLE", ["mechanical tentacles", "grabbed by tentacles"], "actor morphology + actor-target relation"),
    ("S006", "膣に触手があり同時に触手に体を掴まれている", "NONHUMAN_TENTACLE", ["pussy tentacle", "grabbed by tentacles"], "body-site relation + shared non-human actor relation"),
    ("S007", "男性器に触手があり同時に触手に体を掴まれている", "NONHUMAN_TENTACLE", ["penis tentacle", "grabbed by tentacles"], "body-site relation + shared non-human actor relation"),
    ("S008", "触手セックス中に触手に体を掴まれている", "NONHUMAN_TENTACLE", ["tentacle sex", "grabbed by tentacles"], "sexual action + shared non-human actor relation"),
    ("S009", "首に触手が巻き付き口にも触手が入っている", "NONHUMAN_TENTACLE", ["tentacle around neck", "tentacle in mouth"], "two explicit body-site relations for the same non-human implement class"),
    ("S010", "木馬を使い両腕を離して拘束する", "BDSM_RESTRAINT", ["wooden horse", "arms bound apart"], "restraint equipment + posture/spatial restraint structure"),
    ("S011", "乳首にバイブを当てながら乳首をつまむ", "BREAST_NIPPLE", ["vibrator on nipple", "nipple tweak"], "two concurrent actions bound to the same body-site"),
    ("S012", "ぶっかけで特に胸への射精を指定する", "FLUID_EXCRETION", ["bukkake", "cum on breasts"], "fluid pattern + explicit destination/body-site"),
    ("S013", "尿道ビーズが入った状態で尿道内射精も指定する", "URETHRAL", ["urethral beads", "cum in urethra"], "implement placement + fluid destination on the same body-site"),
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower().replace("_", " "))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-dir", required=True)
    ap.add_argument("--profile", required=True)
    args = ap.parse_args()
    root = Path(args.audit_dir)

    with open(args.profile, encoding="utf-8-sig", newline="") as f:
        profile = list(csv.DictReader(f))
    by_tag = {norm(r["Tag"]): r for r in profile}
    raw = list(csv.DictReader((root / "phase_c_candidate_queue_v1.csv").open(encoding="utf-8")))

    accepted: list[dict] = []
    rejected: list[dict] = []

    for r in raw:
        if r["audit_id"] in KEEP_RAW:
            r2 = dict(r)
            r2["route"] = "COMBINATION_RECIPE_REVIEW_CANDIDATE"
            r2["review_status"] = "CANDIDATE"
            r2["product_fit_reason"] = "Components materially share the same body-site; this is not merely independent modifier stacking."
            accepted.append(r2)
        else:
            reason = "REJECT_TRIVIAL_INDEPENDENT_STACK"
            if r["audit_id"] == "C043":
                reason = "REJECT_DUPLICATE_INTENT_C008"
            elif r["audit_id"] == "C045":
                reason = "REJECT_SEMANTIC_SUPPORT_AS_DIRECT_RECIPE_COMPONENT"
            rejected.append({
                "audit_id": r["audit_id"], "intent_ja": r["intent_ja"], "domain": r["domain"],
                "canonical_components": r["canonical_components"], "decision": reason,
                "reason": "Phase C must not become an unbounded Cartesian prompt-combination library; independent restraint/visibility/accessory stacking remains discoverable by selecting tags separately.",
            })

    for aid, intent, domain, tags, fit_reason in SUPPLEMENTAL:
        rs = []
        for tag in tags:
            r = by_tag.get(norm(tag))
            if not r or r["PromotionStatus"] not in DIRECT:
                raise SystemExit(f"Supplemental component is not a direct accepted Special surface: {tag}")
            rs.append(r)
        accepted.append({
            "audit_id": aid,
            "intent_ja": intent,
            "domain": domain,
            "route": "COMBINATION_RECIPE_REVIEW_CANDIDATE",
            "canonical_components": " + ".join(tags),
            "special_ids": " + ".join(r["SpecialID"] for r in rs),
            "recipe_prompt": ", ".join(tags),
            "generation_families": " + ".join(r["GenerationFamily"] for r in rs),
            "model_scope": "MODEL_NEUTRAL_IDENTITY_ONLY; EFFECTIVENESS_NOT_CERTIFIED",
            "ordering_or_weighting": "NONE_ASSUMED",
            "why_not_single_canonical": "No single accepted direct Special surface in the audited baseline expresses the full reviewed structural intent.",
            "source_evidence": "accepted Special generation profile + Issue #97 Phase C product-value review",
            "review_status": "CANDIDATE",
            "product_fit_reason": fit_reason,
        })

    # Exact duplicate intent/component guards.
    seen_intent, seen_components = set(), set()
    for r in accepted:
        ni = norm(r["intent_ja"])
        nc = tuple(sorted(norm(x) for x in r["canonical_components"].split(" + ")))
        if ni in seen_intent or nc in seen_components:
            raise SystemExit(f"duplicate final Phase C candidate: {r['audit_id']}")
        seen_intent.add(ni); seen_components.add(nc)

    def write(path: Path, rows: list[dict]):
        with path.open("w", encoding="utf-8", newline="") as f:
            if not rows:
                return
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)

    write(root / "phase_c_candidate_subset_v1.csv", accepted)
    write(root / "phase_c_rejected_ledger_v1.csv", rejected)
    counts = {}
    for r in accepted:
        counts[r["domain"]] = counts.get(r["domain"], 0) + 1
    summary = {
        "mode": "ISSUE97_PHASE_C_PRODUCT_REVIEW_V1",
        "raw_candidate_total": len(raw),
        "final_candidate_total": len(accepted),
        "rejected_total": len(rejected),
        "final_domain_counts": counts,
        "review_principle": "retain shared-body-site/topology/target-destination/actor-relation/pose-equipment structural combinations; reject trivial independent stacking",
        "recipe_components_direct_accepted_only": "YES",
        "automatic_production_integration": "NO",
        "production_mutation": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "content_filter_used": "NO",
    }
    (root / "phase_c_product_review_summary_v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
