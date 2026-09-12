"""Browse providers for the Issue #66 v1 application shell."""
from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Protocol

from .knowledge import TagKnowledgeCore
from .normalization import normalize_lookup
from .prompt_formatter import PromptFormatter


@dataclass(frozen=True, slots=True)
class BrowseEntry:
    item_id: str
    japanese: str
    english: str
    canonical: str | None
    source: str
    category: str = ""


class BrowseProvider(Protocol):
    @property
    def available(self) -> bool: ...

    @property
    def status_text(self) -> str: ...

    def categories(self) -> tuple[str, ...]: ...

    def browse(self, *, category: str = "", subcategory: str = "", query: str = "",
               limit: int = 200) -> tuple[BrowseEntry, ...]: ...


class SpecialBrowseProvider:
    """Read-only browser over the accepted Issue #56 2,788-row UI taxonomy.

    The #56 sidecar is UI navigation metadata only. It never changes Special
    identity, canonical linkage, product-fit eligibility, or search behavior.
    Rows deliberately left without a browse path by #56 remain search-visible
    but are not force-fit into a misleading shelf here.
    """

    TAXONOMY_REL = Path("docs/issue56/rollout/issue56_ui_genre_taxonomy_v1.json")
    PILOT_REL = Path("docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv")
    REVIEWED_REL = Path("docs/issue56/rollout/reviewed")

    def __init__(self, knowledge: TagKnowledgeCore, root: Path):
        self.knowledge = knowledge
        self.root = Path(root)
        self._genre_order: list[str] = []
        self._genre_labels: dict[str, str] = {}
        self._genre_by_label: dict[str, str] = {}
        self._subgenre_order: dict[str, list[str]] = {}
        self._subgenre_labels: dict[tuple[str, str], str] = {}
        self._subgenre_by_label: dict[tuple[str, str], str] = {}
        self._paths_by_special: dict[str, tuple[tuple[str, str], ...]] = {}
        self._load_taxonomy()
        self._load_mapping()

    @property
    def available(self) -> bool:
        return True

    @property
    def status_text(self) -> str:
        return "Special Core Dictionary / Issue #56 accepted browse taxonomy"

    @property
    def mapped_count(self) -> int:
        return len(self._paths_by_special)

    @property
    def browsable_count(self) -> int:
        return sum(bool(paths) for paths in self._paths_by_special.values())

    def categories(self) -> tuple[str, ...]:
        return tuple(self._genre_labels[genre_id] for genre_id in self._genre_order)

    def subcategories(self, category: str) -> tuple[str, ...]:
        genre_id = self._genre_by_label.get(category)
        if genre_id is None:
            return ()
        return tuple(self._subgenre_labels[(genre_id, subgenre_id)]
                     for subgenre_id in self._subgenre_order[genre_id])

    def browse(self, *, category: str = "", subcategory: str = "", query: str = "",
               limit: int = 200) -> tuple[BrowseEntry, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        key = normalize_lookup(query)
        genre_id = self._genre_by_label.get(category) if category else None
        if category and genre_id is None:
            return ()
        subgenre_id = None
        if subcategory:
            if genre_id is None:
                return ()
            subgenre_id = self._subgenre_by_label.get((genre_id, subcategory))
            if subgenre_id is None:
                return ()

        rows: list[BrowseEntry] = []
        for special_id, paths in self._paths_by_special.items():
            # Product-fit #63 is authoritative for normal browse exposure.
            if not self.knowledge.product_fit.allows(special_id, "browse"):
                continue
            if not paths:
                continue
            matched_paths = self._matching_paths(paths, genre_id, subgenre_id)
            if (genre_id is not None or subgenre_id is not None) and not matched_paths:
                continue
            special = self.knowledge.special[special_id]
            if key:
                haystacks = (special.term, special.japanese, special.description, *special.search_keys)
                if not any(key in normalize_lookup(value) for value in haystacks if value):
                    continue
            display_paths = matched_paths or paths
            rows.append(BrowseEntry(
                special.special_id,
                special.japanese,
                PromptFormatter.format_special(special).text,
                special.chosen_canonical,
                "Special",
                " / ".join(self._path_label(path) for path in display_paths),
            ))
        rows.sort(key=lambda row: (normalize_lookup(row.japanese), row.english, int(row.item_id)))
        return tuple(rows[:limit])

    def _matching_paths(self, paths, genre_id: str | None, subgenre_id: str | None):
        if genre_id is None:
            return paths
        return tuple(path for path in paths
                     if path[0] == genre_id and (subgenre_id is None or path[1] == subgenre_id))

    def _path_label(self, path: tuple[str, str]) -> str:
        genre_id, subgenre_id = path
        label = self._genre_labels[genre_id]
        if subgenre_id:
            label += " > " + self._subgenre_labels[(genre_id, subgenre_id)]
        return label

    def _load_taxonomy(self) -> None:
        payload = json.loads((self.root / self.TAXONOMY_REL).read_text(encoding="utf-8"))
        if payload.get("status") != "FROZEN_FOR_FULL_ROLLOUT":
            raise ValueError("Issue #56 browse taxonomy is not frozen")
        genres = payload.get("genres")
        if not isinstance(genres, list) or len(genres) != 14:
            raise ValueError("Issue #56 browse taxonomy must contain 14 genres")
        for genre in genres:
            genre_id = str(genre.get("id", "")).strip()
            label = str(genre.get("label_ja", "")).strip()
            if not genre_id or not label or genre_id in self._genre_labels or label in self._genre_by_label:
                raise ValueError("Invalid Issue #56 genre")
            self._genre_order.append(genre_id)
            self._genre_labels[genre_id] = label
            self._genre_by_label[label] = genre_id
            self._subgenre_order[genre_id] = []
            for subgenre in genre.get("subgenres", []):
                sub_id = str(subgenre.get("id", "")).strip()
                sub_label = str(subgenre.get("label_ja", "")).strip()
                key = (genre_id, sub_id)
                label_key = (genre_id, sub_label)
                if not sub_id or not sub_label or key in self._subgenre_labels or label_key in self._subgenre_by_label:
                    raise ValueError("Invalid Issue #56 subgenre")
                self._subgenre_order[genre_id].append(sub_id)
                self._subgenre_labels[key] = sub_label
                self._subgenre_by_label[label_key] = sub_id
        if len(self._subgenre_labels) != 38:
            raise ValueError("Issue #56 browse taxonomy must contain 38 subgenres")

    def _load_mapping(self) -> None:
        mapping: dict[str, tuple[tuple[str, str], ...]] = {}
        sources = [self.root / self.PILOT_REL]
        reviewed = self.root / self.REVIEWED_REL
        sources.extend(sorted(reviewed.glob("*.csv")))
        for path in sources:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                required = {"special_id", "primary_genre_id", "primary_subgenre_id",
                            "secondary_paths", "classification_status"}
                if reader.fieldnames is None or not required <= set(reader.fieldnames):
                    raise ValueError(f"Invalid Issue #56 mapping columns: {path}")
                for row in reader:
                    special_id = str(row["special_id"]).strip()
                    if special_id in mapping:
                        raise ValueError(f"Duplicate Issue #56 mapping: {special_id}")
                    if special_id not in self.knowledge.special:
                        raise ValueError(f"Unknown Special ID in Issue #56 mapping: {special_id}")
                    paths: list[tuple[str, str]] = []
                    primary_genre = str(row["primary_genre_id"] or "").strip()
                    primary_subgenre = str(row["primary_subgenre_id"] or "").strip()
                    if primary_genre:
                        self._validate_path(primary_genre, primary_subgenre)
                        paths.append((primary_genre, primary_subgenre))
                    elif primary_subgenre:
                        raise ValueError(f"Subgenre without genre for Special {special_id}")
                    for raw_path in str(row["secondary_paths"] or "").split("|"):
                        raw_path = raw_path.strip()
                        if not raw_path:
                            continue
                        parts = raw_path.split(">", 1)
                        genre_id = parts[0].strip()
                        subgenre_id = parts[1].strip() if len(parts) == 2 else ""
                        self._validate_path(genre_id, subgenre_id)
                        path_tuple = (genre_id, subgenre_id)
                        if path_tuple not in paths:
                            paths.append(path_tuple)
                    mapping[special_id] = tuple(paths)
        if set(mapping) != set(self.knowledge.special):
            missing = set(self.knowledge.special) - set(mapping)
            extra = set(mapping) - set(self.knowledge.special)
            raise ValueError(f"Issue #56 mapping coverage mismatch: missing={len(missing)} extra={len(extra)}")
        self._paths_by_special = mapping

    def _validate_path(self, genre_id: str, subgenre_id: str) -> None:
        if genre_id not in self._genre_labels:
            raise ValueError(f"Unknown Issue #56 genre: {genre_id}")
        if subgenre_id and (genre_id, subgenre_id) not in self._subgenre_labels:
            raise ValueError(f"Unknown Issue #56 subgenre: {genre_id}>{subgenre_id}")


class PendingGeneralBrowseProvider:
    """Stable v1 boundary for the parallel Issue #64 accepted sidecar."""

    @property
    def available(self) -> bool:
        return False

    @property
    def status_text(self) -> str:
        return "General browse は Issue #64 の accepted sidecar 待ちです。検索は利用できます。"

    def categories(self) -> tuple[str, ...]:
        return ()

    def browse(self, *, category: str = "", subcategory: str = "", query: str = "",
               limit: int = 200) -> tuple[BrowseEntry, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        return ()
