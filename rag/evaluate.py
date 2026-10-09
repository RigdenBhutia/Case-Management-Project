import json
from rag.ingest_documents import load_documents
from rag.chunking import chunk_by_paragraph, chunk_fixed_size
from rag.embed_index import build_index, search

THRESHOLDS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

def load_eval_set(path="rag/eval_set.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def evaluate_strategy(name, chunker, eval_set, docs):
    chunks = [c for d in docs for c in chunker(d)]
    embeddings = build_index(chunks)

    rows = []
    for item in eval_set:
        top = search(item["question"], chunks, embeddings, top_k=2)
        rows.append({
            **item,
            "top_score": top[0]["score"],
            "top_source": top[0]["source"],
        })

    answerable = [r for r in rows if r["should_answer"]]
    hits = sum(r["top_source"] == r["expected_source"] for r in answerable)

    print(f"\n===== Strategy: {name} ({len(chunks)} chunks) =====")
    print(f"Top-1 retrieval accuracy: {hits}/{len(answerable)}")

    print("\nQuestions where the wrong document ranked first:")
    misses = [r for r in answerable if r["top_source"] != r["expected_source"]]
    if not misses:
        print("  none")
    for r in misses:
        print(f"  {r['top_score']:.3f} | {r['question']} -> got {r['top_source']}")

    print("\nTop scores for questions that should be refused:")
    for r in rows:
        if not r["should_answer"]:
            print(f"  {r['top_score']:.3f} | {r['question']}")

    print("\nThreshold sweep:")
    print("  thresh | answered ok | wrongly refused | wrongly answered | correctly refused")
    for t in THRESHOLDS:
        ok = sum(r["top_score"] >= t and r["top_source"] == r["expected_source"] for r in answerable)
        wrongly_refused = sum(r["top_score"] < t for r in answerable)
        unanswerable = [r for r in rows if not r["should_answer"]]
        wrongly_answered = sum(r["top_score"] >= t for r in unanswerable)
        correctly_refused = len(unanswerable) - wrongly_answered
        print(f"  {t:.2f}   | {ok:>11} | {wrongly_refused:>15} | {wrongly_answered:>16} | {correctly_refused:>17}")

if __name__ == "__main__":
    docs = load_documents()
    eval_set = load_eval_set()
    evaluate_strategy("paragraph", chunk_by_paragraph, eval_set, docs)
    evaluate_strategy("fixed-size", chunk_fixed_size, eval_set, docs)