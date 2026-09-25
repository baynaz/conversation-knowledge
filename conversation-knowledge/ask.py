# ask.py
import sys
from services.embedding_service import embed_knowledge_object
from services.qdrant_service import search_similar

question = sys.argv[1] if len(sys.argv) > 1 else "VPN not connecting error 800"

vector = embed_knowledge_object({
    "problem": question,
    "symptoms": [],
    "confirmed_solution": ""
})

results = search_similar(vector, top_k=3)

if not results:
    print("No similar problems found in the knowledge base.")
else:
    for r in results:
        print(f"\nscore     : {r['score']:.4f}")
        print(f"thread_id : {r['thread_id']}")
        print(f"problem   : {r['problem']}")
        print(f"solution  : {r['confirmed_solution']}")