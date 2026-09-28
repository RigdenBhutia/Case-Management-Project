import numpy as np
from sentence_transformers import SentenceTransformer
from rag.ingest_documents import load_documents
from rag.chunking import chunk_by_paragraph

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_index(chunks):
    texts = [c["text"] for c in chunks]
    return model.encode(texts, normalize_embeddings=True)

def search(query, chunks, embeddings, top_k=3, category=None):
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    scores = embeddings @ query_vec
    results = []
    for idx in np.argsort(scores)[::-1]:
        chunk = chunks[idx]
        if category and chunk["category"] != category:
            continue
        results.append({**chunk, "score": float(scores[idx])})
        if len(results) == top_k:
            break
    return results

MIN_SCORE = 0.30  # starting guess, to be tuned with the evaluation set

def retrieve(query, chunks, embeddings, top_k=3, category=None, min_score=MIN_SCORE):
    results = search(query, chunks, embeddings, top_k=top_k, category=category)
    return [r for r in results if r["score"] >= min_score]    

if __name__ == "__main__":
    docs = load_documents()
    chunks = [c for d in docs for c in chunk_by_paragraph(d)]
    embeddings = build_index(chunks)

    questions = [
        "When can I get a new laptop?",
        "Can a contractor use the VPN?",
        "Can I install Photoshop?",
        "What is the weather today?",
        "What is the capital of France?",
    ]
    for q in questions:
        results = retrieve(q, chunks, embeddings, top_k=2)
        print(f"\nQ: {q}")
        if not results:
            print("  -> NO ANSWER (nothing above threshold)")
        for r in results:
            print(f"  {r['score']:.3f} | {r['title']} | {r['text'][:70]}...")