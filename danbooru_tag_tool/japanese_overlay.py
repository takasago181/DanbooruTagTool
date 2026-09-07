"""Read-only Japanese display/search overlay for local runtime use."""
from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from types import MappingProxyType

from .normalization import normalize_lookup


JAPANESE_USAGES = frozenset({"display", "search", "candidate", "rejected"})
TERM_COLUMNS = ("canonical_tag", "ja_term", "usage", "source_id")


@dataclass(frozen=True, slots=True)
class JapaneseTerm:
    canonical_tag: str
    ja_term: str
    usage: str
    source_id: str

    def __post_init__(self):
        if (not self.canonical_tag or not self.ja_term.strip() or not self.source_id
                or self.usage not in JAPANESE_USAGES):
            raise ValueError("Invalid Japanese term")


def load_japanese_terms(path: Path) -> tuple[JapaneseTerm, ...]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(TERM_COLUMNS):
            raise ValueError("Unexpected Japanese term columns/order")
        terms = tuple(JapaneseTerm(**row) for row in reader)
    identities = {(term.canonical_tag, term.ja_term) for term in terms}
    if len(identities) != len(terms):
        raise ValueError("Duplicate Japanese term identity")
    return terms


@dataclass(frozen=True, slots=True)
class JapaneseOverlay:
    """Runtime-safe terms only; candidate and rejected rows are never represented."""

    display_by_canonical: MappingProxyType
    search_by_canonical: MappingProxyType

    @classmethod
    def empty(cls) -> "JapaneseOverlay":
        return cls(MappingProxyType({}), MappingProxyType({}))

    @classmethod
    def from_terms(cls, terms: tuple[JapaneseTerm, ...], canonical) -> "JapaneseOverlay":
        display: dict[str, str] = {}
        search: dict[str, list[str]] = {}
        identities = set()
        for term in terms:
            if term.canonical_tag not in canonical:
                raise ValueError("Japanese term references unknown canonical")
            identity = (term.canonical_tag, term.ja_term)
            if identity in identities:
                raise ValueError("Duplicate Japanese term identity")
            identities.add(identity)
            if term.usage == "display":
                if term.canonical_tag in display:
                    raise ValueError("At most one display term per canonical")
                display[term.canonical_tag] = term.ja_term
            if term.usage in {"display", "search"}:
                search.setdefault(term.canonical_tag, []).append(term.ja_term)
        return cls(
            MappingProxyType(dict(sorted(display.items()))),
            MappingProxyType({canonical_tag: tuple(dict.fromkeys(values))
                              for canonical_tag, values in sorted(search.items())}),
        )

    @classmethod
    def load(cls, path: Path, canonical) -> "JapaneseOverlay":
        path = Path(path)
        if not path.exists():
            return cls.empty()
        document = json.loads(path.read_text(encoding="utf-8"))
        if set(document) != {"format_version", "entries"} or document["format_version"] != 1:
            raise ValueError("Unexpected Japanese overlay format")
        entries = document["entries"]
        if not isinstance(entries, dict):
            raise ValueError("Japanese overlay entries must be an object")
        terms = []
        for canonical_tag, value in entries.items():
            if set(value) != {"display_ja", "search_ja"}:
                raise ValueError("Unexpected Japanese overlay entry")
            display = value["display_ja"]
            search = value["search_ja"]
            if display is not None:
                terms.append(JapaneseTerm(canonical_tag, display, "display", "runtime"))
            if not isinstance(search, list) or any(not isinstance(item, str) or not item for item in search):
                raise ValueError("Invalid Japanese overlay search terms")
            for item in search:
                if item != display:
                    terms.append(JapaneseTerm(canonical_tag, item, "search", "runtime"))
        return cls.from_terms(tuple(terms), canonical)

    def to_document(self) -> dict:
        entries = {}
        for canonical_tag in sorted(self.search_by_canonical):
            entries[canonical_tag] = {
                "display_ja": self.display_by_canonical.get(canonical_tag),
                "search_ja": list(self.search_by_canonical[canonical_tag]),
            }
        return {"format_version": 1, "entries": entries}

    def lookup(self) -> dict[str, tuple[str, ...]]:
        result: dict[str, list[str]] = {}
        for canonical_tag, terms in self.search_by_canonical.items():
            for term in terms:
                key = normalize_lookup(term)
                result.setdefault(key, []).append(canonical_tag)
        return {key: tuple(dict.fromkeys(values)) for key, values in result.items()}
