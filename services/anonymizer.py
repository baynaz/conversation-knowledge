import hashlib

# Maps real author names to stable anonymous identifiers
# within a single pipeline run. Stable = same name always
# gets the same alias, so thread reconstruction stays coherent.
_author_map: dict[str, str] = {}


def _get_alias(author: str) -> str:
    """Returns a stable anonymous alias for a given author name.

    Uses a short hash of the name so the alias is deterministic
    across multiple calls within the same session, but doesn't
    expose the original name.
    """
    if author not in _author_map:
        short_hash = hashlib.md5(author.encode()).hexdigest()[:6]
        _author_map[author] = f"user_{short_hash}"
    return _author_map[author]


def anonymize_message(message: dict) -> dict:
    """Returns a copy of the message with the author replaced by an alias.

    The original author is never passed to any LLM — only the alias.
    The alias is stored in raw_messages.author in the database.
    """
    return {
        **message,
        "author": _get_alias(message["author"]),
    }


def reset_author_map() -> None:
    """Clears the in-memory author map. Call this between simulation runs
    so aliases don't bleed across scenarios.
    """
    _author_map.clear()