import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
import uvicorn
from fastapi import FastAPI,Body
from  langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi.responses import StreamingResponse

from scripts.github_repo_loader import clone_github_repo,gettree
import json
from scripts.create_vectors import create_vector_store

from chatbot.session import add_history
from fastapi.middleware.cors import CORSMiddleware

from Database.database import connect_db


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
  
db=connect_db()
@app.get("/")
async def read_root():
    return {"message": "Codebase Reader API iiis running."}

@app.post("/register")
async def register(data):
    
    existing= (
    db.table("profiles")
    .select("*")
    .eq("username", data["user"])
    .execute()
)
    print("existing",existing)
    if len(existing.data)!=0 :
        print("user alredy exist")
        return
        
    
    response1 =  db.auth.sign_in_anonymously(
    {"options": {"data":data} }
)
    print("response1",response1)
    response2 = (
    db.table("profiles")
    .insert({"id":response1.user.id, "username":response1.user.user_metadata['user'],"avatar_url":""})
    .execute()
)    
    
   
    print("response2",response2)
    # return {"user created succefully",response}
    


@app.post("/embeddings")
async def fn_embedding(get: dict = Body(...)):
    url=get["repo_url"]
    user_id=get["user_id"]
    
    
    #  check for exisiting repo with current user and repo_url
    existing= (
    db.table("repositories")
    .select("*")
    .eq("url",url)
    .eq("added_by",user_id)
    .execute()
)
    print("existing",existing)
    if len(existing.data)!=0 :
        print("repo alredy exist")
        return {"message": "Repository already exists."}
    
    data = clone_github_repo(url)
  
   
    
    repo_res=(
        db.table("repositories")
        .insert({
            "id":data["repo_info"]["id"],
            "url":data["repo_info"]['url'],
            "added_by": user_id,
            "repo_name": data['repo_info']['repo_name'],
            "private": data['repo_info']['private'],
            "owner_name": data['repo_info']['owner_name'],
            "owner_avatar_url": data['repo_info']['owner_avatar_url'],
            "description": data['repo_info']['description'],
            "score": data['repo_info']['score']['final_score']
        })
        .execute()
    )
    
    # print("repo_res",repo_res)
    
    #score calculation
    existing_score=(
        db.table("score")
        .select("id")
        .eq("id",data['repo_info']['id'])
        .execute()
    )
    if len(existing_score.data)==0 :
        score_res=(
            db.table("score")
            .insert({
                "id":data['repo_info']['id'],
                "readme": data['score']['readme'],
                "score": data['score']['final_score'],
                "good": data['score']['good'],
                "bad": data['score']['bad'],
                "file_scores": data['score'].get('file_scores', []),
                "folder_scores": data['score'].get('folder_scores', []),
                "issue": data['score'].get('issues_found', [])
            })
            .execute()
        )
        # print("score_res",score_res)
    else:
        print("score exist")
    
    
    # embedding store creation and insertion to db
    exsiting_emebdding=(
        db.table("repo_embeddings")
        .select("*")
        .eq("repo_id",data['repo_info']['id'])
        .execute()
    )
    if len(exsiting_emebdding.data)==0 :
        vector_data=create_vector_store(data['repo_info']['id'],data['path'], hf_model)
        print("vector_data",vector_data)
        vector_data_res=(
            db.table("repo_embeddings")
            .insert(vector_data)
            .execute()
        )
        
        # print("vector_data_res",vector_data_res)
    else:
        print("vector store alredy exist")
        
        
    return {"message": "codebase loaded sucessfully.", "tree":data['tree'],"repo_info":data['repo_info'],"vector_data_count":len(vector_data)}

## todo add the methods for calling 


@app.get("/gettree")
async def get_tree(repo_owner: str, repo_name: str):
    res = gettree(repo_owner, repo_name)
    return {
        "message": "tree fetched successfully",
        "tree": res
    }

# from chatbot.chatbot import create_chatbot, chat_with_codebase

@app.post("/chat")
async def chat():

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
    
@app.post("/start_session")
async def start_session(data: dict = Body(...)):
    thread=data["thread_id"]
    user_id=data["user_id"]
    history=add_history(thread,user_id,db)
    






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
from sqlalchemy import text

import asyncio
    
if(__name__ == "__main__"):
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)
    # asyncio.run(register({"user":"hhfhfhf","password":"jfhjfjfj"}))
 
      
    
  