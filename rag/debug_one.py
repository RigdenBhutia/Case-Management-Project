from rag.service import CHUNKS, EMBEDDINGS
from rag.embed_index import retrieve
from rag.prompt import generate_answer

q = "My laptop won't turn on, can I get a replacement?"
results = retrieve(q, CHUNKS, EMBEDDINGS, top_k=2)

for r in results:
    print(round(r["score"], 3), r["chunk_id"], "|", r["text"][:90])

print()
for i in range(3):
    print(f"Run {i + 1}:", generate_answer(q, results))