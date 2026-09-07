import re
import unicodedata


def normalize_lookup(text: str) -> str:
    """One tag per key; underscores and whitespace are equivalent."""
    text = unicodedata.normalize("NFKC", text).lower().strip()
    return re.sub(r"\s+", " ", text.replace("_", " ")).strip()


def split_prompt_input(text: str) -> tuple[str, ...]:
    text = unicodedata.normalize("NFKC", text)
    return tuple(part.strip() for part in re.split(r"[,\r\n]+", text) if part.strip())
