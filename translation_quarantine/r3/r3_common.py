"""Shared deterministic helpers for the quarantined R3 translation pilot.

R3 deliberately treats every input translation as evidence, never as semantic
authority.  The helpers in this module are kept free of production imports so
that a test run cannot accidentally load or mutate the runtime overlay.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping


SCHEMA_VERSION = "r3-1"
ENGINE_VERSION = "r3-test-engine-1"
PILOT_SEED = "UIJA-R3-PILOT-20260908-V1"
BLIND_SEED = "UIJA-R3-BLIND30-20260908-V1"
PILOT_QUOTAS = {
    "LOW": 25,
    "MEDIUM": 20,
    "HIGH_POSE_ACTION": 20,
    "HIGH_ANATOMY_ADULT": 20,
    "CRITICAL": 15,
}
BLIND_QUOTAS = {
    "LOW": 4,
    "MEDIUM": 5,
    "HIGH_POSE_ACTION": 6,
    "HIGH_ANATOMY_ADULT": 7,
    "CRITICAL": 8,
}
RISK_ORDER = tuple(PILOT_QUOTAS)
STATES = {"READY", "REVIEW", "STALE_REVIEW", "CONTRADICTION"}
BRIDGE_AVAILABILITIES = {"AVAILABLE", "NOT_REQUIRED", "BRIDGE_MISSING", "BLOCKED_BRIDGE"}
TERM_CLASSES = {
    "EXACT_SYNONYM",
    "ORTHOGRAPHIC_VARIANT",
    "READING_VARIANT",
    "COMMON_EXACT_PARAPHRASE",
    "BROAD_SEARCH_ALIAS",
}

_POSE_WORDS = {
    "arching", "bending", "crouching", "dancing", "from_above", "from_behind",
    "from_below", "kneeling", "leaning", "lying", "looking_at_viewer",
    "on_back", "running", "sitting", "standing", "straddling", "walking",
}
_ANATOMY_WORDS = {
    "anal", "anus", "ass", "breast", "breasts", "clitoris", "cum", "dildo",
    "ejaculation", "feet", "footjob", "handjob", "labia", "lactation", "nipples",
    "penis", "pussy", "sex", "sex_toy", "spread_legs", "tail", "vaginal", "gaping",
    "vibrator", "vulva",
}
_CRITICAL_WORDS = {
    "between", "bound", "cuffs", "cross-section", "cross_section", "double",
    "holding", "multiple", "object_insertion", "penetration", "plug", "restraints",
    "sex_machine", "tentacles", "with", "wrapped", "x-ray", "x_ray",
}
_ATTRIBUTE_WORDS = {
    "black", "blue", "blonde", "brown", "closed", "green", "large", "long",
    "medium", "multicolored", "multiple", "purple", "red", "short", "simple",
    "small", "white", "yellow",
}
_ATTRIBUTE_MARKERS = (
    "美少女", "美女", "かわいい", "可愛い", "巨乳", "幼女", "成人", "若い",
    "大型", "小型", "白い", "黒い", "赤い", "青い",
)
_EVIDENCE_HAZARDS = {
    "parent": "PARENT_OR_CATEGORY_CONCEPT",
    "category": "PARENT_OR_CATEGORY_CONCEPT",
    "child": "SUBTYPE_OR_CHILD_CONCEPT",
    "subtype": "SUBTYPE_OR_CHILD_CONCEPT",
    "attribute_added": "ATTRIBUTE_ADDED",
    "actor_added": "ACTOR_ADDED",
    "target_added": "TARGET_ADDED",
    "context_added": "CONTEXT_ADDED",
    "adjacent": "ADJACENT_CONCEPT",
    "implication_only": "IMPLICATION_ONLY",
    "related_only": "RELATED_OR_COOCCURRENCE_ONLY",
    "cooccurrence_only": "RELATED_OR_COOCCURRENCE_ONLY",
    "count_changed": "COUNT_CHANGED",
    "type_changed": "OBJECT_STATE_ACTION_RELATION_TYPE_CHANGED",
    "sibling_collision": "SIBLING_COLLISION",
    "broader": "BROADER_THAN_CANONICAL",
    "narrower": "NARROWER_THAN_CANONICAL",
}


def canonical_json_bytes(value: Any) -> bytes:
    """Return the canonical UTF-8 representation used by all R3 hashes."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.replace("\r\n", "\n").encode("utf-8"))


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for row in rows
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return [dict(row) for row in csv.DictReader(stream)]


def stable_key(seed: str, canonical: str) -> str:
    return sha256_text(seed + "\0" + canonical)


def ensure_r3_output(root: Path, output_dir: Path) -> Path:
    """Validate the fail-closed output boundary and return a resolved path."""

    root = root.resolve()
    allowed = (root / "translation_quarantine" / "r3").resolve()
    output = output_dir.resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise ValueError(f"R3 output must stay below {allowed}, got {output}") from exc
    output.mkdir(parents=True, exist_ok=True)
    return output


def classify_risk(canonical: str, semantic_class: str = "") -> str:
    """Classify from canonical structure only; no Japanese term is consulted."""

    value = canonical.strip().lower()
    tokens = [token for token in re.split(r"[_\-]+", value) if token]
    token_set = set(tokens)
    if (
        any(word in value for word in ("_between_", "_with_", "_on_", "_under_"))
        or any(word in token_set for word in _CRITICAL_WORDS)
        or value.count("_") >= 3
        or any(value.startswith(prefix) for prefix in ("anal_", "multiple_", "two_", "three_"))
    ):
        return "CRITICAL"
    if token_set & _POSE_WORDS or semantic_class in {"pose_composition", "state_action"}:
        return "HIGH_POSE_ACTION"
    if token_set & _ANATOMY_WORDS or semantic_class in {"anatomy_adult", "body_state", "body_action"}:
        return "HIGH_ANATOMY_ADULT"
    if token_set & _ATTRIBUTE_WORDS or any(token.isdigit() for token in tokens) or value in {"1girl", "1boy", "2girls", "3girls"}:
        return "MEDIUM"
    return "LOW"


def semantic_class_for(canonical: str, lanes: str = "") -> str:
    """Return a conservative class label for reports, not semantic authority."""

    value = canonical.lower()
    if any(word in value for word in ("anal", "breast", "penis", "sex", "vaginal", "anus", "nipples")):
        return "anatomy_adult"
    if any(word in value for word in ("standing", "sitting", "kneeling", "lying", "straddling")):
        return "pose_composition"
    if any(word in value for word in ("color", "hair", "eyes", "background")):
        return "qualifier_adjective"
    if "semantic_support" in lanes:
        return "semantic_support"
    return "generic_noun"


def issue32_fingerprint(record: Mapping[str, Any]) -> str:
    """Hash only translation-relevant #32 propositions."""

    # Issue #32 bridge v2 defines its meaning fingerprint over the exact
    # ``translation_visible_semantics`` object and uses a ``sha256:`` prefix.
    # Keep the legacy projection/hash contract unchanged for older fixtures.
    native_semantics = record.get("translation_visible_semantics")
    if isinstance(native_semantics, Mapping) and native_semantics:
        return f"sha256:{json_hash(dict(native_semantics))}"

    selected = issue32_propositions(record)
    if not selected and "meaning_fingerprint" in record:
        return str(record["meaning_fingerprint"])
    return json_hash(selected)


def issue32_propositions(record: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize only UI-JA translation-visible meaning propositions.

    This is an allowlist rather than a short list of whatever fields happen to
    exist in a #32 row.  In particular, generation metadata is intentionally
    ignored.  ``semantic_support_relation`` is included only when the UI-JA
    evaluation explicitly records that it used that relation as meaning
    context.
    """

    native_semantics = record.get("translation_visible_semantics")
    if isinstance(native_semantics, Mapping) and native_semantics:
        return dict(native_semantics)

    aliases = {
        "identity": ("identity", "candidate_canonical", "canonical_tag"),
        "entity_scope": ("entity_scope", "entity", "entity_type"),
        "canonical": ("canonical",),
        "count_cardinality": ("count_cardinality", "count", "cardinality"),
        "actor": ("actor",),
        "ownership": ("ownership", "owner"),
        "target": ("target", "special_tag"),
        "body_site": ("body_site", "body_part", "body_location"),
        "action_state": ("action_state", "action_vs_state", "action_or_state"),
        "intrinsic_relation": ("intrinsic_relation", "relation"),
        "pose": ("pose",),
        "spatial_requirement": ("spatial_requirement", "spatial_relation"),
        "required_modifier": ("required_modifier", "required_qualifier", "qualifier", "modifier"),
        "canonical_meaning_width": ("canonical_meaning_width", "meaning_width", "scope_width"),
    }
    selected: dict[str, Any] = {}
    nested = record.get("translation_visible_propositions")
    nested = nested if isinstance(nested, Mapping) else {}
    for normalized, candidates in aliases.items():
        value = next((nested[name] for name in (normalized, *candidates) if nested.get(name) not in (None, "", [], {})), None)
        if value in (None, "", [], {}):
            value = next((record[candidate] for candidate in candidates if record.get(candidate) not in (None, "", [], {})), None)
        if value not in (None, "", [], {}):
            selected[normalized] = value

    support_used = any(record.get(flag) is True for flag in (
        "semantic_support_used", "semantic_context_used", "semantic_support_relation_used",
    ))
    if support_used:
        for candidate in ("semantic_support_relation", "support_relation", "support_class"):
            if record.get(candidate) not in (None, "", [], {}):
                selected["semantic_support_relation"] = record[candidate]
                break
        if "semantic_support_relation" not in selected:
            for candidate in ("semantic_support_relation", "support_relation", "support_class"):
                if nested.get(candidate) not in (None, "", [], {}):
                    selected["semantic_support_relation"] = nested[candidate]
                    break
    return selected


def normalize_terms(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split("|") if item.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def term_class(term: str, canonical: str, *, explicit: str = "") -> str:
    """Type a candidate without treating it as semantic approval.

    Character shape is intentionally insufficient evidence for an orthographic
    variant.  The trusted evidence record must explicitly provide that class.
    """

    if explicit in TERM_CLASSES:
        return explicit
    if term == canonical:
        return "EXACT_SYNONYM"
    return "COMMON_EXACT_PARAPHRASE"


def search_equivalence_proven(record: Mapping[str, Any], typed_class: str) -> bool:
    """Return whether trusted evidence mechanically proves search equivalence."""

    if record.get("term_class") not in TERM_CLASSES:
        return False
    if typed_class == "ORTHOGRAPHIC_VARIANT":
        return bool(record.get("orthographic_evidence") or record.get("search_equivalence_proof") == "ORTHOGRAPHIC")
    return bool(
        record.get("exact_synonym_verified") is True
        or record.get("search_equivalence_proof") in {"EXACT", "VERIFIED_EXACT", "COMMON_EXACT"}
    )


def disallowed_search_reason(
    term: str,
    canonical: str,
    evidence: Mapping[str, Any] | None = None,
) -> str:
    """Return a reusable reason for a candidate that cannot be auto-accepted."""

    if not term.strip():
        return "EMPTY_TERM"
    evidence = evidence or {}
    for field in ("candidate_relation", "scope_relation", "search_scope_relation", "relation_type"):
        value = str(evidence.get(field, "")).strip().lower().replace(" ", "_")
        if value in _EVIDENCE_HAZARDS:
            return _EVIDENCE_HAZARDS[value]
    for field in ("source_type", "evidence_role"):
        value = str(evidence.get(field, "")).lower()
        if any(marker in value for marker in ("cooccurrence", "related_tag", "implication", "context_only")):
            return "RELATED_OR_IMPLICATION_ONLY"

    lowered = term.lower()
    canonical_lower = canonical.lower()
    if canonical_lower == "1girl" and any(word in term for word in ("ガールズイラスト", "女の子たち")):
        return "CATEGORY_OR_NOISY_ALIAS"
    if any(marker in term for marker in _ATTRIBUTE_MARKERS):
        if canonical_lower in {"1girl", "1boy", "girl", "boy"} or evidence.get("candidate_relation") == "attribute_added":
            return "ATTRIBUTE_ADDED"
    canonical_numbers = [int(value) for value in re.findall(r"\d+", canonical_lower)]
    term_numbers = [int(value) for value in re.findall(r"(?<!\d)(\d+)(?!\d)", term)]
    japanese_count_markers = ("一人", "1人", "二人", "2人", "三人", "3人", "ひとり", "ふたり", "さんにん")
    if canonical_numbers and not (term_numbers or any(marker in term for marker in japanese_count_markers)):
        return "COUNT_CHANGED_OR_MISSING"
    if canonical_numbers and term_numbers and term_numbers != canonical_numbers:
        return "COUNT_CHANGED_OR_MISSING"

    # This is a reusable composition rule: a solid-colour background is a
    # narrower subtype of a simple background, while the direct surface form
    # シンプル背景 does not trigger the narrowing rule.
    if "background" in canonical_lower and "単色" in term:
        return "NARROWER_THAN_CANONICAL"

    if canonical == "straddling" and any(word in term for word in ("騎乗位", "性行為")):
        return "SEXUAL_SUBTYPE_NARROWING"
    if canonical == "cuffs" and any(word in term for word in ("手錠", "手枷")):
        return "SUBTYPE_COLLISION_REQUIRES_SCOPE"
    if any(word in lowered for word in ("meme", "joke", "fanart")):
        return "MEME_JOKE_OR_FANDOM_PHRASE"
    return ""


def issue32_state(current: str, evaluated: str) -> str:
    if not current or not evaluated:
        return "READY"
    if current == evaluated:
        return "READY"
    return "STALE_REVIEW"


def bridge_conflict(record: Mapping[str, Any]) -> bool:
    """Read only an explicit conflict signal from frozen bridge evidence."""

    return any(record.get(field) is True for field in (
        "conflict_signal", "bridge_conflict", "independent_semantic_conflict", "semantic_conflict",
    ))


def derive_row_state(display_state: str, search_state: str, bridge_state: str) -> str:
    values = {display_state, search_state, bridge_state}
    if "CONTRADICTION" in values:
        return "CONTRADICTION"
    if "STALE_REVIEW" in values:
        return "STALE_REVIEW"
    if "REVIEW" in values:
        return "REVIEW"
    return "READY"


def count_values(rows: Iterable[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(field, "")) for row in rows).items()))


def protected_snapshot(root: Path) -> dict[str, str]:
    """Hash only protected boundaries; missing ignored local data is not an error."""

    paths: list[Path] = []
    for directory in (root / "data", root / "validation_quarantine"):
        if directory.exists():
            paths.extend(path for path in directory.rglob("*") if path.is_file())
    for relative in (
        "danbooru_tag_tool/ui.py",
        "tests/test_stage7a_ui.py",
        "docs/project/CURRENT_DEV_TASK.md",
    ):
        path = root / relative
        if path.exists():
            paths.append(path)
    result: dict[str, str] = {}
    for path in sorted(set(paths)):
        result[str(path.relative_to(root)).replace("\\", "/")] = file_hash(path)
    return result


def evidence_by_canonical(rows: Iterable[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        canonical = str(row.get("canonical", "")).strip()
        if canonical:
            result.setdefault(canonical, []).append(dict(row))
    return result


def semantic_evidence(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(row) for row in rows
        if row.get("evidence_role") == "SEMANTIC_SCOPE" and row.get("frozen") is True
    ]


def wording_candidates(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    result: list[str] = []
    for row in rows:
        if row.get("evidence_role") != "WORDING_CANDIDATE":
            continue
        for field in ("display_candidate", "candidate_display", "wording", "term"):
            result.extend(normalize_terms(row.get(field)))
    return list(dict.fromkeys(result))
