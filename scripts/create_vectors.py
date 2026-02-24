from scripts.loader import load_code
from scripts.spliiter import splitter
from uuid import uuid4
def create_vector_store(repo_id,path, hf_model):
    
    docs= load_code(path)
    chunks = splitter(docs)
    rows = []

    for i, doc in enumerate(chunks):
    # Each doc should contain text + metadata (file path)
        chunk_text = doc.page_content if hasattr(doc, "page_content") else str(doc)
        file_path = doc.metadata.get("source", "") if hasattr(doc, "metadata") else ""

        # Get embedding vector for this chunk
        embedding_vector = hf_model.embed_query(chunk_text)

        rows.append({
            "repo_id": repo_id,  # unique int8 id
          
            "file_path": file_path,
            "chunk_text": chunk_text,
            "embedding": embedding_vector
        })
    
    return rows
       