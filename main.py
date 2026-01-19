from dotenv import load_dotenv
import os
load_dotenv()
import uvicorn
from fastapi import FastAPI
from  langchain_community.embeddings import HuggingFaceEmbeddings


from scripts.github_repo_loader import clone_github_repo
from scripts.loader import load_code


from scripts.spliiter import splitter

from scripts.vd import create_vector_store
from scripts.retriverAndaug import get_response,chain_llm

# app = FastAPI()
# api=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
# hf_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"

# )
# @app.get("/")
# async def read_root():
#     return {"message": "Codebase Reader API iiis running."}

# @app.get("/embeddings")
# async def fn(github_repo_url: str):
#     repo_path = clone_github_repo(github_repo_url)
#     documents = load_code(repo_path)
#     chunks = splitter(documents)
#     global vector_store
#     vector_store = create_vector_store(chunks, hf_model)
#     # print("Vector store created.")
#     # print(vector_store.index_to_docstore_id)
#     return {"message": "Vector store created successfully.", "num_chunks": len(chunks), "store": vector_store.index_to_docstore_id}

# ## todo add the methods for calling 

# @app.get("/respond")
# async def call(github_repo_url: str, query: str, k: int=4):
#     # repo_path = clone_github_repo("https://github.com/pbhatt009/Ml-Model-Streamlit.git")
#     # documents = load_code(repo_path)
#     # chunks = splitter(documents)
#     # vector_store = create_vector_store(chunks, hf_model)
#     # # print("Vector store created.")
#     # # print(vector_store.index_to_docstore_id)
#     # # return {"message": "Vector store created successfully.", "num_chunks": len(chunks), "id": vector_store.index_to_docstore_id}
#     response=get_response(vector_store, query, k=4)
#     return {"response": response}




# ### download embedding model on startup instead of at request time







# for doc in documents:
#     print("meta", doc.metadata['source'].split(".")[-1])
    


# print(f"Total chunks created: {len(chunks)}")
# for chunk in chunks[:3]:
#     print(chunk.page_content)
#     print("-----")
    


# vector_store = create_vector_store(chunks, hf_model)
# print("Vector store created.")
# print(vector_store.index_to_docstore_id)


# print(chain_llm)

# result=get_response(vector_store, "What is the purpose of this repository?",k=4)
# print(result)

from repo_qulaity.scanner import scan_repo

if(__name__ == "__main__"):
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    print(scan_repo("scripts/clone_repo/video_sharing_platform_backend"))