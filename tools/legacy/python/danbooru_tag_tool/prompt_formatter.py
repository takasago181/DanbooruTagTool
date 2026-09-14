from .models import CanonicalTag, PromptTag, SpecialTag


class PromptFormatter:
    @staticmethod
    def format_special(tag: SpecialTag) -> PromptTag:
        return PromptTag(tag.term.replace("_", " "))

    @staticmethod
    def format_tag(tag: CanonicalTag) -> PromptTag:
        return PromptTag(tag.canonical_tag.replace("_", " "))
