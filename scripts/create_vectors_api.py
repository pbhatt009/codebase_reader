import requests
from scripts.spliiter import splitter
from uuid import uuid4
import os
import dotenv
from scripts.loader import load_code
from scripts.spliiter import splitter
from uuid import uuid4

dotenv.load_dotenv()


HEADERS = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACEHUB_ACCESS_TOKEN')}",
    "Content-Type": "application/json"
}



HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en"




# 🔹 batch embedding function
def embed_batch(texts):
    texts = ["passage: " + t for t in texts]

    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": texts}   
    )

    if response.status_code != 200:
        raise Exception(f"Embedding API error: {response.text}")

    return response.json()


# 🔹 main function
def create_vector_store(repo_id, path):
    docs = load_code(path)
    chunks = splitter(docs)
    print(f"Total chunks created: {len(chunks)}")

    rows = []

    chunk_texts = []
    metadata_list = []

    for doc in chunks:
        chunk_text = doc.page_content if hasattr(doc, "page_content") else str(doc)
        file_path = doc.metadata.get("source", "") if hasattr(doc, "metadata") else ""

        chunk_texts.append(chunk_text)
        metadata_list.append((file_path, chunk_text))

    BATCH_SIZE = 30
    all_vectors = []

    for i in range(0, len(chunk_texts), BATCH_SIZE):
        batch = chunk_texts[i:i + BATCH_SIZE]
        vectors = embed_batch(batch)
        all_vectors.extend(vectors)

    for i, (file_path, chunk_text) in enumerate(metadata_list):
        rows.append({
            "repo_id": repo_id,
            "file_path": file_path,
            "chunk_text": chunk_text,
            "embedding": all_vectors[i]
        })

    return rows


def embed_query(query):
    texts = ["passage: " + query]

    response = requests.post(
        HF_API_URL,
        headers=HEADERS,
        json={"inputs": texts}   
    )

    if response.status_code != 200:
        raise Exception(f"Embedding API error: {response.text}")
    


    return response.json()[0]
    
    