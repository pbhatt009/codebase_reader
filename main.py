import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
import uvicorn
from fastapi import FastAPI,Body
from  langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi.responses import StreamingResponse

from scripts.github_repo_loader import clone_github_repo,gettree
from scripts.loader import load_code

import json
from scripts.spliiter import splitter

from scripts.vd import create_vector_store
from chatbot.chatbot import add_vector_store
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
# origins = [
#     "http://localhost:5173/"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,        # allowed origins
#     allow_credentials=True,
#     allow_methods=["*"],          # GET, POST, PUT, DELETE etc.
#     allow_headers=["*"],          # all headers
# )
api=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
hf_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"

)
@app.get("/")
async def read_root():
    return {"message": "Codebase Reader API iiis running."}

@app.post("/embeddings")
async def fn_embedding(url: dict = Body(...)):
    data = clone_github_repo(url["repo_url"])
    # docs= load_code(data['path'])
    # chunks = splitter(docs)
    # print(chunks)
    # vector_store = create_vector_store(chunks, hf_model)
    # print("Vector store created.")
    # add_vector_store(vector_store,data['path'])
    # print("Vector store created.")
    # print(vector_store.index_to_docstore_id)
    # return {"message": "Vector store created successfully.", "num_chunks": len(chunks), "store": vector_store.index_to_docstore_id,"tree":data['tree']}
    return {"message": "codebase loaded sucessfully.", "tree":data['tree'],"repo_info":data['repo_info']}

## todo add the methods for calling 


@app.get("/gettree")
async def get_tree(repo_owner: str, repo_name: str):
    res = gettree(repo_owner, repo_name)
    return {
        "message": "tree fetched successfully",
        "tree": res
    }

from chatbot.chatbot import create_chatbot, chat_with_codebase

@app.post("/chat")
async def chat():
    data=create_chatbot()
    return {"message": "Chatbot created successfully.", "thread_id": data}

@app.post("/respond")
async def call(data: dict = Body(...)):
    # repo_path = clone_github_repo("https://github.com/pbhatt009/Ml-Model-Streamlit.git")
    # documents = load_code(repo_path)
    # chunks = splitter(documents)
    # vector_store = create_vector_store(chunks, hf_model)
    # print("Vector store created.")
    # print(vector_store.index_to_docstore_id)
    # return {"message": "Vector store created successfully.", "num_chunks": len(chunks), "id": vector_store.index_to_docstore_id}
    async def event_generator():
        i=0
        for chunk in chat_with_codebase(data["query"], data["thread_id"]):
            # SSE FORMAT (CRITICAL)
            i+=1
            # print("chunk name",i, chunk)
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)
           
    

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        
    )
    







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
from repo_qulaity.metrics import readme_metrics, analyze_files,analyze_folder
from repo_qulaity.score_cal import calculate_score

if(__name__ == "__main__"):
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)
    # data=scan_repo("scripts/clone_repo/Blog_Web_App")
    # print(data)
    # readme_data=readme_metrics("scripts/clone_repo/Blog_Web_App")
    # print("readme data", readme_data)
    
    # f_data=analyze_files(data["files"])
    # print("file analysis data", f_data)
    
    # folder_data=analyze_folder(data["folders"])
    # print("folder analysis data", folder_data)
    
    # def dict_to_string() -> str:
    #     result=calculate_score("scripts/clone_repo/Video-Sharing-Platform-Frontend")
    #     return json.dumps(result, indent=2, ensure_ascii=False)
    # print(dict_to_string())
  
    # fn_embedding({"repo_url":"https://github.com/pbhatt009/Video-Sharing-Platform-Frontend.git"})
    # create_chatbot()
    # chat_with_codebase("Explain the function of the codebase.", "1")
    
    # fn_embedding({"repo_url":"https://github.com/pbhatt009/Video-Sharing-Platform-Frontend.git"})
    # create_chatbot()
    # res=call({"query":"Explain the function of the codebase.","thread_id":"1"})
    # print(res)
    