#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

EXPECTED_GELBOORU_SHA256 = "7329c1e4b4d037e27bd10b90751ba850fa1a42ff43bfc80a96f0bb235aa174cc"
EXPECTED_GELBOORU_ROWS = 1_393_773

# e621/e926 category mapping used by current DB exports.
E621_INVALID_CATEGORY = 6

# Gelbooru 2026-06-11 dataset card:
# 2 = Invalid / Unused, 6 = Deprecated.
GELBOORU_BLOCKED_CATEGORIES = {2, 6}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(value: object) -> str:
    if value is None:
        return ""
    s = unicodedata.normalize("NFKC", str(value)).strip().lower()
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def filename_date(path: Path) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else ""


def read_terms(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = {"norm", "term", "source_kind", "special_id"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"terms CSV missing columns: {sorted(missing)}")
    if len(df) != 2811:
        raise ValueError(f"expected 2811 unique terms, got {len(df)}")
    if df["norm"].astype(str).duplicated().any():
        raise ValueError("terms CSV contains duplicate norm values")
    if df["term"].fillna("").astype(str).str.strip().eq("").any():
        raise ValueError("terms CSV contains blank term")
    recalculated = df["term"].map(norm)
    mismatch = df["norm"].astype(str) != recalculated.astype(str)
    if mismatch.any():
        sample = df.loc[mismatch, ["term", "norm"]].head(5).to_dict("records")
        raise ValueError(f"terms CSV normalization mismatch: {sample}")
    return df


def validate_terms_cover_special(terms: pd.DataFrame, special_path: Path) -> dict:
    sp = pd.read_csv(special_path, encoding="utf-8-sig")
    if len(sp) != 2788 or sp["ID"].nunique() != 2788:
        raise ValueError("Special source must contain exactly 2788 unique IDs")
    if sp["Tag"].astype(str).str.casefold().duplicated().any():
        raise ValueError("Special source contains duplicate original tags")
    special_norm = sp["Tag"].map(norm)
    if special_norm.duplicated().any():
        dup = sp.loc[special_norm.duplicated(keep=False), ["ID", "Tag"]].head(10).to_dict("records")
        raise ValueError(f"Special source contains duplicate normalized tags: {dup}")

    term_norms = set(terms["norm"].astype(str))
    missing = [str(t) for t in sp["Tag"] if norm(t) not in term_norms]
    if missing:
        raise ValueError(f"model-aux input misses Special terms: {missing[:10]}")
    return {
        "special_rows": 2788,
        "special_terms_covered": 2788,
        "external_unique_terms": int(len(terms) - 2788),
    }


# ----------------------------
# e621 RAW DB EXPORT (preferred)
# ----------------------------

def read_e621_raw_tags(path: Path) -> pd.DataFrame:
    # pandas infers gzip from .gz.
    df = pd.read_csv(path, encoding="utf-8-sig", compression="infer")
    lc = {str(c).strip().lower(): c for c in df.columns}
    required = {}
    for target, choices in {
        "name": ("name", "tag_name"),
        "category": ("category", "category_id"),
        "post_count": ("post_count", "count"),
    }.items():
        col = next((lc[k] for k in choices if k in lc), None)
        if col is None:
            raise ValueError(f"e621 tags export missing {target}; columns={list(df.columns)}")
        required[target] = col

    out = pd.DataFrame({
        "name": df[required["name"]].fillna("").astype(str),
        "category": pd.to_numeric(df[required["category"]], errors="coerce").fillna(-1).astype("int64"),
        "post_count": pd.to_numeric(df[required["post_count"]], errors="coerce").fillna(0).astype("int64"),
    })
    out = out[out["name"].str.strip().ne("")].copy()
    out["norm_name"] = out["name"].map(norm)
    return out


def read_e621_raw_aliases(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig", compression="infer")
    lc = {str(c).strip().lower(): c for c in df.columns}
    antecedent = next((lc[k] for k in ("antecedent_name", "alias", "antecedent") if k in lc), None)
    consequent = next((lc[k] for k in ("consequent_name", "tag", "consequent") if k in lc), None)
    status = next((lc[k] for k in ("status", "state") if k in lc), None)
    if antecedent is None or consequent is None:
        raise ValueError(
            f"e621 alias export missing antecedent/consequent; columns={list(df.columns)}"
        )
    out = pd.DataFrame({
        "antecedent_name": df[antecedent].fillna("").astype(str),
        "consequent_name": df[consequent].fillna("").astype(str),
        "status": df[status].fillna("unknown").astype(str).str.strip().str.lower() if status is not None else "unknown",
    })
    out = out[
        out["antecedent_name"].str.strip().ne("") &
        out["consequent_name"].str.strip().ne("")
    ].copy()
    out["norm_antecedent"] = out["antecedent_name"].map(norm)
    out["norm_consequent"] = out["consequent_name"].map(norm)
    return out


def crossmatch_e621_raw(
    terms: pd.DataFrame,
    tags_path: Path,
    aliases_path: Path | None,
    allow_date_mismatch: bool = False,
) -> tuple[pd.DataFrame, dict]:
    tags = read_e621_raw_tags(tags_path)
    aliases = read_e621_raw_aliases(aliases_path) if aliases_path else pd.DataFrame(
        columns=["antecedent_name", "consequent_name", "status", "norm_antecedent", "norm_consequent"]
    )

    tags_date = filename_date(tags_path)
    alias_date = filename_date(aliases_path) if aliases_path else ""
    if (
        aliases_path and tags_date and alias_date and tags_date != alias_date
        and not allow_date_mismatch
    ):
        raise ValueError(
            f"e621 tags/aliases export dates differ: tags={tags_date}, aliases={alias_date}"
        )

    exact_map: dict[str, list] = {}
    tag_by_norm: dict[str, list] = {}
    for r in tags.itertuples(index=False):
        exact_map.setdefault(r.norm_name, []).append(r)
        tag_by_norm.setdefault(r.norm_name, []).append(r)

    alias_map: dict[str, list] = {}
    for r in aliases.itertuples(index=False):
        alias_map.setdefault(r.norm_antecedent, []).append(r)

    status_rank = {"active": 0, "pending": 1, "deleted": 2, "retired": 3, "unknown": 4}

    def resolve_alias(alias_rows: list, also_alias: str, invalid_exact_forms: str = "") -> dict:
        ordered = sorted(
            alias_rows,
            key=lambda r: (status_rank.get(str(r.status), 9), r.consequent_name),
        )
        active = [r for r in ordered if str(r.status) == "active"]
        pending = [r for r in ordered if str(r.status) == "pending"]
        historical = [r for r in ordered if str(r.status) in {"deleted", "retired"}]
        unknown = [r for r in ordered if str(r.status) not in {"active", "pending", "deleted", "retired"}]
        active_targets = sorted({r.consequent_name for r in active})

        if len(active_targets) == 1:
            chosen = active[0]
            target_rows = tag_by_norm.get(chosen.norm_consequent, [])
            valid_targets = [r for r in target_rows if int(r.category) != E621_INVALID_CATEGORY]
            target = sorted(valid_targets, key=lambda r: (-int(r.post_count), r.name))[0] if valid_targets else None
            target_valid = target is not None
            collision_parts = []
            if len(active) > 1:
                collision_parts.append("DUPLICATE_ACTIVE_ALIAS_ROWS")
            if invalid_exact_forms:
                collision_parts.append("INVALID_EXACT_AND_ACTIVE_ALIAS")
            return {
                "e621_match_kind": "ACTIVE_ALIAS",
                "e621_exact_form": "",
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": chosen.consequent_name,
                "e621_alias_status": "active",
                "e621_post_count": int(target.post_count) if target is not None else "",
                "e621_category": int(target.category) if target is not None else "",
                "e621_invalid": False if target_valid else "",
                "also_alias_matches": also_alias,
                "collision": " | ".join(collision_parts),
                "e621_source_candidate_form": chosen.consequent_name if target_valid else "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_ACTIVE_ALIAS",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": (
                    "Active raw e621 alias resolves to an existing non-invalid canonical source tag; this is source evidence only, not a NoobAI recommendation."
                    + (" An invalid same-input exact tag was retained only as audit evidence." if invalid_exact_forms else "")
                    if target_valid else
                    "Active alias target is missing or only invalid in the paired tags export; do not recommend."
                ),
            }
        if active:
            return {
                "e621_match_kind": "AMBIGUOUS_ACTIVE_ALIAS",
                "e621_exact_form": "",
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": " | ".join(active_targets),
                "e621_alias_status": "active",
                "e621_post_count": "",
                "e621_category": "",
                "e621_invalid": "",
                "also_alias_matches": also_alias,
                "collision": "MULTIPLE_ACTIVE_ALIAS_TARGETS" + (" | INVALID_EXACT_PRESENT" if invalid_exact_forms else ""),
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_ACTIVE_ALIAS_AMBIGUOUS",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Multiple active alias targets; never silently resolve or default-recommend.",
            }
        if pending:
            return {
                "e621_match_kind": "PENDING_ALIAS",
                "e621_exact_form": "",
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": " | ".join(sorted({r.consequent_name for r in pending})),
                "e621_alias_status": "pending",
                "e621_post_count": "",
                "e621_category": "",
                "e621_invalid": "",
                "also_alias_matches": also_alias,
                "collision": "INVALID_EXACT_PRESENT" if invalid_exact_forms else "",
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_PENDING_ALIAS_DISCOVERY_ONLY",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Pending alias is discovery-only; never default-recommend.",
            }
        if historical:
            return {
                "e621_match_kind": "HISTORICAL_ALIAS",
                "e621_exact_form": "",
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": " | ".join(sorted({r.consequent_name for r in historical})),
                "e621_alias_status": "deleted_or_retired",
                "e621_post_count": "",
                "e621_category": "",
                "e621_invalid": "",
                "also_alias_matches": also_alias,
                "collision": "INVALID_EXACT_PRESENT" if invalid_exact_forms else "",
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_HISTORICAL_ALIAS_AUDIT_ONLY",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Deleted/retired alias is audit history only; never default-recommend.",
            }
        return {
            "e621_match_kind": "UNKNOWN_STATUS_ALIAS",
            "e621_exact_form": "",
            "e621_invalid_exact_forms": invalid_exact_forms,
            "e621_alias_target": " | ".join(sorted({r.consequent_name for r in unknown})),
            "e621_alias_status": "unknown",
            "e621_post_count": "",
            "e621_category": "",
            "e621_invalid": "",
            "also_alias_matches": also_alias,
            "collision": "INVALID_EXACT_PRESENT" if invalid_exact_forms else "",
            "e621_source_candidate_form": "",
            "recommended_noob_eps_form": "",
            "recommended_noob_vpred_form": "",
            "source_evidence": "RAW_E621_ALIAS_STATUS_UNKNOWN",
            "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
            "reason": "Alias status is not trusted; discovery only; never default-recommend.",
        }

    rows = []
    for t in terms.itertuples(index=False):
        n = str(t.norm)
        exact_rows = exact_map.get(n, [])
        alias_rows = alias_map.get(n, [])
        valid_exact_rows = [r for r in exact_rows if int(r.category) != E621_INVALID_CATEGORY]
        invalid_exact_rows = [r for r in exact_rows if int(r.category) == E621_INVALID_CATEGORY]

        also_alias = " | ".join(
            f"{r.status}:{r.consequent_name}" for r in
            sorted(alias_rows, key=lambda x: (x.status, x.consequent_name))
        )
        invalid_exact_forms = " | ".join(
            r.name for r in sorted(invalid_exact_rows, key=lambda r: (-int(r.post_count), r.name))
        )

        # A valid exact current tag has the strongest source-identity evidence.
        if valid_exact_rows:
            ordered = sorted(valid_exact_rows, key=lambda r: (-int(r.post_count), r.name))
            best = ordered[0]
            collision = []
            if len(valid_exact_rows) > 1:
                collision.append("MULTIPLE_VALID_EXACT_ROWS")
            if invalid_exact_rows:
                collision.append("VALID_AND_INVALID_EXACT_ROWS")
            if alias_rows:
                collision.append("EXACT_AND_ALIAS_SAME_INPUT")
            result = {
                "e621_match_kind": "EXACT_TAG",
                "e621_exact_form": best.name,
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": "",
                "e621_alias_status": "",
                "e621_post_count": int(best.post_count),
                "e621_category": int(best.category),
                "e621_invalid": False,
                "also_alias_matches": also_alias,
                "collision": " | ".join(collision),
                "e621_source_candidate_form": best.name,
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_EXACT_TAG",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Exact non-invalid tag exists in the paired raw e621 tags export; this is source evidence only, not a NoobAI recommendation.",
            }
        # Category=6 exact rows are audit evidence, not a default form. A unique valid
        # active alias for the same input may still supply the current canonical source form.
        elif alias_rows:
            result = resolve_alias(alias_rows, also_alias, invalid_exact_forms)
        elif invalid_exact_rows:
            best = sorted(invalid_exact_rows, key=lambda r: (-int(r.post_count), r.name))[0]
            result = {
                "e621_match_kind": "EXACT_INVALID_TAG",
                "e621_exact_form": best.name,
                "e621_invalid_exact_forms": invalid_exact_forms,
                "e621_alias_target": "",
                "e621_alias_status": "",
                "e621_post_count": int(best.post_count),
                "e621_category": int(best.category),
                "e621_invalid": True,
                "also_alias_matches": "",
                "collision": "MULTIPLE_INVALID_EXACT_ROWS" if len(invalid_exact_rows) > 1 else "",
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "RAW_E621_INVALID_EXACT_TAG_AUDIT_ONLY",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Only category=6 invalid exact tag exists; keep audit-visible and never default-recommend.",
            }
        else:
            result = {
                "e621_match_kind": "NO_MATCH_IN_RAW_EXPORT",
                "e621_exact_form": "",
                "e621_invalid_exact_forms": "",
                "e621_alias_target": "",
                "e621_alias_status": "",
                "e621_post_count": "",
                "e621_category": "",
                "e621_invalid": "",
                "also_alias_matches": "",
                "collision": "",
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "NO_RAW_E621_TAG_OR_ALIAS_MATCH",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "No exact raw tag or alias match in this pinned export.",
            }

        rows.append({
            "input_norm": n,
            "input_term": t.term,
            "source_kind": t.source_kind,
            "special_id": t.special_id,
            **result,
        })

    result_df = pd.DataFrame(rows)
    meta = {
        "mode": "RAW_DB_EXPORT",
        "tags_path": str(tags_path),
        "tags_sha256": sha256(tags_path),
        "tags_date": tags_date,
        "tags_rows": int(len(tags)),
        "aliases_path": str(aliases_path) if aliases_path else "",
        "aliases_sha256": sha256(aliases_path) if aliases_path else "",
        "aliases_date": alias_date,
        "aliases_rows": int(len(aliases)),
        "input_rows": int(len(terms)),
        "result_rows": int(len(result_df)),
        "match_counts": {
            str(k): int(v) for k, v in result_df["e621_match_kind"].value_counts().items()
        },
        "model_familiarity_note": (
            "Tag/alias presence in a current source is vocabulary evidence, not proof that NoobAI learned it."
        ),
    }
    return result_df, meta


# -------------------------------------
# e621 PROCESSED AUTOCOMPLETE (fallback)
# -------------------------------------

def sniff_e621_autocomplete(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    lc = {str(c).strip().lower(): c for c in df.columns}
    name_col = next((lc[k] for k in ("name", "tag", "tag_name") if k in lc), None)
    cat_col = next((lc[k] for k in ("category", "category_id", "type") if k in lc), None)
    count_col = next((lc[k] for k in ("post_count", "count", "posts") if k in lc), None)
    alias_col = next((lc[k] for k in ("aliases", "alias") if k in lc), None)

    if name_col is None or count_col is None:
        df = pd.read_csv(path, encoding="utf-8-sig", header=None)
        if df.shape[1] < 3:
            raise ValueError(f"e621 autocomplete CSV has only {df.shape[1]} columns")
        cols = ["name", "category", "post_count", "aliases"] + [
            f"extra_{i}" for i in range(max(0, df.shape[1] - 4))
        ]
        df.columns = cols[:df.shape[1]]
        name_col = "name"
        cat_col = "category" if "category" in df.columns else None
        count_col = "post_count"
        alias_col = "aliases" if "aliases" in df.columns else None

    out = pd.DataFrame({
        "name": df[name_col].fillna("").astype(str),
        "category": pd.to_numeric(df[cat_col], errors="coerce").fillna(-1).astype("int64")
                    if cat_col is not None else -1,
        "post_count": pd.to_numeric(df[count_col], errors="coerce").fillna(0).astype("int64"),
        "aliases": df[alias_col].fillna("").astype(str) if alias_col is not None else "",
    })
    out = out[out["name"].str.strip().ne("")].copy()
    out["norm_name"] = out["name"].map(norm)
    return out


def split_alias_cell(cell: str) -> list[str]:
    # The upstream processor joins aliases with commas.
    return [p.strip() for p in str(cell or "").split(",") if p.strip()]


def crossmatch_e621_autocomplete(
    terms: pd.DataFrame,
    path: Path,
) -> tuple[pd.DataFrame, dict]:
    src = sniff_e621_autocomplete(path)
    exact_map: dict[str, list] = {}
    alias_map: dict[str, list] = {}
    for r in src.itertuples(index=False):
        exact_map.setdefault(r.norm_name, []).append(r)
        for a in split_alias_cell(r.aliases):
            alias_map.setdefault(norm(a), []).append(r)

    rows = []
    for t in terms.itertuples(index=False):
        ex = exact_map.get(str(t.norm), [])
        al = alias_map.get(str(t.norm), [])
        if ex:
            ordered = sorted(ex, key=lambda r: (-int(r.post_count), r.name))
            b = ordered[0]
            invalid = int(b.category) == E621_INVALID_CATEGORY
            rows.append({
                "input_norm": t.norm, "input_term": t.term, "source_kind": t.source_kind, "special_id": t.special_id,
                "e621_match_kind": "EXACT_TAG_IN_THRESHOLD_LIST",
                "e621_exact_form": b.name, "e621_alias_target": "", "e621_alias_status": "",
                "e621_post_count": int(b.post_count), "e621_category": int(b.category),
                "e621_invalid": invalid, "also_alias_matches": "",
                "collision": "MULTIPLE_EXACT_ROWS" if len(ex) > 1 else "",
                "e621_source_candidate_form": b.name if not invalid else "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "THRESHOLDED_AUTOCOMPLETE_EXACT_TAG",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Exact tag in thresholded autocomplete list; presence is useful, absence would not prove nonexistence."
            })
        elif al:
            rows.append({
                "input_norm": t.norm, "input_term": t.term, "source_kind": t.source_kind, "special_id": t.special_id,
                "e621_match_kind": "ALIAS_IN_COMBINED_IA_ED",
                "e621_exact_form": "",
                "e621_alias_target": " | ".join(sorted({r.name for r in al})),
                "e621_alias_status": "ACTIVE_OR_DELETED_NOT_SEPARABLE_FROM_PROCESSED_LIST",
                "e621_post_count": "", "e621_category": "", "e621_invalid": "",
                "also_alias_matches": "", "collision": "MULTIPLE_ALIAS_TARGETS" if len({r.name for r in al}) > 1 else "",
                "e621_source_candidate_form": "",
                "recommended_noob_eps_form": "",
                "recommended_noob_vpred_form": "",
                "source_evidence": "THRESHOLDED_AUTOCOMPLETE_ALIAS_DISCOVERY_ONLY",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "Processed ia-ed alias hit is discovery-only; active/deleted status is not preserved here."
            })
        else:
            rows.append({
                "input_norm": t.norm, "input_term": t.term, "source_kind": t.source_kind, "special_id": t.special_id,
                "e621_match_kind": "NO_MATCH_IN_THRESHOLD_LIST",
                "e621_exact_form": "", "e621_alias_target": "", "e621_alias_status": "",
                "e621_post_count": "", "e621_category": "", "e621_invalid": "",
                "also_alias_matches": "", "collision": "",
                "e621_source_candidate_form": "", "recommended_noob_eps_form": "", "recommended_noob_vpred_form": "",
                "source_evidence": "NO_THRESHOLD_LIST_MATCH_NOT_ABSENCE_PROOF",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "No match in a post-thresholded autocomplete list; this is NOT proof the tag is absent from e621."
            })

    result = pd.DataFrame(rows)
    meta = {
        "mode": "THRESHOLDED_AUTOCOMPLETE_FALLBACK",
        "source_path": str(path),
        "source_sha256": sha256(path),
        "source_rows": int(len(src)),
        "input_rows": int(len(terms)),
        "result_rows": int(len(result)),
        "match_counts": {
            str(k): int(v) for k, v in result["e621_match_kind"].value_counts().items()
        },
        "critical_note": "Fallback source is thresholded and combines active/deleted aliases.",
    }
    return result, meta


# ----------------------------
# Gelbooru / Anima
# ----------------------------

def parse_bool_series(series: pd.Series) -> pd.Series:
    """Parse booleans strictly; avoids bool("false") == True for CSV fixtures/sources."""
    true_values = {"1", "true", "t", "yes", "y"}
    false_values = {"0", "false", "f", "no", "n", "", "none", "nan", "null"}
    def one(v: object) -> bool:
        if isinstance(v, bool):
            return v
        if pd.isna(v):
            return False
        text = str(v).strip().lower()
        if text in true_values:
            return True
        if text in false_values:
            return False
        raise ValueError(f"Unrecognized boolean value in Gelbooru ambiguity column: {v!r}")
    return series.map(one).astype(bool)

def read_gelbooru(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        try:
            df = pd.read_parquet(path)
        except ImportError:
            try:
                import duckdb
            except ImportError as e:
                raise ImportError("Parquet requires pyarrow/fastparquet or duckdb.") from e
            escaped = str(path).replace("'", "''")
            df = duckdb.sql(f"SELECT * FROM read_parquet('{escaped}')").df()
    else:
        df = pd.read_csv(path, encoding="utf-8-sig")

    lc = {str(c).strip().lower(): c for c in df.columns}
    mapping = {}
    for out_name, choices in {
        "tag_name": ("tag_name", "name"),
        "post_count": ("post_count", "count"),
        "category_id": ("category_id", "category", "type"),
        "is_ambiguous": ("is_ambiguous", "ambiguous"),
    }.items():
        col = next((lc[k] for k in choices if k in lc), None)
        if col is None and out_name != "is_ambiguous":
            raise ValueError(f"Gelbooru source missing {out_name}; columns={list(df.columns)}")
        mapping[out_name] = col

    out = pd.DataFrame({
        "tag_name": df[mapping["tag_name"]].fillna("").astype(str),
        "post_count": pd.to_numeric(df[mapping["post_count"]], errors="coerce").fillna(0).astype("int64"),
        "category_id": pd.to_numeric(df[mapping["category_id"]], errors="coerce").fillna(-1).astype("int64"),
        "is_ambiguous": (
            parse_bool_series(df[mapping["is_ambiguous"]])
            if mapping["is_ambiguous"] is not None else False
        ),
    })
    # Dataset card notes one empty tag; keep it out of identity matching.
    out = out[out["tag_name"].str.strip().ne("")].copy()
    out["norm_name"] = out["tag_name"].map(norm)
    return out


def crossmatch_gelbooru(
    terms: pd.DataFrame,
    path: Path,
    require_frozen_sha: bool,
    require_expected_rows: bool,
) -> tuple[pd.DataFrame, dict]:
    actual_sha = sha256(path)
    if require_frozen_sha and actual_sha != EXPECTED_GELBOORU_SHA256:
        raise ValueError(
            f"Gelbooru SHA mismatch: expected {EXPECTED_GELBOORU_SHA256}, got {actual_sha}"
        )
    src = read_gelbooru(path)
    # Expected published row count includes the empty row. We removed blank names above.
    if require_expected_rows and len(src) not in {EXPECTED_GELBOORU_ROWS, EXPECTED_GELBOORU_ROWS - 1}:
        raise ValueError(
            f"Gelbooru row-count mismatch after blank filtering: got {len(src)}, "
            f"expected {EXPECTED_GELBOORU_ROWS} or {EXPECTED_GELBOORU_ROWS - 1}"
        )

    by_norm: dict[str, list] = {}
    for r in src.itertuples(index=False):
        by_norm.setdefault(r.norm_name, []).append(r)

    rows = []
    for t in terms.itertuples(index=False):
        matches = by_norm.get(str(t.norm), [])
        if not matches:
            rows.append({
                "input_norm": t.norm, "input_term": t.term, "source_kind": t.source_kind, "special_id": t.special_id,
                "gelbooru_match_kind": "NO_EXACT_GELBOORU_MATCH",
                "gelbooru_exact_form": "", "gelbooru_post_count": "", "gelbooru_category_id": "",
                "gelbooru_is_ambiguous": "", "gelbooru_blocked_category": "",
                "gelbooru_deprecated": "", "collision": "", "anima_gelbooru_source_candidate_form": "", "anima_recommended_form": "",
                "source_evidence": "NO_EXACT_GELBOORU_TAG_MATCH",
                "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
                "reason": "No exact normalized tag-name match; Gelbooru source has no alias table in this workflow, so do not guess."
            })
            continue

        ordered = sorted(matches, key=lambda r: (-int(r.post_count), r.tag_name))
        b = ordered[0]
        cat = int(b.category_id)
        blocked = cat in GELBOORU_BLOCKED_CATEGORIES
        deprecated = cat == 6
        ambiguous = bool(b.is_ambiguous)
        recommendable = not blocked and not ambiguous

        rows.append({
            "input_norm": t.norm, "input_term": t.term, "source_kind": t.source_kind, "special_id": t.special_id,
            "gelbooru_match_kind": "EXACT_TAG",
            "gelbooru_exact_form": b.tag_name, "gelbooru_post_count": int(b.post_count),
            "gelbooru_category_id": cat, "gelbooru_is_ambiguous": ambiguous,
            "gelbooru_blocked_category": blocked, "gelbooru_deprecated": deprecated,
            "collision": "MULTIPLE_EXACT_ROWS" if len(matches) > 1 else "",
            "anima_gelbooru_source_candidate_form": b.tag_name if recommendable else "",
            "anima_recommended_form": "",
            "source_evidence": "GELBOORU_EXACT_TAG",
            "model_familiarity_status": "UNKNOWN_NOT_MODEL_OBSERVED",
            "reason": (
                "Exact Gelbooru form is a source-side candidate only; current-source presence does not prove Anima learned or prefers it."
                if recommendable else
                "Exact form is ambiguous or in invalid/unused/deprecated category 2/6; audit-visible only."
            )
        })

    result = pd.DataFrame(rows)
    meta = {
        "source_path": str(path),
        "source_sha256": actual_sha,
        "expected_sha256": EXPECTED_GELBOORU_SHA256,
        "published_rows_with_blank": EXPECTED_GELBOORU_ROWS,
        "usable_nonblank_rows": int(len(src)),
        "input_rows": int(len(terms)),
        "result_rows": int(len(result)),
        "match_counts": {
            str(k): int(v) for k, v in result["gelbooru_match_kind"].value_counts().items()
        },
        "blocked_exact_matches": int(
            ((result["gelbooru_match_kind"] == "EXACT_TAG") &
             (result["gelbooru_blocked_category"] == True)).sum()
        ),
        "ambiguous_exact_matches": int(
            ((result["gelbooru_match_kind"] == "EXACT_TAG") &
             (result["gelbooru_is_ambiguous"] == True)).sum()
        ),
        "model_familiarity_note": "Current Gelbooru presence does not itself prove Anima learned the tag.",
    }
    return result, meta


def build_cross_source_audit(
    terms: pd.DataFrame,
    e621: pd.DataFrame | None,
    gelbooru: pd.DataFrame | None,
) -> pd.DataFrame:
    base = terms[["norm", "term", "source_kind", "special_id"]].copy()
    base = base.rename(columns={"norm": "input_norm", "term": "input_term"})

    if e621 is not None:
        ec = e621[[
            "input_norm", "e621_match_kind", "e621_exact_form", "e621_alias_target",
            "e621_source_candidate_form", "recommended_noob_eps_form", "recommended_noob_vpred_form",
            "model_familiarity_status"
        ]].copy()
        ec = ec.rename(columns={"model_familiarity_status": "e621_model_familiarity_status"})
        base = base.merge(ec, on="input_norm", how="left")
    else:
        base["e621_match_kind"] = "NOT_RUN"
        base["e621_exact_form"] = ""
        base["e621_alias_target"] = ""
        base["e621_source_candidate_form"] = ""
        base["recommended_noob_eps_form"] = ""
        base["recommended_noob_vpred_form"] = ""
        base["e621_model_familiarity_status"] = "NOT_RUN"

    if gelbooru is not None:
        gc = gelbooru[[
            "input_norm", "gelbooru_match_kind", "gelbooru_exact_form",
            "anima_gelbooru_source_candidate_form", "anima_recommended_form", "model_familiarity_status"
        ]].copy()
        gc = gc.rename(columns={"model_familiarity_status": "gelbooru_model_familiarity_status"})
        base = base.merge(gc, on="input_norm", how="left")
    else:
        base["gelbooru_match_kind"] = "NOT_RUN"
        base["gelbooru_exact_form"] = ""
        base["anima_gelbooru_source_candidate_form"] = ""
        base["anima_recommended_form"] = ""
        base["gelbooru_model_familiarity_status"] = "NOT_RUN"

    def classify(r) -> str:
        e = str(r["e621_match_kind"])
        g = str(r["gelbooru_match_kind"])
        e_exact = e.startswith("EXACT_TAG")
        g_exact = g == "EXACT_TAG"
        e_alias = "ALIAS" in e
        if e_exact and g_exact:
            if norm(r["e621_exact_form"]) == norm(r["gelbooru_exact_form"]):
                return "BOTH_EXACT_SAME_NORMALIZED_FORM"
            return "BOTH_EXACT_DIFFERENT_SOURCE_FORMS"
        if e_exact and not g_exact:
            return "E621_EXACT_ONLY"
        if g_exact and not e_exact:
            return "GELBOORU_EXACT_E621_NONEXACT"
        if e_alias and not g_exact:
            return "E621_ALIAS_ONLY"
        if e_alias and g_exact:
            return "GELBOORU_EXACT_E621_ALIAS"
        if e == "NOT_RUN" or g == "NOT_RUN":
            return "PARTIAL_SOURCE_RUN"
        return "NO_EXACT_MATCH_IN_EITHER"

    base["cross_source_relation"] = base.apply(classify, axis=1)
    base["model_aux_identity_rule"] = "MODEL_AUX_NEVER_AUTO_REPLACES_SPECIAL_PROMPT_OWNER"
    return base


def write_deterministic_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def validate_e621_export_filename(path: Path, kind: str) -> str:
    expected_prefix = "tags-" if kind == "tags" else "tag_aliases-"
    m = re.fullmatch(rf"{re.escape(expected_prefix)}(\d{{4}}-\d{{2}}-\d{{2}})\.csv\.gz", path.name)
    if not m:
        raise ValueError(f"--final-audit requires canonical e621 {kind} filename, got {path.name!r}")
    return m.group(1)


def validate_e621_source_url(value: str, label: str) -> None:
    text = str(value or "").strip()
    if not re.fullmatch(r"https?://[^\s]+", text, flags=re.I):
        raise ValueError(f"e621 {label} source URL must be an absolute http(s) URL")
    host = re.sub(r"^https?://", "", text, flags=re.I).split("/", 1)[0].lower()
    if not (host == "e621.net" or host.endswith(".e621.net")):
        raise ValueError(f"e621 {label} source URL must point to e621.net provenance, got {host!r}")


def validate_final_audit_args(args: argparse.Namespace) -> None:
    if not getattr(args, "final_audit", False):
        return
    if args.e621_autocomplete:
        raise ValueError("--final-audit forbids thresholded --e621-autocomplete fallback")
    if not args.e621_tags or not args.e621_aliases or not args.gelbooru:
        raise ValueError("--final-audit requires --e621-tags + --e621-aliases + --gelbooru")
    if args.allow_e621_date_mismatch:
        raise ValueError("--final-audit forbids --allow-e621-date-mismatch")
    if args.allow_unpinned_gelbooru or args.skip_gelbooru_row_check:
        raise ValueError("--final-audit requires frozen Gelbooru SHA and row-count checks")
    td = validate_e621_export_filename(args.e621_tags, "tags")
    ad = validate_e621_export_filename(args.e621_aliases, "aliases")
    if td != ad:
        raise ValueError(f"--final-audit requires same-date e621 pair: tags={td}, aliases={ad}")
    required_text = {
        "--e621-tags-source-url": args.e621_tags_source_url,
        "--e621-aliases-source-url": args.e621_aliases_source_url,
        "--e621-tags-published-sha256": args.e621_tags_published_sha256,
        "--e621-aliases-published-sha256": args.e621_aliases_published_sha256,
    }
    missing = [k for k, v in required_text.items() if not str(v or "").strip()]
    if missing:
        raise ValueError("--final-audit missing provenance/checksum fields: " + ", ".join(missing))
    validate_e621_source_url(args.e621_tags_source_url, "tags")
    validate_e621_source_url(args.e621_aliases_source_url, "aliases")
    for label, value in (
        ("tags", args.e621_tags_published_sha256),
        ("aliases", args.e621_aliases_published_sha256),
    ):
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(value)):
            raise ValueError(f"published SHA-256 for e621 {label} is not 64 hex chars")


def verify_published_sha(path: Path, published_sha: str, label: str) -> str:
    actual = sha256(path)
    if published_sha and actual.lower() != str(published_sha).lower():
        raise ValueError(f"e621 {label} SHA mismatch: published={published_sha}, actual={actual}")
    return actual


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True, type=Path)
    ap.add_argument("--special", type=Path, help="Optional Special2788 source for coverage validation.")
    ap.add_argument("--output-dir", required=True, type=Path)

    e = ap.add_mutually_exclusive_group()
    e.add_argument("--e621-tags", type=Path, help="Preferred raw e621 tags-YYYY-MM-DD.csv.gz")
    e.add_argument("--e621-autocomplete", type=Path, help="Fallback thresholded processed list")

    ap.add_argument("--e621-aliases", type=Path, help="Raw tag_aliases-YYYY-MM-DD.csv.gz")
    ap.add_argument("--allow-e621-date-mismatch", action="store_true")
    ap.add_argument("--e621-tags-source-url", default="")
    ap.add_argument("--e621-aliases-source-url", default="")
    ap.add_argument("--e621-tags-published-sha256", default="")
    ap.add_argument("--e621-aliases-published-sha256", default="")

    ap.add_argument("--gelbooru", type=Path)
    ap.add_argument("--allow-unpinned-gelbooru", action="store_true")
    ap.add_argument("--skip-gelbooru-row-check", action="store_true")
    ap.add_argument("--final-audit", action="store_true", help="Strict final evidence gate; local files only, no network.")
    args = ap.parse_args()

    if args.e621_aliases and not args.e621_tags:
        raise ValueError("--e621-aliases requires --e621-tags")
    validate_final_audit_args(args)

    terms = read_terms(args.terms)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict = {"input_terms": len(terms)}

    if args.special:
        summary["input_coverage"] = validate_terms_cover_special(terms, args.special)

    e621_result = None
    if args.e621_tags:
        e621_result, meta = crossmatch_e621_raw(
            terms, args.e621_tags, args.e621_aliases,
            allow_date_mismatch=args.allow_e621_date_mismatch,
        )
        if args.e621_tags_published_sha256:
            verify_published_sha(args.e621_tags, args.e621_tags_published_sha256, "tags")
        if args.e621_aliases and args.e621_aliases_published_sha256:
            verify_published_sha(args.e621_aliases, args.e621_aliases_published_sha256, "aliases")
        meta.update({
            "tags_source_url": args.e621_tags_source_url,
            "aliases_source_url": args.e621_aliases_source_url,
            "tags_published_sha256": args.e621_tags_published_sha256,
            "aliases_published_sha256": args.e621_aliases_published_sha256,
            "final_audit_gate": bool(args.final_audit),
        })
        write_deterministic_csv(e621_result, args.output_dir / "e621_source_form_audit.csv")
        summary["e621"] = meta
    elif args.e621_autocomplete:
        e621_result, meta = crossmatch_e621_autocomplete(terms, args.e621_autocomplete)
        write_deterministic_csv(e621_result, args.output_dir / "e621_source_form_audit.csv")
        summary["e621"] = meta

    gel_result = None
    if args.gelbooru:
        gel_result, meta = crossmatch_gelbooru(
            terms,
            args.gelbooru,
            require_frozen_sha=not args.allow_unpinned_gelbooru,
            require_expected_rows=not args.skip_gelbooru_row_check,
        )
        write_deterministic_csv(gel_result, args.output_dir / "gelbooru_source_form_audit.csv")
        summary["gelbooru"] = meta

    cross = build_cross_source_audit(terms, e621_result, gel_result)
    write_deterministic_csv(cross, args.output_dir / "model_aux_cross_source_audit.csv")
    summary["cross_source_counts"] = {
        str(k): int(v) for k, v in cross["cross_source_relation"].value_counts().items()
    }

    (args.output_dir / "model_aux_crossmatch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
