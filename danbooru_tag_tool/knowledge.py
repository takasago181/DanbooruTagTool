"""Static CSV loaders and exact resolution only; no search ranking or statistics."""
import csv
from dataclasses import dataclass
from pathlib import Path

from .models import CanonicalTag, CoreTagSet, SemanticCandidate, SpecialTag, Translation
from .normalization import normalize_lookup
from .japanese_overlay import JapaneseOverlay
from .generation_profile import (
    GenerationProfileStore, load_generation_profiles, join_generation_profiles,
)
from .ruleset2 import Ruleset2Store


def _rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


def _add(index, key, value):
    values = index.setdefault(normalize_lookup(key), [])
    if value not in values:
        values.append(value)


def load_canonical(path: Path) -> dict[str, CanonicalTag]:
    result = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.reader(stream):
            if len(row) != 4:
                raise ValueError("Expected headerless four-column dictionary")
            name, category, count, _ = row
            if name in result:
                raise ValueError(f"Duplicate canonical: {name}")
            result[name] = CanonicalTag(name, int(category), int(count))
    return result


def load_aliases(path: Path, canonical) -> dict[str, tuple[str, ...]]:
    result = {}
    seen = set()
    for row in _rows(path):
        key = row["NormalizedAlias"]
        if key in seen:
            raise ValueError(f"Duplicate source alias key: {key}")
        seen.add(key)
        targets = ((row["CanonicalTargets"],) if int(row["TargetCount"]) == 1
                   else tuple(row["CanonicalTargets"].split(";")))
        if len(set(targets)) != int(row["TargetCount"]) or not set(targets) <= canonical.keys():
            raise ValueError(f"Invalid alias targets: {key}")
        for target in targets:
            _add(result, key, target)
    return {key: tuple(values) for key, values in result.items()}


def load_special(source_path: Path, linkage_path: Path, canonical, aliases):
    linkage = {}
    for row in _rows(linkage_path):
        if row["ID"] in linkage:
            raise ValueError("Duplicate linkage ID")
        linkage[row["ID"]] = row
    result = {}
    for row in _rows(source_path):
        sid = row["ID"]
        if sid in result or sid not in linkage:
            raise ValueError("Duplicate/missing Special ID")
        link = linkage[sid]
        if any(row[key] != link[key] for key in row):
            raise ValueError(f"Special source/linkage mismatch: {sid}")
        raw_targets = link["CanonicalTargets"]
        targets = ((raw_targets,) if raw_targets in canonical
                   else tuple(filter(None, raw_targets.split(";"))))
        chosen = link["ChosenCanonicalTag"] or None
        typ = link["SourceMatchType"]
        if not set(targets) <= canonical.keys() or (chosen and chosen not in targets):
            raise ValueError("Invalid Special canonical reference")
        if typ == "semantic_unmapped":
            valid = row["Layer"] == "Semantic" and not targets and chosen is None
        elif typ == "canonical":
            valid = (row["Layer"] in {"Core", "Extended"} and len(targets) == 1
                     and chosen == targets[0]
                     and normalize_lookup(chosen) == normalize_lookup(row["Tag"]))
        elif typ in {"alias_unique", "alias_ambiguous_curated", "alias_ambiguous_multiple"}:
            valid = row["Layer"] == "Alias" and set(targets) == set(aliases.get(normalize_lookup(row["Tag"]), ()))
            valid &= ((len(targets) == 1 and chosen is not None) if typ == "alias_unique"
                      else (len(targets) > 1 and ((chosen is None) == (typ == "alias_ambiguous_multiple"))))
        else:
            valid = False
        if not valid:
            raise ValueError(f"Invalid Special linkage behavior: {sid}")
        result[sid] = SpecialTag(sid, row["Tag"], row["日本語"], row["元の日本語説明"],
                                 row["Layer"], row["元カテゴリ"], chosen, typ, targets)
    if result.keys() != linkage.keys():
        raise ValueError("Special/linkage ID sets differ")
    return result


RELATIONS = frozenset({"exact-ish", "alias-like", "broader", "narrower", "related", "UNMAPPED"})
REVIEW_STATUSES = frozenset({"UNREVIEWED", "REVIEWED", "REJECTED"})


def load_semantic(path: Path, canonical, special) -> dict[str, SemanticCandidate]:
    result = {}
    for row in _rows(path):
        if set(row) != set(SemanticCandidate.__dataclass_fields__):
            raise ValueError("Unexpected semantic columns (counts are not permitted)")
        sid = row["semantic_id"]
        target = row["candidate_canonical"] or None
        source = special.get(row["special_id"])
        if not sid or sid in result:
            raise ValueError("Duplicate/empty semantic_id")
        if source is None or source.layer != "Semantic" or source.term != row["semantic_term"]:
            raise ValueError("Invalid semantic Special reference")
        if row["relation_type"] not in RELATIONS or row["review_status"] not in REVIEW_STATUSES:
            raise ValueError("Invalid semantic relation/review status")
        if (target is None) != (row["relation_type"] == "UNMAPPED"):
            raise ValueError("UNMAPPED must have no canonical candidate")
        if target is not None and target not in canonical:
            raise ValueError("Unknown semantic canonical candidate")
        row["candidate_canonical"] = target
        result[sid] = SemanticCandidate(**row)
    return result


@dataclass(frozen=True, slots=True)
class ExactResolution:
    match_type: str
    canonical_candidates: tuple[str, ...] = ()
    special_ids: tuple[str, ...] = ()
    semantic_ids: tuple[str, ...] = ()

    @property
    def resolved_canonical(self) -> str | None:
        # Semantic candidates never become a silent canonical resolution.
        if len(self.canonical_candidates) == 1 and not self.semantic_ids:
            return self.canonical_candidates[0]
        return None


class TagKnowledgeCore:
    def __init__(self, canonical, aliases, special, semantic, translations=(), japanese_overlay=None,
                 ruleset2=None):
        self.canonical = canonical
        self.aliases = aliases
        self.special = special
        self.semantic = semantic
        self.translations = tuple(translations)
        self.japanese_overlay = japanese_overlay or JapaneseOverlay.empty()
        self.ruleset2 = ruleset2
        self.semantic_routes = ruleset2.semantic_routes if ruleset2 is not None else {}
        self.canonical_lookup = {}
        self.japanese_lookup = {}
        self.special_lookup = {}
        self.special_search_lookup = {}
        self.semantic_lookup = {}
        self.special_to_semantic_ids = {}
        for tag in canonical.values():
            _add(self.canonical_lookup, tag.lookup_key, tag.canonical_tag)
        for tag in special.values():
            _add(self.special_lookup, tag.term, tag.special_id)
            _add(self.japanese_lookup, tag.japanese, tag.special_id)
            for search_key in tag.search_keys:
                _add(self.special_search_lookup, search_key, tag.special_id)
        self.translation_lookup = {}
        for item in self.translations:
            if item.canonical_tag not in canonical:
                raise ValueError("Unknown translation canonical")
            _add(self.translation_lookup, item.japanese, item.canonical_tag)
        self.overlay_lookup = self.japanese_overlay.lookup()
        for item in semantic.values():
            self.special_to_semantic_ids.setdefault(item.special_id, []).append(item.semantic_id)
            for term in (item.semantic_term, item.ja_label, item.en_concept):
                if term:
                    _add(self.semantic_lookup, term, item.semantic_id)
        self.special_to_semantic_ids = {
            special_id: tuple(semantic_ids)
            for special_id, semantic_ids in self.special_to_semantic_ids.items()
        }

    @classmethod
    def load(cls, root: Path, translations=(), japanese_overlay_path: Path | None = None):
        data = root / "data"
        canonical = load_canonical(data / "source/danbooru-2026-09-02.csv")
        aliases = load_aliases(data / "derived/danbooru_alias_normalized_index_VERIFIED_34417.csv", canonical)
        baseline_special = load_special(
            data / "special2788/illustrious_tag_knowledge_base_2788.csv",
            data / "derived/special2788_VERIFIED_LINKAGE.csv", canonical, aliases,
        )
        ruleset2 = Ruleset2Store.load(data / "derived/ruleset2", baseline_special)
        special = ruleset2.special
        semantic = load_semantic(data / "semantic/semantic_bridge_v1.csv", canonical, special)
        overlay_path = (data / "runtime/japanese_overlay.json" if japanese_overlay_path is None
                        else japanese_overlay_path)
        return cls(canonical, aliases, special, semantic, translations,
                   JapaneseOverlay.load(overlay_path, canonical), ruleset2)

    def load_generation_profile(self, path: Path | None = None):
        """Return a separate metadata view; existing knowledge is never mutated."""
        profiles = load_generation_profiles(path)
        joined = join_generation_profiles(self.special, profiles)
        return joined

    def load_generation_profile_store(self, root: Path) -> GenerationProfileStore:
        """Load v2 static rules/observations as an inspection-only sidecar."""
        return GenerationProfileStore.load(root, self.special)

    def create_core_set(self, **fields) -> CoreTagSet:
        result = CoreTagSet(**fields)
        result.validate(self.special)
        return result

    def resolve_exact(self, text: str) -> ExactResolution:
        key = normalize_lookup(text)
        special_ids = tuple(self.special_lookup.get(key, ()))
        # Preserve literal source identity even if NFKC collapses distinct canonicals.
        if text in self.canonical:
            return ExactResolution("canonical", (text,), special_ids)
        if key in self.canonical_lookup:
            return ExactResolution("canonical", tuple(self.canonical_lookup[key]), special_ids)
        if key in self.aliases:
            return ExactResolution("alias", self.aliases[key], special_ids)
        if key in self.japanese_lookup or key in self.translation_lookup or key in self.overlay_lookup:
            ids = tuple(self.japanese_lookup.get(key, ()))
            targets = list(self.translation_lookup.get(key, ()))
            targets.extend(self.overlay_lookup.get(key, ()))
            for sid in ids:
                tag = self.special[sid]
                targets.extend((tag.chosen_canonical,) if tag.chosen_canonical else tag.canonical_candidates)
            semantic_ids = tuple(
                semantic_id
                for special_id in ids
                for semantic_id in self.special_to_semantic_ids.get(special_id, ())
            )
            return ExactResolution("japanese", tuple(dict.fromkeys(targets)), ids, semantic_ids)
        if key in self.semantic_lookup:
            ids = tuple(self.semantic_lookup[key])
            return ExactResolution("semantic", special_ids=special_ids, semantic_ids=ids)
        return ExactResolution("none", special_ids=special_ids)
