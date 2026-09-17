#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SIDECAR = Path("docs/issue118/research_sidecar_v3.csv")
GENERAL = Path("docs/issue64/production_candidate/effective_sidecar.csv")
TRIAGE = Path("docs/issue118/remaining_cluster_triage_v8/cluster_triage_v8.csv")
OUT = Path("docs/issue118/bulk_candidate_adversarial_v9")

LEX_GROUPS = {
    "EXPLICIT_SEX": {
        "sex","handjob","blowjob","fellatio","paizuri","irrumatio","cum","cumshot","ejaculation",
        "orgasm","masturbation","vibrator","dildo","buttjob","threesome","penetration","prostitution",
        "zoophilia","rape","cunnilingus","anilingus","fingering","footjob","creampie","bukkake",
        "fleshlight","onahole","fuck","fucking",
    },
    "ANATOMY": {
        "penis","pussy","vagina","vulva","anus","anal","clitoris","testicle","testicles","scrotum",
        "nipple","nipples","breast","breasts","areola","areolae","pubic","crotch","genital",
    },
    "RESTRAINT_FETISH": {
        "gag","gagged","handcuff","handcuffs","leash","rope","shackle","restraint","restraints",
        "bondage","blindfold","clamp","clamps","collar","fetish","bdsm","spanking","whip",
    },
    "REPRO": {
        "pregnant","pregnancy","lactation","breastfeeding","birth","insemination","fertilization",
        "fertilisation","impregnation",
    },
    "INJURY": {
        "blood","wound","gore","amputee","amputation","castration","corpse","injury","snuff",
    },
    "EXPOSURE_INTIMATE": {
        "nude","naked","topless","bottomless","panties","underwear","bra","cleavage","underboob",
        "upskirt","downblouse","lingerie","crotchless","pasties","maebari",
    },
    "ADULT_ROLE_DEVICE": {
        "condom","condoms","porn","pornstar","stripper","prostitute","courtesan","oiran","speculum",
        "bodystocking","bustier","gravure",
    },
}

MANUAL_EXACT_TOKENS = {
    "ahegao","ecchi","erotic","erotica","hentai","horny","lewd","lust","lustful","sensual",
    "seductive","suggestive","sexual","sexualized","nsfw","r18","r18g","fetish",
    "orgasm","orgasmic","cum","cumshot","ejaculation","masturbation","rape","fuck","fucking",
    "fellatio","cunnilingus","anilingus","paizuri","handjob","footjob","blowjob","creampie",
    "bukkake","nude","naked","lingerie","panties","underwear","bra","cleavage","breast","breasts",
    "nipple","nipples","penis","pussy","vagina","vulva","anus","anal","clitoris","crotch","pubic",
    "genital","condom","dildo","vibrator","onahole","fleshlight","bdsm","bondage","gag","collar",
    "leash","spanking","whip","pregnant","pregnancy","lactation","breastfeeding","impregnation",
    "prostitute","stripper","porn","pornstar","gravure","bodystocking","bustier","speculum",
}

MANUAL_COMPOUND_STEMS = {
    "sexual","erotic","hentai","orgasm","masturb","fellatio","cunniling","aniling","paizuri",
    "handjob","footjob","blowjob","creampie","bukkake","nipple","penis","vagina","vulva",
    "clitoris","condom","dildo","vibrator","fleshlight","onahole","bondage","pregnan","lactat",
    "impregn","prostitut","stripper","gravure","bodystocking","bustier","speculum",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return "_".join(value.strip().lower().replace("_", " ").split())


def tokenize(key: str) -> set[str]:
    return {p for p in re.split(r"[^a-z0-9]+", key.lower()) if len(p) >= 2}


def old_flags(key: str) -> str:
    # Reproduce v7 clustering exactly. Do not reuse the broader red-team tokenizer here.
    parts = {p for p in re.split(r"[_()\-]+", key.lower()) if p}
    hit = sorted(name for name, terms in LEX_GROUPS.items() if parts & terms)
    return "+".join(hit) if hit else "NONE"


def learned_risk_tokens(side_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    risk_rows = [r for r in side_rows if r["sexual_intent"] in {"SEXUAL", "CONTEXTUAL"}]
    non_rows = [r for r in side_rows if r["sexual_intent"] == "NON_SEXUAL"]

    risk_counts = Counter()
    non_counts = Counter()
    for r in risk_rows:
        risk_counts.update(tokenize(r["identity_key"]))
    for r in non_rows:
        non_counts.update(tokenize(r["identity_key"]))

    result = []
    risk_n = max(1, len(risk_rows))
    non_n = max(1, len(non_rows))
    for token, rc in risk_counts.items():
        if len(token) < 3 or rc < 2:
            continue
        nc = non_counts[token]
        risk_prev = rc / risk_n
        non_prev = nc / non_n
        lift = (risk_prev + 1e-6) / (non_prev + 1e-6)
        if lift < 6.0:
            continue
        result.append({
            "token": token,
            "risk_count": rc,
            "nonsexual_count": nc,
            "risk_prevalence": round(risk_prev, 8),
            "nonsexual_prevalence": round(non_prev, 8),
            "lift": round(lift, 4),
        })
    result.sort(key=lambda x: (-float(x["lift"]), -int(x["risk_count"]), str(x["token"])))
    return result


def manual_redteam_flags(key: str) -> list[str]:
    toks = tokenize(key)
    flags = []
    exact = sorted(toks & MANUAL_EXACT_TOKENS)
    if exact:
        flags.append("manual_exact:" + ",".join(exact))

    normalized = key.lower()
    stems = sorted(stem for stem in MANUAL_COMPOUND_STEMS if stem in normalized)
    if stems:
        flags.append("manual_stem:" + ",".join(stems))
    return flags


def holdout_rank(key: str) -> str:
    return hashlib.sha256(("issue118-v9-fresh-holdout:" + key).encode("utf-8")).hexdigest()


def main() -> int:
    side = read_csv(SIDECAR)
    general = read_csv(GENERAL)
    triage = read_csv(TRIAGE)

    if len(side) != 31752:
        raise SystemExit(f"sidecar drift: {len(side)}")
    bulk_clusters = {
        r["cluster_key"] for r in triage if r["triage_bucket"] == "BULK_CANDIDATE"
    }
    if len(bulk_clusters) != 4:
        raise SystemExit(f"expected 4 corrected v8 BULK_CANDIDATE clusters, got {len(bulk_clusters)}")

    g = {norm(r["canonical"]): r for r in general}
    learned = learned_risk_tokens(side)
    learned_set = {str(r["token"]) for r in learned}

    candidates = []
    for r in side:
        if r["review_status"] != "UNCLASSIFIED":
            continue
        key = r["identity_key"]
        gr = g.get(key)
        if gr is None or r["is_special"] == "YES":
            continue
        path = (gr.get("primary_path") or "").strip() or "(none)"
        fl = old_flags(key)
        cluster_key = "|".join(["GENERAL_ONLY", path, fl])
        if cluster_key not in bulk_clusters:
            continue

        toks = tokenize(key)
        learned_hits = sorted(toks & learned_set)
        redteam = manual_redteam_flags(key)
        if learned_hits:
            redteam.append("learned_risk_token:" + ",".join(learned_hits))

        candidates.append({
            "identity_key": key,
            "general_path": path,
            "cluster_key": cluster_key,
            "old_lex_flags": fl,
            "redteam_flags": "|".join(redteam),
            "candidate_state": "REDTEAM_REVIEW" if redteam else "CLEAN_FOR_FRESH_HOLDOUT",
        })

    candidates.sort(key=lambda r: r["identity_key"])
    if len(candidates) != 1843:
        raise SystemExit(f"expected 1843 corrected v8 bulk identities, got {len(candidates)}")

    flagged = [r for r in candidates if r["candidate_state"] == "REDTEAM_REVIEW"]
    clean = [r for r in candidates if r["candidate_state"] == "CLEAN_FOR_FRESH_HOLDOUT"]
    holdout = sorted(clean, key=lambda r: (holdout_rank(r["identity_key"]), r["identity_key"]))[:120]

    OUT.mkdir(parents=True, exist_ok=True)

    inv_fields = [
        "identity_key","general_path","cluster_key","old_lex_flags",
        "redteam_flags","candidate_state",
    ]
    with (OUT / "bulk_candidate_inventory_v9.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(candidates)

    with (OUT / "redteam_review_inventory_v9.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(flagged)

    learned_fields = [
        "token","risk_count","nonsexual_count","risk_prevalence","nonsexual_prevalence","lift",
    ]
    with (OUT / "learned_risk_tokens_v9.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=learned_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(learned)

    holdout_fields = [
        "identity_key","general_path","cluster_key","candidate_state",
        "human_intent","review_note",
    ]
    with (OUT / "fresh_holdout_template_v9.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=holdout_fields, lineterminator="\n")
        w.writeheader()
        for r in holdout:
            w.writerow({
                "identity_key": r["identity_key"],
                "general_path": r["general_path"],
                "cluster_key": r["cluster_key"],
                "candidate_state": r["candidate_state"],
                "human_intent": "",
                "review_note": "",
            })

    summary = {
        "issue": 118,
        "mode": "BULK_CANDIDATE_ADVERSARIAL_V9",
        "source_bulk_candidate_identities": len(candidates),
        "redteam_review_rows": len(flagged),
        "clean_for_fresh_holdout_rows": len(clean),
        "fresh_holdout_template_rows": len(holdout),
        "learned_risk_token_count": len(learned),
        "risk_seed_class_counts": {
            "SEXUAL": sum(1 for r in side if r["sexual_intent"] == "SEXUAL"),
            "CONTEXTUAL": sum(1 for r in side if r["sexual_intent"] == "CONTEXTUAL"),
            "NON_SEXUAL": sum(1 for r in side if r["sexual_intent"] == "NON_SEXUAL"),
        },
        "learned_token_use": "DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY",
        "manual_pattern_use": "DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY",
        "holdout_verdicts_generated": "NO",
        "semantic_authority": "NO",
        "auto_promotion_performed": "NO",
        "production_authority": "NO",
        "main_mutated": "NO",
        "issue117_code_mutated": "NO",
        "catalog_mutated": "NO",
        "user_db_mutated": "NO",
        "next_gate": (
            "independently review all redteam rows and the fixed 120-row fresh holdout; "
            "freeze review artifact SHA before any sidecar promotion"
        ),
    }
    (OUT / "summary_v9.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
