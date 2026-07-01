from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-loads the embedding model once, reused across calls."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_knowledge_object(knowledge: dict) -> list[float]:
    """Builds a single text representation of the knowledge object and embeds it.

    Concatenates the fields that matter for semantic retrieval: problem, symptoms,
    and confirmed_solution. We deliberately exclude context/technology here since
    those are better used as Qdrant metadata filters, not embedded text.
    """
    parts = [
        knowledge.get("problem") or "",
        " ".join(knowledge.get("symptoms", [])),
        knowledge.get("confirmed_solution") or "",
    ]
    text = " ".join(p for p in parts if p).strip()

    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
