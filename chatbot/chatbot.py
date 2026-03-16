# ================== imports ==================
from typing import TypedDict, Annotated, List
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage,AIMessageChunk
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFacePipeline,HuggingFaceEndpoint
from repo_qulaity.score_cal import calculate_score
import os,json
from dotenv import load_dotenv

from utils import get_utils

from chatbot.session import add_history,get_history,fetch_history,history_store,clear_history



load_dotenv()

# ================== LLM ==================
db=None
hf_model=None
chat = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=8000,
    streaming=True
)


# ================== Prompt ==================
prompt = PromptTemplate(
    template="""
You are a helpful assistant.

Use ONLY the information provided in the Context and the Conversation History to answer the Current Question.
Do NOT use any external knowledge or assumptions.

If the answer cannot be found in the provided information, say:
"I don't know."

Conversation History:
{history}

Context:
{context}

Current Question:
{question}

Answer:
""",
    input_variables=["context", "question","history"]
)

# ================== State ==================
class ChatState(TypedDict):
    message:BaseMessage
    answer:BaseMessage
    user_id:str
    thread_id:str
    repo_id:str
    # stream:str

# ================== RAG helpers ==================



  
### repo info function
def repo_info(repo_id):
    
    res=(
        db.table("score")
        .select("*")
        .eq("id", repo_id)
        .execute()
    )
    
    if len(res.data)==0:
        return "No information available about the repository."
    score_data=res.data[0]
    return str(score_data)
   
    

# fetch context function

def fetch_context(question,repo_id):
    vector=hf_model.embed_query(question)
    # print("vector",vector)
    response = db.rpc(
    "semantic",
    {
        "query_vec": vector,  
        "id": int(repo_id)
    }
    ).execute()
    print("response",response)
    
    context="\n\n".join(doc["chunk_text"] for doc in response.data)
    return context



# add message to database
def add_message_db(content,role,thread_id, user_id):
    
    message_entry=(
        db.table("messages") 
        .insert({
            
            "content": content,
            "role": role,
            "thread_id": thread_id,
            "user_id": user_id
        })
        .execute()
    )
    print("message_entry sucessfull")


    
def is_info_related(question):
    keywords = ["repo", "repository", "project", "about", "overview"]
    question_lower = question.lower()
    return any(k in question_lower for k in keywords)   

    
    # ================== Graph Node ==================

def response_node(state: ChatState):
   
    

    question = state["message"].content
    thread_id=state["thread_id"]
    user_id=state["user_id"]
    repo_id=state["repo_id"]
    
    ## retrive history from memory
    history_text = get_history(user_id, thread_id)
    ### add question to history
    add_history(user_id,thread_id,"User", question)
    ## add question to database
    
    add_message_db(state["message"].content, "user", thread_id, user_id)
    
    


    
    
    if is_info_related(question):
        context_text = repo_info(repo_id)
    else:
        context_text=fetch_context(question,repo_id)
        
    
    # conditioning chaining for context
    
    

    chain =(
        {
            "context": RunnableLambda(lambda _:context_text),
            "history": RunnableLambda(lambda _: history_text),
            "question": RunnableLambda(lambda _: question),
        }
        | prompt
        | chat
    )

    full_answer = ""

    #  STREAM TOKENS
    print(question)
    i=0
    for chunk in chain.stream(state['message']):
        # print("chunk", chunk)
       
        if hasattr(chunk, "content"):
            full_answer += chunk.content
            # print(f"chunk {i} yielded {i}")
            yield AIMessageChunk(content=chunk.content)
            i += 1

    
    # print("Full answer:", full_answer)
    # print("yielding full answer",full_answer)
    
    add_history(user_id, thread_id, "assistant", full_answer)
    add_message_db(full_answer, "assistant", thread_id, user_id)
    
    yield {"answer":[AIMessage(content=full_answer)]}
    

# ================== Build Graph ==================
graph = StateGraph(ChatState)
graph.add_node("response", response_node)
graph.add_edge(START, "response")
graph.add_edge("response", END)

def check_thread(thread_id,user_id,repo_id):
    res=(
        db.table("threads")
    )

workflow =graph.compile()

# ================== Public API ==================
def chat_with_codebase(question: str, thread_id: str,user_id:str,repo_id:str):
    config = {"configurable": {"thread_id": thread_id,"user_id": user_id}}
    global hf_model, db
    if hf_model is None:
        (hf_model,db)=get_utils()
        
    
        
    
        
  
        fetch_history(thread_id, user_id, db)

    
    
    for msg, meta in workflow.stream(
    {"message": HumanMessage(content=question), "user_id": user_id, "thread_id": thread_id, "repo_id": repo_id},
    config=config,
    stream_mode="messages"
    ):
        if isinstance(msg, AIMessageChunk):
            print(msg.content)
            yield msg.content      
        elif isinstance(msg, AIMessage):
            pass
    
    # print("updating state")
           
 
                
