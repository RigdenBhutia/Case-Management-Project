from rag.ingest_documents import load_documents
from rag.chunking import chunk_by_paragraph
from rag.embed_index import build_index, retrieve
from rag.prompt import generate_answer, NO_ANSWER

# Built once when the app starts, not on every request
_docs = load_documents()
CHUNKS = [c for d in _docs for c in chunk_by_paragraph(d)]
EMBEDDINGS = build_index(CHUNKS)

def answer_question(question, category=None, top_k=2):
    results = retrieve(question, CHUNKS, EMBEDDINGS, top_k=top_k, category=category)
    answer = generate_answer(question, results)
    answered = bool(results) and answer.strip() != NO_ANSWER
    sources = [
        {
            "title": r["title"],
            "source": r["source"],
            "chunk_id": r["chunk_id"],
            "score": round(r["score"], 3),
        }
        for r in results
    ] if answered else []
    return {"answer": answer, "answered": answered, "sources": sources}