from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

COLLECTION_NAME = "knowledge_objects"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

_client = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host="localhost", port=6333)
        _ensure_collection(_client)
    return _client


def _ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def index_knowledge_object(knowledge_object: dict, vector: list[float]) -> None:
    """Indexes one knowledge object into Qdrant, keyed by its Postgres id."""
    client = get_client()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(knowledge_object["id"]),
                vector=vector,
                payload={
                    "thread_id": knowledge_object["thread_id"],
                    "problem": knowledge_object.get("problem"),
                    "confirmed_solution": knowledge_object.get("confirmed_solution"),
                    "technology": knowledge_object.get("technology"),
                },
            )
        ],
    )


def search_similar(vector: list[float], top_k: int = 3) -> list[dict]:
    """Returns the top_k most similar knowledge objects for a query vector."""
    client = get_client()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
    ).points
    return [{"score": r.score, **r.payload} for r in results]
