import os

def load_documents(folder_path="rag/documents"):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_text = clean_text(raw_text)

            documents.append({
                "filename": filename,
                "title": cleaned_text.split("\n")[0],
                "text": cleaned_text
            })
    return documents

def clean_text(text: str) -> str:
    # Remove excess blank lines and leading/trailing whitespace
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line != ""]
    return "\n".join(lines)

if __name__ == "__main__":
    docs = load_documents()
    for doc in docs:
        print(f"--- {doc['title']} ({doc['filename']}) ---")
        print(doc["text"])
        print()