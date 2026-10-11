from rag.ingest_documents import load_documents

CATEGORY_MAP = {
    "hardware_replacement_policy.txt": "Hardware",
    "vpn_access_policy.txt": "Network",
    "software_licensing_policy.txt": "Software",
}

def chunk_by_paragraph(doc):
    lines = doc["text"].split("\n")
    body = lines[1:]  # first line is the document title, skip it
    chunks = []
    for i, paragraph in enumerate(body):
        chunks.append({
            "chunk_id": f"{doc['filename']}::paragraph::{i}",
            "text": paragraph,
            "source": doc["filename"],
            "title": doc["title"],
            "category": CATEGORY_MAP.get(doc["filename"], "Unknown"),
            "strategy": "paragraph",
        })
    return chunks

def chunk_fixed_size(doc, chunk_size=30, overlap=10):
    body_text = " ".join(doc["text"].split("\n")[1:])
    words = body_text.split()
    step = chunk_size - overlap
    chunks = []
    for i, start in enumerate(range(0, len(words), step)):
        chunk_words = words[start:start + chunk_size]
        chunks.append({
            "chunk_id": f"{doc['filename']}::fixed::{i}",
            "text": " ".join(chunk_words),
            "source": doc["filename"],
            "title": doc["title"],
            "category": CATEGORY_MAP.get(doc["filename"], "Unknown"),
            "strategy": "fixed",
        })
        if start + chunk_size >= len(words):
            break
    return chunks

if __name__ == "__main__":
    docs = load_documents()
    paragraph_chunks = [c for d in docs for c in chunk_by_paragraph(d)]
    fixed_chunks = [c for d in docs for c in chunk_fixed_size(d)]

    print("Paragraph chunks:", len(paragraph_chunks))
    print("Fixed-size chunks:", len(fixed_chunks))
    print("\nSample paragraph chunk:\n", paragraph_chunks[0])
    print("\nSample fixed chunk:\n", fixed_chunks[0])