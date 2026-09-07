from dataclasses import asdict, dataclass
from datetime import datetime
import json
from typing import Collection

from .normalization import normalize_lookup


TRANSLATION_STATUSES = frozenset({
    "UNREVIEWED_TRIAL", "UNREVIEWED", "REVIEWED", "REJECTED",
})


@dataclass(frozen=True, slots=True)
class CanonicalTag:
    canonical_tag: str
    category: int
    current_post_count: int

    def __post_init__(self):
        if not self.canonical_tag or any(c.isspace() for c in self.canonical_tag):
            raise ValueError("Canonical must be a nonempty source tag, without spaces")
        if self.category not in {0, 1, 3, 4, 5} or self.current_post_count < 0:
            raise ValueError("Invalid category/current_post_count")

    @property
    def lookup_key(self) -> str:
        return normalize_lookup(self.canonical_tag)


@dataclass(frozen=True, slots=True)
class PromptTag:
    text: str


@dataclass(frozen=True, slots=True)
class SpecialTag:
    special_id: str
    term: str
    japanese: str
    description: str
    layer: str
    source_category: str
    chosen_canonical: str | None
    match_type: str
    canonical_candidates: tuple[str, ...]
    is_special: bool = True
    main_category: str = ""
    related_category: str = ""
    gender_scope: str = ""
    danbooru_kind: str = ""
    dictionary_post_count: int | None = None
    count_band: str = ""
    search_keys: tuple[str, ...] = ()
    alias_semantic_status: str = ""
    alias_semantic_role: str = ""
    alias_statistics_policy: str = ""
    default_full_semantic_stats_allowed: bool | None = None
    related_evidence_allowed: bool = False
    automatic_prompt_replacement: str = "NEVER"

    @property
    def statistics_canonical(self) -> str | None:
        """Canonical eligible for default AND statistics, never Prompt output."""
        if self.layer == "Alias" and self.default_full_semantic_stats_allowed is False:
            return None
        return self.chosen_canonical


@dataclass(frozen=True, slots=True)
class Translation:
    canonical_tag: str
    japanese: str
    translation_source: str
    translation_status: str
    updated_at: str | None = None

    def __post_init__(self):
        if not isinstance(self.canonical_tag, str) or not self.canonical_tag.strip():
            raise ValueError("Translation canonical tag required")
        if not isinstance(self.japanese, str) or not self.japanese.strip():
            raise ValueError("Translation Japanese text required")
        if self.translation_status not in TRANSLATION_STATUSES:
            raise ValueError("Invalid translation status")


@dataclass(frozen=True, slots=True)
class SemanticCandidate:
    semantic_id: str
    special_id: str
    semantic_term: str
    ja_label: str
    en_concept: str
    candidate_canonical: str | None
    relation_type: str
    notes: str
    review_status: str


@dataclass(frozen=True, slots=True)
class CoreTagSet:
    core_set_id: str
    core_set_name: str
    special_tag_ids: tuple[str, ...]
    memo: str
    created_at: str

    def __post_init__(self):
        if not all(isinstance(v, str) for v in
                   (self.core_set_id, self.core_set_name, self.memo, self.created_at)):
            raise ValueError("Core metadata must be strings")
        if not self.core_set_id.strip() or not self.core_set_name.strip():
            raise ValueError("Core ID/name required")
        if not isinstance(self.special_tag_ids, (list, tuple)):
            raise ValueError("Special IDs must be an array")
        ids = tuple(self.special_tag_ids)
        if not ids or any(not isinstance(i, str) or not i for i in ids):
            raise ValueError("Core requires at least one Special ID")
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate Special IDs")
        object.__setattr__(self, "special_tag_ids", ids)
        if "T" not in self.created_at:
            raise ValueError("created_at must be ISO-8601 datetime")
        datetime.fromisoformat(self.created_at)

    def validate(self, special_ids: Collection[str]) -> None:
        if not set(self.special_tag_ids) <= set(special_ids):
            raise ValueError("Unknown Special ID")

    def to_json(self, special_ids: Collection[str]) -> str:
        self.validate(special_ids)
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, text: str, special_ids: Collection[str]) -> "CoreTagSet":
        result = cls(**json.loads(text))
        result.validate(special_ids)
        return result


AUXILIARY_ROLES = frozenset({
    "composition", "pose", "expression", "clothing", "background",
    "situation", "detail", "body", "action", "other",
})


@dataclass(frozen=True, slots=True)
class AuxiliaryTag:
    tag: CanonicalTag
    role: str = "other"

    def __post_init__(self):
        if not isinstance(self.tag, CanonicalTag) or self.role not in AUXILIARY_ROLES:
            raise ValueError("Invalid auxiliary tag/role")


@dataclass(frozen=True, slots=True)
class LoRA:
    name: str
    weight: float = 1.0
    trigger: str = ""
