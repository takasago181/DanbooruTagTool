#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data/generation/special2788_generation_profile.csv"
BRIDGE = ROOT / "data/semantic/semantic_bridge_v1.csv"
OUTDIR = ROOT / "docs/knowledge/current/issue44_evaluator_coverage_20260910"
OUTDIR.mkdir(parents=True, exist_ok=True)

WD_REPO = "SmilingWolf/wd-eva02-large-tagger-v3"
WD_REV = "b25b82a03f7282e41aa2f257a52c7583b710bd1c"
KAGAMI_REPO = "Redstonexs/kagami-24k"
CL_REPO = "cella110n/cl_tagger_v2"
CL_REV = "v2_00"

CLASS_DIRECT = "DIRECT"
CLASS_ALIAS = "ALIAS_APPROX"
CLASS_COMPONENT = "COMPONENT_ONLY"
CLASS_HARD = "AUTO_EVAL_DIFFICULT"
CLASS_UNVERIFIED = "UNVERIFIED_GATED"

TRUE = {"1", "true", "yes", "y"}
REL_FLAG_WORDS = (
    "ACTOR", "TARGET", "BODY", "SPATIAL", "RELATION", "ASSIGN", "SEPARAT",
    "OWNERSHIP", "SOURCE", "DESTINATION", "TOPOLOGY", "CONNECT", "COUNT",
    "MULTI", "SIMULTAN", "LEFT", "RIGHT", "FRONT", "BACK", "UPPER", "LOWER",
)
REL_FAMILY_WORDS = (
    "MULTI_ACTOR", "INTERACTION", "INSERT", "RESTRAINT", "MACHINE", "DEVICE",
    "FLUID", "EXCRETION", "SOILING", "TENTACLE", "NONHUMAN", "GORE",
)
REL_TAG_PATTERNS = (
    r"\b(two|three|four|multiple|double|triple)\b",
    r"\b(left|right|front|behind|back|above|below|under|over)\b",
    r"\b(on|in|into|through|between|against|around|from|to)\b",
    r"\bwith\b",
)
STOP = {
    "a","an","the","of","to","in","on","at","by","for","with","from","and","or",
    "after","before","while","during","using","use","via","style","view","focus"
}


def norm(s: object) -> str:
    x = unicodedata.normalize("NFKC", str(s or "")).strip().casefold()
    x = x.replace("_", " ")
    x = re.sub(r"[()\[\]{}]", " ", x)
    x = re.sub(r"[^\w\s'/-]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def fetch_bytes(url: str, token: str = "") -> bytes:
    headers = {"User-Agent": "DanbooruTagTool-Issue44-Coverage/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def hf_model_sha(repo: str) -> str:
    data = json.loads(fetch_bytes(f"https://huggingface.co/api/models/{repo}").decode("utf-8"))
    return str(data["sha"])


def read_csv_vocab(raw: bytes) -> set[str]:
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise RuntimeError("empty CSV vocabulary")
    fields = rows[0].keys()
    name_col = next((c for c in ("name", "tag", "tag_name") if c in fields), None)
    if not name_col:
        raise RuntimeError(f"cannot find tag column in {list(fields)}")
    return {norm(r[name_col]) for r in rows if norm(r.get(name_col, ""))}


def read_cl_vocab(raw: bytes) -> set[str]:
    obj = json.loads(raw.decode("utf-8"))
    if isinstance(obj.get("tag_to_idx"), dict):
        return {norm(k) for k in obj["tag_to_idx"].keys() if norm(k)}
    if isinstance(obj.get("idx_to_tag"), dict):
        return {norm(v) for v in obj["idx_to_tag"].values() if norm(v)}
    raise RuntimeError("unexpected CL vocabulary schema")


def load_vocabularies() -> tuple[dict[str, set[str] | None], dict]:
    provenance = {}
    wd_url = f"https://huggingface.co/{WD_REPO}/resolve/{WD_REV}/selected_tags.csv?download=true"
    wd = read_csv_vocab(fetch_bytes(wd_url))
    provenance["WD14"] = {"repo": WD_REPO, "revision": WD_REV, "vocab_rows": len(wd), "status": "OK"}

    kagami_rev = hf_model_sha(KAGAMI_REPO)
    kagami_url = f"https://huggingface.co/{KAGAMI_REPO}/resolve/{kagami_rev}/selected_tags.csv?download=true"
    kagami = read_csv_vocab(fetch_bytes(kagami_url))
    provenance["Kagami"] = {"repo": KAGAMI_REPO, "revision": kagami_rev, "vocab_rows": len(kagami), "status": "OK"}

    token = os.environ.get("HF_TOKEN", "").strip()
    cl = None
    cl_status = "UNAVAILABLE_GATED"
    cl_error = ""
    try:
        cl_url = f"https://huggingface.co/{CL_REPO}/resolve/main/{CL_REV}/model_vocabulary.json?download=true"
        cl = read_cl_vocab(fetch_bytes(cl_url, token=token))
        cl_status = "OK"
    except Exception as e:  # do not pretend gated data was observed
        cl_error = f"{type(e).__name__}: {e}"
    provenance["CL"] = {
        "repo": CL_REPO,
        "revision": CL_REV,
        "vocab_rows": len(cl) if cl is not None else None,
        "status": cl_status,
        "error": cl_error,
        "authenticated": bool(token),
    }
    return {"WD14": wd, "Kagami": kagami, "CL": cl}, provenance


def bridge_terms() -> dict[int, list[str]]:
    out: dict[int, list[str]] = defaultdict(list)
    with BRIDGE.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            try:
                sid = int(r["special_id"])
            except Exception:
                continue
            for k in ("semantic_term", "en_concept", "candidate_canonical"):
                v = norm(r.get(k, ""))
                if v and v not in out[sid]:
                    out[sid].append(v)
    return out


def is_true(v: str) -> bool:
    return str(v or "").strip().casefold() in TRUE


def relation_needed(r: dict[str, str], tag: str) -> tuple[bool, list[str]]:
    reasons = []
    for col in (
        "ActorRequirementOverride", "BodypartRequirementOverride", "ImplementRequirementOverride",
        "PoseRequirementOverride", "CameraRequirementOverride", "SpatialAssignmentOverride",
    ):
        if is_true(r.get(col, "")):
            reasons.append(col)
    family = str(r.get("GenerationFamily", "")).upper()
    flags = str(r.get("SpecialFlags", "")).upper()
    if any(x in family for x in REL_FAMILY_WORDS):
        reasons.append(f"family:{family}")
    if any(x in flags for x in REL_FLAG_WORDS):
        reasons.append(f"flags:{flags}")
    nt = norm(tag)
    for pat in REL_TAG_PATTERNS:
        if re.search(pat, nt):
            reasons.append(f"lexical:{pat}")
    # Compound concepts are not assumed unary just because a single model label exists.
    if any(sep in nt for sep in (" and ", " + ", "/")):
        reasons.append("compound_lexical")
    return bool(reasons), reasons


def component_candidates(tag: str, aliases: list[str]) -> list[str]:
    values = [norm(tag)] + aliases
    cand = []
    for v in values:
        # split at common relation/composition connectors
        pieces = re.split(r"\b(?:and|with|on|in|into|through|between|against|around|from|to|by|using|after|before)\b|[/+]", v)
        for p in pieces:
            p = re.sub(r"\s+", " ", p).strip()
            toks = [t for t in p.split() if t not in STOP and len(t) > 1]
            if len(toks) >= 1:
                # whole piece and informative singletons are observation predicates, never semantic authority.
                if p and p != v:
                    cand.append(p)
                cand.extend(toks)
    return list(dict.fromkeys(x for x in cand if x))


def classify(vocab: set[str] | None, tag: str, aliases: list[str]) -> tuple[str, list[str]]:
    if vocab is None:
        return CLASS_UNVERIFIED, []
    t = norm(tag)
    if t in vocab:
        return CLASS_DIRECT, [t]
    hits = [a for a in aliases if a in vocab and a != t]
    if hits:
        return CLASS_ALIAS, hits[:8]
    comps = [c for c in component_candidates(tag, aliases) if c in vocab]
    # Require at least one multiword component or two distinct component tags to avoid declaring trivial word overlap useful.
    useful = [c for c in comps if " " in c]
    if useful or len(set(comps)) >= 2:
        return CLASS_COMPONENT, list(dict.fromkeys(comps))[:12]
    return CLASS_HARD, []


def final_recommend(classes: dict[str, str], rel: bool) -> tuple[str, bool, str]:
    verified = [v for v in classes.values() if v != CLASS_UNVERIFIED]
    any_directish = any(v in {CLASS_DIRECT, CLASS_ALIAS} for v in verified)
    any_component = any(v == CLASS_COMPONENT for v in verified)
    any_hard = any(v == CLASS_HARD for v in verified)
    if rel:
        if any_directish or any_component:
            return "REVIEW_REQUIRED", True, "relation/binding predicate requires human calibration"
        return "BLOCKED", True, "relation required and no useful verified vocabulary observation"
    if any_directish:
        # Candidate only. Real-image calibration still required before automatic Stage10 use.
        return "AUTO_CANDIDATE", False, "unary/non-relational vocabulary candidate; calibration pending"
    if any_component:
        return "REVIEW_REQUIRED", True, "only component predicates observable"
    if any_hard:
        return "BLOCKED", True, "no verified direct/alias/component observation"
    return "BLOCKED", True, "evaluator vocabulary unavailable"


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def choose_cases(rows: list[dict]) -> list[dict]:
    strata = [
        ("simple_unary", lambda r: r["final_recommendation"] == "AUTO_CANDIDATE" and r["relation_required"] == "false"),
        ("rare_or_no_vocab", lambda r: r["final_recommendation"] == "BLOCKED"),
        ("relation", lambda r: r["relation_required"] == "true"),
        ("alias_dependent", lambda r: "ALIAS_APPROX" in (r["wd14_class"], r["kagami_class"], r["cl_class"])),
        ("components_only", lambda r: "COMPONENT_ONLY" in (r["wd14_class"], r["kagami_class"], r["cl_class"])),
        ("bodypart", lambda r: "BodypartRequirementOverride" in r["relation_reasons"]),
        ("actor_subject_object", lambda r: "ActorRequirementOverride" in r["relation_reasons"] or "ACTOR" in r["relation_reasons"]),
        ("spatial", lambda r: "SpatialAssignmentOverride" in r["relation_reasons"] or "SPATIAL" in r["relation_reasons"]),
        ("count_or_multi", lambda r: any(x in r["relation_reasons"] for x in ("COUNT", "MULTI", "two", "three", "four"))),
        ("compound", lambda r: "compound_lexical" in r["relation_reasons"]),
    ]
    picked = []
    used = set()
    for name, pred in strata:
        candidates = [r for r in rows if pred(r) and r["special_id"] not in used]
        for r in candidates[:3]:
            used.add(r["special_id"])
            picked.append({
                "stratum": name,
                "special_id": r["special_id"],
                "canonical": r["canonical"],
                "final_recommendation": r["final_recommendation"],
                "why_selected": r["recommendation_reason"],
            })
    # ensure all outcome classes appear even if strata overlap
    for rec in ("AUTO_CANDIDATE", "REVIEW_REQUIRED", "BLOCKED"):
        for r in rows:
            if r["final_recommendation"] == rec and r["special_id"] not in used:
                used.add(r["special_id"])
                picked.append({"stratum": f"outcome_{rec.lower()}", "special_id": r["special_id"], "canonical": r["canonical"], "final_recommendation": rec, "why_selected": r["recommendation_reason"]})
                break
    return picked


def main():
    vocabs, provenance = load_vocabularies()
    aliases_by_id = bridge_terms()
    rows = []
    with PROFILE.open(encoding="utf-8-sig", newline="") as f:
        src = list(csv.DictReader(f))
    if len(src) != 2788 or len({r["SpecialID"] for r in src}) != 2788:
        raise RuntimeError(f"expected 2788 unique Special rows, got {len(src)}")

    for r in src:
        sid = int(r["SpecialID"])
        tag = r["Tag"]
        aliases = aliases_by_id.get(sid, [])
        rel, rel_reasons = relation_needed(r, tag)
        classes = {}
        hits = {}
        for name, vocab in vocabs.items():
            c, h = classify(vocab, tag, aliases)
            classes[name] = c; hits[name] = h
        rec, human, rec_reason = final_recommend(classes, rel)
        rows.append({
            "special_id": sid,
            "canonical": tag,
            "wd14_class": classes["WD14"],
            "kagami_class": classes["Kagami"],
            "cl_class": classes["CL"],
            "usable_tags_aliases": json.dumps(hits, ensure_ascii=False, separators=(",", ":")),
            "relation_required": str(rel).lower(),
            "relation_reasons": " | ".join(rel_reasons),
            "human_review_required": str(human).lower(),
            "final_recommendation": rec,
            "recommendation_reason": rec_reason,
        })

    fields = ["special_id","canonical","wd14_class","kagami_class","cl_class","usable_tags_aliases","relation_required","relation_reasons","human_review_required","final_recommendation","recommendation_reason"]
    write_csv(OUTDIR / "special2788_evaluator_coverage.csv", rows, fields)
    cases = choose_cases(rows)
    write_csv(OUTDIR / "representative_calibration_cases.csv", cases, ["stratum","special_id","canonical","final_recommendation","why_selected"])

    summary = {"rows": len(rows), "provenance": provenance, "coverage": {}, "final": dict(Counter(r["final_recommendation"] for r in rows)), "relation_required": sum(r["relation_required"] == "true" for r in rows), "representative_cases": len(cases)}
    for key, col in (("WD14","wd14_class"),("Kagami","kagami_class"),("CL","cl_class")):
        ctr = Counter(r[col] for r in rows)
        direct = ctr[CLASS_DIRECT]
        incl_alias = direct + ctr[CLASS_ALIAS]
        summary["coverage"][key] = {"classes": dict(ctr), "direct_count": direct, "direct_pct": round(direct/2788*100,2), "direct_alias_count": incl_alias, "direct_alias_pct": round(incl_alias/2788*100,2)}
    verified_cols = ["wd14_class","kagami_class"] + (["cl_class"] if provenance["CL"]["status"] == "OK" else [])
    union_direct = sum(any(r[c] == CLASS_DIRECT for c in verified_cols) for r in rows)
    union_da = sum(any(r[c] in {CLASS_DIRECT,CLASS_ALIAS} for c in verified_cols) for r in rows)
    union_components = sum(any(r[c] in {CLASS_DIRECT,CLASS_ALIAS,CLASS_COMPONENT} for c in verified_cols) for r in rows)
    summary["combined"] = {
        "verified_evaluators": verified_cols,
        "direct_union_count": union_direct,
        "direct_union_pct": round(union_direct/2788*100,2),
        "direct_alias_union_count": union_da,
        "direct_alias_union_pct": round(union_da/2788*100,2),
        "observable_including_components_count": union_components,
        "observable_including_components_pct": round(union_components/2788*100,2),
        "three_evaluator_exact_available": provenance["CL"]["status"] == "OK",
    }
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def pct(n): return f"{n/2788*100:.2f}%"
    lines = [
        "# Issue #44 — Special 2,788 evaluator coverage desk analysis",
        "",
        "> Desk/vocabulary coverage only. This is not image-level accuracy proof and not Danbooru semantic authority.",
        "",
        f"- rows classified: {len(rows)} / 2788",
        f"- relation/binding review required by structural heuristic: {summary['relation_required']} / 2788 ({pct(summary['relation_required'])})",
        "",
        "## Evaluator vocabulary coverage",
    ]
    for k in ("WD14","Kagami","CL"):
        c = summary["coverage"][k]
        p = provenance[k]
        lines.append(f"- {k}: status={p['status']}, vocab={p['vocab_rows']}, direct={c['direct_count']} ({c['direct_pct']}%), direct+alias={c['direct_alias_count']} ({c['direct_alias_pct']}%)")
    co = summary["combined"]
    lines += [
        "",
        "## Combined confirmed coverage",
        f"- verified evaluators: {', '.join(verified_cols)}",
        f"- direct union: {co['direct_union_count']} ({co['direct_union_pct']}%)",
        f"- direct+alias union: {co['direct_alias_union_count']} ({co['direct_alias_union_pct']}%)",
        f"- including component predicates: {co['observable_including_components_count']} ({co['observable_including_components_pct']}%)",
        f"- exact 3-evaluator result available: {co['three_evaluator_exact_available']}",
        "",
        "## Provisional routing",
    ]
    for rec in ("AUTO_CANDIDATE","REVIEW_REQUIRED","BLOCKED"):
        n = summary["final"].get(rec,0); lines.append(f"- {rec}: {n} ({pct(n)})")
    lines += [
        "",
        "## Boundary",
        "- AUTO_CANDIDATE means only: at least one verified evaluator has direct/alias vocabulary support, and no structural relation/binding requirement was detected. It still requires real-image calibration before Stage10 automatic use.",
        "- REVIEW_REQUIRED includes relation/binding/body-site/spatial/count/compound cases even when a unary tag exists.",
        "- BLOCKED has no useful verified direct/alias/component observation, or relation is required with no useful observation.",
        "- CL gated vocabulary access failure, if present, is an access blocker and must not be misreported as model incapability.",
        "",
        "## Files",
        "- `special2788_evaluator_coverage.csv`",
        "- `representative_calibration_cases.csv`",
        "- `summary.json`",
        "",
        "No `data/**` file was modified by this analysis.",
    ]
    (OUTDIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
