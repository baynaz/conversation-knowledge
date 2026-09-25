from services.embedding_service import embed_knowledge_object
from services.qdrant_service import search_similar

# below this score we consider the match too weak to be useful
SIMILARITY_THRESHOLD = 0.70


def ask(question: str, top_k: int = 3) -> dict:
    """Searches the knowledge base for the most relevant past solution.

    Returns a dict with:
    - answer_found  : bool
    - question      : the original question
    - score         : similarity score of the best match (0.0 to 1.0)
    - problem       : the matched past problem
    - confirmed_solution : the fix that worked (None if no match)
    - technology    : the technology involved
    - thread_id     : source thread for provenance
    - candidates    : all results above threshold (for transparency)
    """
    # embed the question using the same fields structure as knowledge objects
    vector = embed_knowledge_object({
        "problem": question,
        "symptoms": [],
        "confirmed_solution": "",
    })

    results = search_similar(vector, top_k=top_k)

    # filter results above threshold
    relevant = [r for r in results if r["score"] >= SIMILARITY_THRESHOLD]

    if not relevant:
        return {
            "answer_found": False,
            "question": question,
            "score": results[0]["score"] if results else 0.0,
            "problem": None,
            "confirmed_solution": None,
            "technology": None,
            "thread_id": None,
            "candidates": [],
        }

    best = relevant[0]

    return {
        "answer_found": True,
        "question": question,
        "score": round(best["score"], 4),
        "problem": best.get("problem"),
        "confirmed_solution": best.get("confirmed_solution"),
        "technology": best.get("technology"),
        "thread_id": best.get("thread_id"),
        "candidates": [
            {
                "score": round(r["score"], 4),
                "problem": r.get("problem"),
                "confirmed_solution": r.get("confirmed_solution"),
                "thread_id": r.get("thread_id"),
            }
            for r in relevant
        ],
    }