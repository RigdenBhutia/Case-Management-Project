import ollama
from rag.ingest_documents import load_documents
from rag.chunking import chunk_by_paragraph
from rag.embed_index import build_index, retrieve

NO_ANSWER = "I don't have information on that in the approved policies."

SYSTEM_INSTRUCTIONS = f"""You are an IT policy assistant.
Answer the question using ONLY the numbered context passages below.
You may make reasonable inferences if the passages clearly imply the answer, even if exact words don't match.
Cite the passages you used, like [1] or [2].
If the passages truly do not contain relevant information, reply exactly: "{NO_ANSWER}"
Do not use outside knowledge beyond what's implied by the passages."""

def build_prompt(question, results):
    context = "\n\n".join(
        f"[{i}] ({r['title']}) {r['text']}" for i, r in enumerate(results, start=1)
    )
    return f"{SYSTEM_INSTRUCTIONS}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

def generate_answer(question, results):
    if not results:
        return NO_ANSWER
    prompt_text = build_prompt(question, results)
    response = ollama.generate(model="llama3.2", prompt=prompt_text)
    return response["response"]

if __name__ == "__main__":
    docs = load_documents()
    chunks = [c for d in docs for c in chunk_by_paragraph(d)]
    embeddings = build_index(chunks)

    for q in ["Can I install Photoshop?", "What is the capital of France?"]:
        results = retrieve(q, chunks, embeddings, top_k=2)
        answer = generate_answer(q, results)
        print(f"\nQ: {q}")
        print(f"A: {answer}")