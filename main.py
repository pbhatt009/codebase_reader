import asyncio
from importlib.resources import path
import shutil
from dotenv import load_dotenv
import os
import stat
load_dotenv()
from sqlalchemy import func
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
from utils import add_utils

import asyncio
import uuid


app = FastAPI()
origins = [
    os.getenv("FRONTEND_URL")  # frontend URL from .env
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # allowed origins
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE etc.
    allow_headers=["*"],          # all headers
)
api=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
hf_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"

)
  
db=connect_db()

add_utils(db,hf_model)

@app.get("/")
async def read_root():
    return {"message": "Codebase Reader API iiis running."}

@app.post("/register")
async def register(data: dict = Body(...)):
    
    existing= (
    db.table("profiles")
    .select("*")
    .eq("id", data["user"])
    .execute()
)
    # print("existing",existing)
    if len(existing.data)!=0 :
        print("user alredy exist")
        return {"message": "User already exists.", "user_info": existing.data[0]}
        

    
    response2 = (
    db.table("profiles")
        .insert({"id":data['user'], "username":f"user_{data['user']}", "avatar_url":""})
        .execute()
)    
    
   
    print("response2",response2)
    # return {"user created succefully",response}
    return {"message": "User created successfully.", "user_info": response2.data[0]}
    


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
        return {"message": "Repository already exists.","exist":True}
    
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
    chunks_count=0
    if len(exsiting_emebdding.data)==0 :
        vector_data=create_vector_store(data['repo_info']['id'],data['path'], hf_model)
        chunks_count=len(vector_data)
        print("vector_data",vector_data)
        vector_data_res=(
            db.table("repo_embeddings")
            .insert(vector_data)
            .execute()
        )
    else:
        
        chunks_count=len(exsiting_emebdding.data)
        # print("vector_data_res",vector_data_res)

        print("vector store alredy exist")
        
    # delete the cloned repo to save space
    print(data['path'])
    def remove_readonly(func, path, _):
        os.chmod(path,stat.S_IWRITE)
        func(path)
    shutil.rmtree(data['path'],onexc=remove_readonly)
        
        
    return {"message": "codebase loaded sucessfully.", "tree":data['tree'],"repo_info":data['repo_info'],"vector_data_count":chunks_count,"exist":False,"score":data["score"]
            }

## todo add the methods for calling 


@app.get("/gettree")
async def get_tree(repo_owner: str, repo_name: str):
    res = gettree(repo_owner, repo_name)
    return {
        "message": "tree fetched successfully",
        "tree": res
    }

from chatbot.chatbot import  chat_with_codebase


@app.get("/getscore/{repo_id}")
async def get_score(repo_id: int):
    res=(
        db.table("score")
        .select("*")
        .eq("id", repo_id)
        .execute()
    )
    return {
        "message": "Score fetched successfully",
        "score": res.data[0] if len(res.data) > 0 else None
    }


@app.post("/newchat")
async def new_chat(data: dict = Body(...)):
 
    user_id = data["user_id"]
    repo_id = data["repo_id"]
    title=data["title"]
    res=(db.table("threads")
    .insert({
        
        "repo_id": repo_id,
        "created_by": user_id,
        "title": title
    })
    .execute()
    )
    print("thread created",res)
    return {"message": "Thread created successfully.", "response": res}

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
        for chunk in chat_with_codebase(data["query"], data["thread_id"],data['user_id'],data['repo_id']):
            # SSE FORMAT (CRITICAL)
            i+=1
            # print("chunk name",i, chunk)
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)
           
    

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        
    )
    
@app.get("/repositories/{user_id}")
async def get_repositories(user_id: str):
    user_id=uuid.UUID(user_id)
    res=(
        db.table("repositories")
        .select("*")
        .eq("added_by", user_id)
        .execute()
    )
    return {
        "message": "Repositories fetched successfully",
        "repositories": res.data
    }

@app.get("/threads/{repo_id}/{user_id}")
async def get_threads(repo_id: int, user_id:str):
    res=(
        db.table("threads")
        .select("id","title","created_at")
        .eq("repo_id", repo_id)
        .eq("created_by", user_id)
        .execute()
    )
    return {
        "message": "Threads fetched successfully",
        "threads": res.data
    }
    
    
@app.get("/messages/{thread_id}")
async def get_messages(thread_id: int):
    
    res=(
        db.table("messages")
        .select("*")
        .eq("thread_id", thread_id)
      
        .order("created_at", desc=False)
        .execute()
    )
    return {
        "message": "Messages fetched successfully",
        "history": res.data
    }

    
if(__name__ == "__main__"):
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)
    # asyncio.run(register({"user":"hhfhfhf","password":"jfhjfjfj"}))
 
      
    
  