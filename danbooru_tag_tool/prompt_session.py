"""Minimal Special selection/export, independent of optional generation metadata."""
from dataclasses import dataclass

from .models import CoreTagSet, SpecialTag
from .prompt_formatter import PromptFormatter


@dataclass(frozen=True, slots=True)
class PromptSession:
    core: CoreTagSet
    special_tags: tuple[SpecialTag, ...]

    def __post_init__(self):
        if not isinstance(self.special_tags, tuple) or any(
            not isinstance(tag, SpecialTag) for tag in self.special_tags
        ):
            raise ValueError("Session requires a tuple of Special tags")
        if tuple(tag.special_id for tag in self.special_tags) != self.core.special_tag_ids:
            raise ValueError("Session Special identities must match Core order")

    @classmethod
    def from_core(cls, core: CoreTagSet, knowledge):
        core.validate(knowledge.special)
        return cls(core, tuple(knowledge.special[sid] for sid in core.special_tag_ids))

    def export_prompt(self) -> str:
        # Never use chosen_canonical or generation metadata to rewrite this identity.
        return ", ".join(PromptFormatter.format_special(tag).text for tag in self.special_tags)

    @property
    def statistics_canonicals(self) -> tuple[str, ...]:
        """Only existing resolved linkage; unmapped/ambiguous remain unresolvable."""
        return tuple(dict.fromkeys(tag.statistics_canonical for tag in self.special_tags
                                   if tag.statistics_canonical is not None))

    @property
    def unresolved_statistics_special_ids(self) -> tuple[str, ...]:
        return tuple(tag.special_id for tag in self.special_tags
                     if tag.statistics_canonical is None)
