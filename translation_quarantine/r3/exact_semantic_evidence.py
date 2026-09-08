"""Reusable, fail-closed exact-canonical semantic evidence mechanism.

This module is intentionally independent from production translation and
search code.  It provides the boundary that future exact-canonical sources
can implement, a frozen evidence record, conservative deterministic
proposition extraction, validation, and the R3 risk gate.

The extractor never asks an LLM to fill a gap.  Every non-trivial proposition
must be supported by an exact source's introductory text; otherwise the row is
returned as REVIEW (or CONTRADICTION when the source contains conflicting
signals).
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from .r3_common import canonical_json_bytes, read_jsonl, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from r3_common import canonical_json_bytes, read_jsonl, write_json, write_jsonl


SCHEMA_VERSION = "exact-canonical-semantic-evidence-v1"
EXTRACTOR_VERSION = "deterministic-proposition-extractor-v1"
FIELD_NAMES = (
    "identity",
    "entity_scope",
    "actor",
    "ownership",
    "target",
    "body_site",
    "direction",
    "count",
    "intrinsic_relation",
    "spatial_requirement",
    "action_state",
    "required_modifier",
    "canonical_meaning_width",
)
RISK_ORDER = ("LOW", "MEDIUM", "HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _plain_wiki(value: str) -> str:
    """Normalize only markup; do not add semantic content."""

    text = html.unescape(value.replace("\r\n", "\n"))
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"!post\s+#\d+", "", text, flags=re.I)
    text = re.sub(r"^h[1-6]\.\s*.*$", "", text, flags=re.M | re.I)
    text = re.sub(r"^\s*[*#].*$", "", text, flags=re.M)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    return _clean(text)


def _intro(value: str) -> str:
    # Related tags/examples are not semantic authority for the page itself.
    text = _plain_wiki(value)
    return re.split(r"\b(?:Examples|Related tags|See also)\b", text, maxsplit=1, flags=re.I)[0].strip()


def _norm_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _canonical_words(canonical: str) -> list[str]:
    return [word for word in re.split(r"[_\-]+", canonical.lower()) if word]


_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
_MODIFIERS = {
    "black", "blue", "blonde", "brown", "closed", "curly", "dark", "female",
    "front", "green", "large", "light", "long", "male", "multiple", "pink",
    "purple", "red", "short", "small", "straight", "white", "yellow",
}
_BODY_SITES = {
    "abdomen", "arm", "arms", "back", "breast", "breasts", "cheek", "chest",
    "clitoris", "ear", "ears", "eye", "eyes", "face", "feet", "foot", "hand",
    "hands", "head", "hip", "hips", "knee", "leg", "legs", "mouth", "neck",
    "nipple", "nipples", "nose", "penis", "pussy", "thigh", "throat", "vagina",
}
_DIRECTION_WORDS = {
    "above", "away", "back", "backward", "below", "down", "front", "forward",
    "from", "left", "right", "toward", "towards", "up",
}
_ACTION_WORDS = {
    "attach", "attached", "bite", "bites", "bending", "bound", "carry", "carrying",
    "climb", "eating", "facing", "fighting", "holding", "hugging", "kissing",
    "licking", "looking", "open", "opening", "penetrating", "pulling", "push",
    "pushing", "reading", "running", "sitting", "standing", "straddling", "walking",
    "wearing", "wrapped",
}
_RELATION_WORDS = {
    "attached", "behind", "between", "inside", "near", "on", "over", "under",
    "surrounding", "through", "with", "within",
}


class ExactSourceAdapter(Protocol):
    """Adapter contract; adapters must return metadata plus raw payload."""

    adapter_id: str

    def acquire(self, canonical: str) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class FrozenEvidence:
    canonical: str
    adapter_id: str
    source_url: str
    revision: str
    content_hash: str
    raw_response_identity: str
    title: str
    body: str
    exact_title_match: bool
    frozen: bool = True
    http_status: int | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["provenance"] = dict(self.provenance)
        return result


class DanbooruWikiAdapter:
    """Live acquisition adapter.  It is never called by replay functions."""

    adapter_id = "danbooru_exact_canonical_wiki"

    def __init__(self, base_url: str = "https://danbooru.donmai.us/wiki_pages/") -> None:
        self.base_url = base_url.rstrip("/") + "/"

    def acquire(self, canonical: str) -> Mapping[str, Any]:
        url = self.base_url + quote(canonical, safe="") + ".json"
        request = Request(url, headers={"User-Agent": "DanbooruTagTool/exact-semantic-evidence-v1"})
        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read()
                payload = json.loads(raw.decode("utf-8"))
            title = _clean(payload.get("title"))
            return freeze_payload(
                canonical=canonical,
                adapter_id=self.adapter_id,
                source_url=url,
                revision=f"wiki_page_id:{payload.get('id', '')};updated_at:{payload.get('updated_at', '')}",
                raw_response=raw,
                title=title,
                body=_clean(payload.get("body")),
                exact_title_match=title == canonical,
                http_status=200,
                provenance={"acquisition": "live", "wiki_page_id": payload.get("id"), "updated_at": payload.get("updated_at")},
            ).as_dict()
        except HTTPError as exc:
            return freeze_payload(
                canonical=canonical, adapter_id=self.adapter_id, source_url=url, revision="",
                raw_response=b"", title="", body="", exact_title_match=False, http_status=int(exc.code),
                provenance={"acquisition": "live", "error": f"HTTP_{exc.code}"},
            ).as_dict()
        except (URLError, TimeoutError, ValueError, OSError) as exc:
            return freeze_payload(
                canonical=canonical, adapter_id=self.adapter_id, source_url=url, revision="",
                raw_response=b"", title="", body="", exact_title_match=False, http_status=None,
                provenance={"acquisition": "live", "error": type(exc).__name__},
            ).as_dict()


def freeze_payload(*, canonical: str, adapter_id: str, source_url: str, revision: str,
                   raw_response: bytes, title: str, body: str, exact_title_match: bool,
                   http_status: int | None, provenance: Mapping[str, Any] | None = None) -> FrozenEvidence:
    """Create a durable evidence record; content identity is never inferred."""

    raw_identity = sha256_bytes(raw_response) if raw_response else ""
    content_hash = sha256_bytes(raw_response) if raw_response else ""
    return FrozenEvidence(
        canonical=canonical, adapter_id=adapter_id, source_url=source_url,
        revision=revision, content_hash=content_hash, raw_response_identity=raw_identity,
        title=title, body=body, exact_title_match=exact_title_match,
        frozen=True, http_status=http_status, provenance=dict(provenance or {}),
    )


class FrozenEvidenceStore:
    """Read-only replay store.  No adapter or network call is reachable here."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[FrozenEvidence]:
        rows = read_jsonl(self.path)
        result: list[FrozenEvidence] = []
        for row in rows:
            raw_identity = _clean(row.get("raw_response_identity") or row.get("raw_response_sha256"))
            if raw_identity and not raw_identity.startswith("sha256:"):
                raw_identity = "sha256:" + raw_identity
            provenance = dict(row.get("provenance")) if isinstance(row.get("provenance"), Mapping) else {}
            for key in ("wiki_page_id", "updated_at", "other_names", "semantic_status", "fetch_error"):
                if key in row:
                    provenance[key] = row[key]
            provenance["store"] = str(self.path)
            result.append(FrozenEvidence(
                canonical=_clean(row.get("canonical")),
                adapter_id=_clean(row.get("adapter_id") or row.get("source_type")),
                source_url=_clean(row.get("source_url")),
                revision=_clean(row.get("revision")),
                content_hash=_clean(row.get("content_hash") or row.get("content_identity")),
                raw_response_identity=raw_identity,
                title=_clean(row.get("title")), body=str(row.get("body") or ""),
                exact_title_match=row.get("exact_title_match") is True,
                frozen=row.get("frozen") is True,
                http_status=row.get("http_status") if isinstance(row.get("http_status"), int) else None,
                provenance=provenance,
            ))
        return result


@dataclass(frozen=True)
class PropositionSet:
    canonical: str
    fields: Mapping[str, Any]
    required_fields: tuple[str, ...]
    evidence_spans: Mapping[str, str]
    extractor_version: str = EXTRACTOR_VERSION
    ambiguities: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "canonical": self.canonical, "fields": dict(self.fields),
            "required_fields": list(self.required_fields), "evidence_spans": dict(self.evidence_spans),
            "extractor_version": self.extractor_version, "ambiguities": list(self.ambiguities),
        }


@dataclass(frozen=True)
class ValidationResult:
    canonical: str
    status: str
    missing_fields: tuple[str, ...]
    errors: tuple[str, ...]
    authority_ok: bool
    proposition_complete: bool
    evidence_identity_ok: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self) | {"missing_fields": list(self.missing_fields), "errors": list(self.errors)}


def _first(pattern: str, text: str, flags: int = re.I) -> str:
    match = re.search(pattern, text, flags)
    return _clean(match.group(1)) if match else ""


def _count(text: str, canonical: str) -> int | str | None:
    match = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", text, re.I)
    if match:
        value = match.group(1).lower()
        return int(value) if value.isdigit() else _NUMBERS[value]
    for token in _canonical_words(canonical):
        if token.isdigit():
            return int(token)
        if token in _NUMBERS:
            return _NUMBERS[token]
    if "multiple" in text.lower():
        return "multiple"
    return None


def extract_propositions(evidence: FrozenEvidence) -> PropositionSet:
    """Extract only explicit propositions from the exact page introduction."""

    intro = _intro(evidence.body)
    sentence = re.split(r"[.!?]", intro, maxsplit=1)[0].strip()
    canonical = evidence.canonical
    lower = sentence.lower()
    words = _canonical_words(canonical)
    fields: dict[str, Any] = {name: None for name in FIELD_NAMES}
    spans: dict[str, str] = {}
    ambiguities: list[str] = []

    fields["identity"] = canonical if evidence.exact_title_match else None
    if fields["identity"]:
        spans["identity"] = evidence.title

    entity = _first(r"\b(?:depicting|containing|showing|of)\s+(?:a|an|the\s+)?(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)?\s*([^.;]+)", intro)
    if not entity:
        entity = _first(r"^(?:a|an|the)?\s*((?:[a-z]+\s+){0,3}(?:hair|eyes|face|head|hand|hands|body|character|characters|wing|wings|tail|dress|shirt|bikini))\.?$", intro)
    if not entity:
        entity = _first(r"^(?:a|an|the)\s+((?:[a-z]+\s+){0,3}(?:character|characters|hair|eyes|hand|hands|body|wings?))\b", intro)
    if not entity:
        phrase = " ".join(words)
        if phrase and phrase in lower:
            entity = phrase
    if entity:
        entity = re.sub(r"^(?:a|an|the)\s+", "", entity, flags=re.I)
        entity = re.sub(r"\s+(?:may|can|only|who)\b.*$", "", entity, flags=re.I)
        fields["entity_scope"] = _clean(entity)
        spans["entity_scope"] = entity

    count = _count(intro, canonical)
    if count is not None and (bool(re.match(r"^\d+", canonical)) or any(token.isdigit() or token in _NUMBERS or token == "multiple" for token in words) or re.search(r"\b(?:one|two|three|four|five|six|multiple)\b", lower)):
        fields["count"] = count
        spans["count"] = str(count)

    modifier_hits = [token for token in words if token in _MODIFIERS and re.search(rf"\b{re.escape(token)}\b", lower)]
    for token in ("male", "female"):
        if token in lower.split() and token not in modifier_hits:
            modifier_hits.append(token)
    if modifier_hits:
        fields["required_modifier"] = modifier_hits
        spans["required_modifier"] = ", ".join(modifier_hits)

    body_hits = sorted({word for word in _BODY_SITES if re.search(rf"\b{re.escape(word)}\b", lower)})
    body_site = _first(r"\b(?:on|at|from|around|over|under)\s+(?:the|a|an|another person's)\s+([a-z -]+?)(?:\b(?:and|that|which|where)\b|[.;]|$)", intro)
    if body_site:
        body_site = body_site.rstrip()
    if body_site and any(word in body_site.lower().split() for word in _BODY_SITES):
        fields["body_site"] = body_site
        spans["body_site"] = body_site
    elif len(body_hits) == 1 and any(token in _BODY_SITES for token in words):
        fields["body_site"] = body_hits[0]
        spans["body_site"] = body_hits[0]

    actor = _first(r"\b(?:held|carried|worn|owned|attached)\s+by\s+([^.;]+)", intro)
    owner = _first(r"\b([^.;]+?)['’]s\s+[^.;]+", intro)
    if actor:
        fields["actor"] = actor
        spans["actor"] = actor
    if owner:
        fields["ownership"] = owner
        spans["ownership"] = owner

    target = _first(r"\b(?:holding|hugging|kissing|licking|facing|looking at|carrying|wearing)\s+(?:a|an|the)\s+([^.;]+)", intro)
    if target:
        fields["target"] = target
        spans["target"] = target

    directions = sorted({word for word in _DIRECTION_WORDS if re.search(rf"\b{re.escape(word)}\b", lower)})
    direction_phrase = _first(r"\b((?:from|toward|towards|away from|to)\s+(?:the\s+)?[a-z -]+)", intro)
    if direction_phrase:
        fields["direction"] = direction_phrase
        spans["direction"] = direction_phrase
    elif len(directions) == 1 and any(token in _DIRECTION_WORDS for token in words):
        fields["direction"] = directions[0]
        spans["direction"] = directions[0]
    elif len(directions) > 1 and any(token in _DIRECTION_WORDS for token in words):
        ambiguities.append("multiple_directions")

    relation_hits = sorted({word for word in _RELATION_WORDS | {"holding", "facing"} if re.search(rf"\b{re.escape(word)}\b", lower)})
    if relation_hits:
        fields["intrinsic_relation"] = relation_hits
        spans["intrinsic_relation"] = ", ".join(relation_hits)
    if relation_hits or any(word in lower for word in ("between", "inside", "behind", "under", "on top", "surrounding")):
        fields["spatial_requirement"] = True
        spans["spatial_requirement"] = "explicit spatial relation in introduction"

    action_hits = sorted({word for word in _ACTION_WORDS if re.search(rf"\b{re.escape(word)}\b", lower)})
    state_hits = bool(re.search(r"(?<![a-z])(?:is|are|has|have|contains?|depicts?|shows?|visible|present|hair|eyes|color)(?![a-z])", lower))
    if action_hits and state_hits and any(word in lower for word in ("is", "are", "contains", "depicts", "shows")):
        ambiguities.append("action_and_state_signals")
    elif action_hits:
        fields["action_state"] = "action"
        spans["action_state"] = ", ".join(action_hits)
    elif state_hits:
        fields["action_state"] = "state"
        spans["action_state"] = "explicit state/attribute wording"
    else:
        fields["action_state"] = "not_applicable"

    if fields["entity_scope"] and fields["required_modifier"]:
        fields["canonical_meaning_width"] = "entity plus explicit required modifier"
        spans["canonical_meaning_width"] = "entity_scope + required_modifier"
    elif fields["entity_scope"]:
        fields["canonical_meaning_width"] = "entity scope"
        spans["canonical_meaning_width"] = "entity_scope"

    required: list[str] = ["identity", "entity_scope"]
    if any(token.isdigit() or token in _NUMBERS or token == "multiple" for token in words):
        required.append("count")
    if any(token in _BODY_SITES for token in words) or body_site:
        required.append("body_site")
    if any(token in _DIRECTION_WORDS for token in words):
        required.append("direction")
    if any(token in {"between", "with", "on", "under", "behind", "inside", "holding", "facing"} for token in words):
        required.append("intrinsic_relation")
    if any(token in _ACTION_WORDS for token in words):
        required.append("action_state")
    if (len(words) > 1 and any(token in _MODIFIERS for token in words)) or (bool(re.match(r"^\d+", canonical)) and modifier_hits):
        required.append("required_modifier")
    if fields["actor"] and fields["target"]:
        required.extend(("actor", "target"))
    required = list(dict.fromkeys(required))
    return PropositionSet(canonical, fields, tuple(required), spans, ambiguities=tuple(ambiguities))


def validate_propositions(evidence: FrozenEvidence, propositions: PropositionSet) -> ValidationResult:
    errors: list[str] = []
    authority_ok = bool(
        evidence.frozen and evidence.exact_title_match and evidence.source_url and evidence.revision
        and evidence.content_hash and evidence.raw_response_identity and evidence.content_hash == evidence.raw_response_identity
        and evidence.http_status == 200
    )
    if not authority_ok:
        errors.append("EXACT_CANONICAL_AUTHORITY_UNAVAILABLE")
    missing = tuple(field for field in propositions.required_fields if propositions.fields.get(field) in (None, "", [], {}))
    if missing:
        errors.append("PROPOSITION_INCOMPLETE")
    if propositions.ambiguities:
        errors.append("PROPOSITION_AMBIGUOUS")
    if propositions.fields.get("identity") != evidence.canonical:
        errors.append("IDENTITY_OR_TITLE_MISMATCH")
    if propositions.fields.get("canonical_meaning_width") is None:
        errors.append("CANONICAL_WIDTH_UNSPECIFIED")
    if propositions.ambiguities:
        # Ambiguous source language is a REVIEW condition.  CONTRADICTION is
        # reserved for an explicit conflicting evidence record, never for a
        # parser heuristic that merely sees more than one signal.
        status = "AMBIGUOUS"
    elif errors:
        status = "INCOMPLETE"
    else:
        status = "VALIDATED"
    return ValidationResult(
        canonical=evidence.canonical, status=status, missing_fields=missing,
        errors=tuple(dict.fromkeys(errors)), authority_ok=authority_ok,
        proposition_complete=not missing and not propositions.ambiguities,
        evidence_identity_ok=bool(evidence.content_hash and evidence.raw_response_identity and evidence.content_hash == evidence.raw_response_identity),
    )


def risk_gate(evidence: FrozenEvidence, propositions: PropositionSet, validation: ValidationResult, risk_class: str) -> dict[str, Any]:
    """Apply R3 without promotion shortcuts; only VALIDATED can be READY."""

    high_or_critical = risk_class.startswith("HIGH") or risk_class == "CRITICAL"
    ready = validation.status == "VALIDATED" and validation.proposition_complete and validation.authority_ok
    if high_or_critical:
        ready = ready and evidence.exact_title_match and evidence.adapter_id.startswith("danbooru_exact_canonical_wiki") or (ready and evidence.exact_title_match and bool(evidence.adapter_id))
    return {
        "canonical": evidence.canonical, "risk_class": risk_class,
        "decision": "READY" if ready else "REVIEW",
        "validation_status": validation.status,
        "exact_authority_required": high_or_critical,
        "exact_authority_satisfied": validation.authority_ok,
        "required_fields": list(propositions.required_fields),
        "missing_fields": list(validation.missing_fields),
        "reason_codes": list(validation.errors),
        "proposition_hash": sha256_json(propositions.as_dict()),
        "source_url": evidence.source_url, "revision": evidence.revision,
        "content_hash": evidence.content_hash, "raw_response_identity": evidence.raw_response_identity,
        "frozen": evidence.frozen, "production_modified": False,
    }


def process_frozen_rows(evidence_rows: Iterable[FrozenEvidence], risk_by_canonical: Mapping[str, str]) -> dict[str, list[dict[str, Any]]]:
    propositions: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    handoff: list[dict[str, Any]] = []
    for evidence in sorted(evidence_rows, key=lambda row: row.canonical):
        extracted = extract_propositions(evidence)
        validation = validate_propositions(evidence, extracted)
        gate = risk_gate(evidence, extracted, validation, risk_by_canonical.get(evidence.canonical, "LOW"))
        propositions.append({"canonical": evidence.canonical, "evidence": evidence.as_dict(), "propositions": extracted.as_dict()})
        validations.append({"canonical": evidence.canonical, **validation.as_dict()})
        gates.append(gate)
        handoff.append({
            "canonical": evidence.canonical,
            "semantic_status": gate["decision"],
            "wording_route": "READY_FOR_WORDING_REVIEW" if gate["decision"] == "READY" else "PARKED",
            "search_route": "BLOCKED_UNTIL_WORDING_AND_EQUIVALENCE_PROOF" if gate["decision"] == "READY" else "PARKED",
            "reason_codes": gate["reason_codes"] or (["SEMANTIC_SCOPE_VALIDATED"] if gate["decision"] == "READY" else []),
            "production_modified": False,
        })
    return {"propositions": propositions, "validations": validations, "risk_gates": gates, "handoff": handoff}


def write_run_artifacts(output: Path, rows: Mapping[str, list[dict[str, Any]]]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output / "propositions.jsonl", rows["propositions"])
    write_jsonl(output / "validations.jsonl", rows["validations"])
    write_jsonl(output / "risk_gates.jsonl", rows["risk_gates"])
    write_jsonl(output / "wording_search_handoff.jsonl", rows["handoff"])
