import hashlib
import spacy

# Maps real author names to stable anonymous identifiers
# within a single pipeline run. Stable = same name always
# gets the same alias, so thread reconstruction stays coherent.

_author_map: dict[str, str] = {}
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_alias(name: str) -> str:
    """Returns a stable alias for a real name."""
    key = name.strip().lower()  # normalize before hashing
    if key not in _author_map:
        short_hash = hashlib.md5(key.encode()).hexdigest()[:6]
        _author_map[key] = f"user_{short_hash}"
    return _author_map[key]


def _anonymize_content(content: str) -> str:
    """Detects person names in content via NER and replaces them with aliases."""
    nlp = _get_nlp()
    doc = nlp(content)
    result = content

    # process longest names first to avoid partial replacements
    persons = sorted(
        [ent for ent in doc.ents if ent.label_ == "PERSON"],
        key=lambda e: len(e.text),
        reverse=True,
    )

    for ent in persons:
        alias = _get_alias(ent.text)
        result = result.replace(ent.text, alias)

    return result


def anonymize_message(message: dict) -> dict:
    """Anonymizes both the author field and any person names in content."""
    return {
        **message,
        "author": _get_alias(message["author"]),
        "content": _anonymize_content(message["content"]),
    }


def reset_author_map() -> None:
    _author_map.clear()