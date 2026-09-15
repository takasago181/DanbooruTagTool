#!/usr/bin/env python3
"""Issue #97 Phase C: bounded combination-concept / recipe gap audit.

Read-only audit. It does not mutate Special, General, Issue #70, catalog.db, or UserData.
The intent inventory is deliberately product-focused: adult/fetish/niche body-site, insertion,
restraint, fluid, non-human/tentacle and R18G-adjacent discovery. Generic pose/style recipes
are intentionally out of scope.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ALLOWED = {"APPROVED_STATIC", "APPROVED_SEMANTIC_ROLE", "APPROVED_CORRECTION_METADATA"}

# Each slot contains preferred exact Special surfaces in priority order. The first accepted
# direct/semantic surface found is used. Alias-only/provisional/review rows are not recipe
# components because final output must not silently depend on unresolved identity handling.
INTENTS = [
    # anal / rectal + restraint / implement
    ("アナルビーズを使いながら拘束", "ANAL_RECTAL", [["anal beads"], ["bondage", "bound"]]),
    ("アナルテールを付けたまま拘束", "ANAL_RECTAL", [["anal tail"], ["bondage", "bound"]]),
    ("バットプラグを付けたまま拘束", "ANAL_RECTAL", [["butt plug"], ["bondage", "bound"]]),
    ("肛門にバイブを入れた状態で拘束", "ANAL_RECTAL", [["vibrator in anus"], ["bondage", "bound"]]),
    ("ペギングしながら手錠", "ANAL_RECTAL", [["pegging"], ["handcuffs"]]),
    ("ペギングしながら目隠し", "ANAL_RECTAL", [["pegging"], ["blindfold"]]),
    ("トリプルアナルで拘束", "ANAL_RECTAL", [["triple anal"], ["bondage", "bound"]]),
    ("アナルビーズと開いた肛門を同時に見せる", "ANAL_RECTAL", [["anal beads"], ["spread anus", "gaping"]]),
    ("アナルテールと開いた肛門を同時に見せる", "ANAL_RECTAL", [["anal tail"], ["spread anus", "gaping"]]),

    # urethral
    ("尿道ビーズを入れた状態で拘束", "URETHRAL", [["urethral beads"], ["bondage", "bound"]]),
    ("尿道挿入しながら目隠し", "URETHRAL", [["urethral insertion"], ["blindfold"]]),
    ("尿道フィンガリングしながら手錠", "URETHRAL", [["urethral fingering"], ["handcuffs"]]),
    ("尿道ペネトレーションしながら拘束", "URETHRAL", [["urethral penetration"], ["bondage", "bound"]]),
    ("カテーテルを使った状態で拘束", "URETHRAL", [["catheter"], ["bondage", "bound"]]),
    ("尿道内射精と拘束を同時に指定", "URETHRAL", [["cum in urethra"], ["bondage", "bound"]]),

    # restraint implements / poses / stimulation
    ("ボールギャグと手錠を同時に使う", "BDSM_RESTRAINT", [["ball gag"], ["handcuffs"]]),
    ("ボールギャグと目隠しを同時に使う", "BDSM_RESTRAINT", [["ball gag"], ["blindfold"]]),
    ("ディルドギャグと手錠を同時に使う", "BDSM_RESTRAINT", [["dildo gag"], ["handcuffs"]]),
    ("手錠と目隠しを同時に使う", "BDSM_RESTRAINT", [["handcuffs"], ["blindfold"]]),
    ("手錠と足首拘束を同時に使う", "BDSM_RESTRAINT", [["handcuffs"], ["bound ankles"]]),
    ("両腕を離して拘束しボールギャグ", "BDSM_RESTRAINT", [["arms bound apart"], ["ball gag"]]),
    ("拘束状態で鞭を使う", "BDSM_RESTRAINT", [["bound", "bondage"], ["whip"]]),
    ("拘束状態でフロッガーを使う", "BDSM_RESTRAINT", [["bound", "bondage"], ["flogger"]]),
    ("拘束状態で木馬を使う", "BDSM_RESTRAINT", [["bound", "bondage"], ["wooden horse"]]),
    ("乳首へのバイブ刺激と手錠", "BREAST_NIPPLE", [["vibrator on nipple"], ["handcuffs"]]),
    ("乳首いじりと拘束", "BREAST_NIPPLE", [["nipple tweak"], ["bondage", "bound"]]),

    # fluids / excretion + constraint / site
    ("女性射精と拘束を同時に指定", "FLUID_EXCRETION", [["female ejaculation"], ["bondage", "bound"]]),
    ("膣内射精と拘束を同時に指定", "FLUID_EXCRETION", [["cum in pussy"], ["bondage", "bound"]]),
    ("胸への射精と拘束を同時に指定", "FLUID_EXCRETION", [["cum on breasts"], ["bondage", "bound"]]),
    ("ぶっかけと拘束を同時に指定", "FLUID_EXCRETION", [["bukkake"], ["bondage", "bound"]]),
    ("内部射精と目隠しを同時に指定", "FLUID_EXCRETION", [["internal cumshot"], ["blindfold"]]),
    ("放屁フェチ表現と拘束を同時に指定", "FLUID_EXCRETION", [["fart"], ["bondage", "bound"]]),

    # non-human / tentacle
    ("触手セックスと拘束を同時に指定", "NONHUMAN_TENTACLE", [["tentacle sex"], ["bondage", "bound"]]),
    ("触手オナニーと拘束を同時に指定", "NONHUMAN_TENTACLE", [["tentacle masturbation"], ["bondage", "bound"]]),
    ("触手ディルドと拘束を同時に指定", "NONHUMAN_TENTACLE", [["tentacle dildo"], ["bondage", "bound"]]),
    ("膣への触手表現と拘束を同時に指定", "NONHUMAN_TENTACLE", [["pussy tentacle"], ["bondage", "bound"]]),
    ("男性器への触手表現と拘束を同時に指定", "NONHUMAN_TENTACLE", [["penis tentacle", "tentacle on penis"], ["bondage", "bound"]]),
    ("口内触手と目隠しを同時に指定", "NONHUMAN_TENTACLE", [["tentacle in mouth"], ["blindfold"]]),
    ("触手に掴まれた状態でボールギャグ", "NONHUMAN_TENTACLE", [["grabbed by tentacles"], ["ball gag"]]),
    ("機械触手と拘束を同時に指定", "NONHUMAN_TENTACLE", [["mechanical tentacles"], ["bondage", "bound"]]),
    ("首に巻き付く触手と拘束を同時に指定", "NONHUMAN_TENTACLE", [["tentacle around neck"], ["bondage", "bound"]]),
    ("多数の触手と目隠しを同時に指定", "NONHUMAN_TENTACLE", [["multiple tentacles"], ["blindfold"]]),

    # body state / extreme / damage-adjacent
    ("開いた状態とアナルビーズを同時に指定", "BODY_STATE_EXTREME", [["gaping"], ["anal beads"]]),
    ("脱出・突出状態と拘束を同時に指定", "BODY_STATE_EXTREME", [["prolapse"], ["bondage", "bound"]]),
    ("極端なストレッチとアナルビーズを同時に指定", "BODY_STATE_EXTREME", [["extreme stretching"], ["anal beads"]]),
    ("切断表現と拘束を同時に指定", "R18G_DAMAGE", [["amputee"], ["bondage", "bound"]]),

    # multi-actor / relation-heavy adult states
    ("複数人の性行為と目隠しを同時に指定", "MULTI_ACTOR", [["teamwork (sexual)"], ["blindfold"]]),
    ("協力手コキと拘束を同時に指定", "MULTI_ACTOR", [["cooperative handjob"], ["bondage", "bound"]]),
    ("協力足コキと拘束を同時に指定", "MULTI_ACTOR", [["cooperative footjob"], ["bondage", "bound"]]),
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower().replace("_", " "))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--expected-special", type=int, default=2983)
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(args.profile, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    ids = [int(r["SpecialID"]) for r in rows]
    if len(rows) != args.expected_special or ids != list(range(1, args.expected_special + 1)):
        raise SystemExit(f"Special identity closure mismatch: rows={len(rows)} range={ids[:1]}..{ids[-1:]}")

    by_norm = {norm(r["Tag"]): r for r in rows}

    candidates = []
    rejected = []
    for n, (intent_ja, domain, slot_options) in enumerate(INTENTS, 1):
        resolved = []
        missing = []
        for options in slot_options:
            chosen = None
            for option in options:
                r = by_norm.get(norm(option))
                if r and r["PromotionStatus"] in ALLOWED:
                    chosen = r
                    break
            if chosen is None:
                missing.append(" | ".join(options))
            else:
                resolved.append(chosen)

        if missing:
            rejected.append({
                "audit_id": f"C{n:03d}", "intent_ja": intent_ja, "domain": domain,
                "decision": "HOLD_MISSING_ACCEPTED_COMPONENT", "details": "; ".join(missing),
            })
            continue

        # If one accepted Special surface already lexically contains every component surface,
        # the intent is not a recipe gap; route it away for manual confirmation.
        component_norms = [norm(r["Tag"]) for r in resolved]
        covering = []
        for r in rows:
            if r["PromotionStatus"] not in ALLOWED:
                continue
            t = norm(r["Tag"])
            if all(c in t or t in c for c in component_norms):
                covering.append(r["Tag"])
        if covering:
            rejected.append({
                "audit_id": f"C{n:03d}", "intent_ja": intent_ja, "domain": domain,
                "decision": "ROUTE_EXISTING_SPECIAL_REVIEW", "details": " | ".join(sorted(set(covering))[:8]),
            })
            continue

        tags = [r["Tag"] for r in resolved]
        ids_resolved = [r["SpecialID"] for r in resolved]
        families = [r["GenerationFamily"] for r in resolved]
        candidates.append({
            "audit_id": f"C{n:03d}",
            "intent_ja": intent_ja,
            "domain": domain,
            "route": "COMBINATION_RECIPE_CANDIDATE",
            "canonical_components": " + ".join(tags),
            "special_ids": " + ".join(ids_resolved),
            "recipe_prompt": ", ".join(tags),
            "generation_families": " + ".join(families),
            "model_scope": "MODEL_NEUTRAL_IDENTITY_ONLY; EFFECTIVENESS_NOT_CERTIFIED",
            "ordering_or_weighting": "NONE_ASSUMED",
            "why_not_single_canonical": "No accepted single Special surface mechanically covers all resolved components; requires human product-fit review.",
            "source_evidence": "accepted Special generation profile + Issue #97 Phase C product-intent inventory",
            "review_status": "REVIEW_REQUIRED",
        })

    def write_csv(path: Path, data: list[dict]):
        if not data:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)

    write_csv(out / "phase_c_candidate_queue_v1.csv", candidates)
    write_csv(out / "phase_c_routed_or_held_v1.csv", rejected)
    summary = {
        "mode": "ISSUE97_PHASE_C_BOUNDED_DISCOVERY_V1",
        "special_rows": len(rows),
        "intent_inventory": len(INTENTS),
        "candidate_total": len(candidates),
        "routed_or_held_total": len(rejected),
        "domains": {},
        "production_mutation": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "general_reaudit": "NO",
        "phase_b_auto_promotion": "NO",
        "pseudo_canonical_created": "NO",
        "content_filter_used": "NO",
        "generic_prompt_recipe_scope": "EXCLUDED",
    }
    for r in candidates:
        summary["domains"][r["domain"]] = summary["domains"].get(r["domain"], 0) + 1
    (out / "phase_c_summary_v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
