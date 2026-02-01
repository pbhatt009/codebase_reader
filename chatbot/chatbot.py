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
import os
from dotenv import load_dotenv
load_dotenv()
 
# ================== LLM ==================
chat = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_tokens=8000,
    streaming=True
)

# chat = HuggingFaceEndpoint(
#     api_key=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN"),
#     repo_id="meta-llama/Llama-3.1-8B-Instruct",
#     task="text-generation",
#     max_new_tokens=5000,
#     do_sample=False,
    
# )
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
    messages: Annotated[List[BaseMessage], add_messages]
    # stream:str

# ================== RAG helpers ==================
def return_context(docs):
    print(len(docs), "docs found for retrieval")
    return "\n\n".join(doc.page_content for doc in docs)

def format_history(messages: List[BaseMessage]) -> str:
    formatted = []
    for msg in messages[:-1]:  # exclude current question
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)


# vector store injected later


def add_vector_store(store):
    global vector_store
    vector_store = store
    
    
def repo_info():
    pass
    # ================== Graph Node ==================
def response_node(state: ChatState):
    """Streams tokens and saves final answer once"""
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    question = state["messages"][-1].content
    history_text = format_history(state["messages"])
    
    def is_info_related(question):
        pass

    
    
    if is_info_related(question):
        context_text = repo_info()
    else:
        docs = retriever.invoke(question)
        context_text = return_context(docs)
        
    
    # conditioning chaining for context
    
    

    chain = (
        {
            "context": RunnableLambda(context_text),
            "history": RunnableLambda(lambda _: history_text),
            "question": RunnableLambda(lambda _: question),
        }
        | prompt
        | chat
    )

    full_answer = ""

    # 🔥 STREAM TOKENS
    print(question)
    i=0
    for chunk in chain.stream(state['messages']):
        # print("chunk", chunk)
       
        if hasattr(chunk, "content"):
            full_answer += chunk.content
            # print(f"chunk {i} yielded {i}")
            yield AIMessageChunk(content=chunk.content)
            i += 1

    
    # print("Full answer:", full_answer)
    # print("yielding full answer",full_answer)
    
    yield {"messages":[AIMessage(content=full_answer)]}
    

# ================== Build Graph ==================
graph = StateGraph(ChatState)
graph.add_node("response", response_node)
graph.add_edge(START, "response")
graph.add_edge("response", END)

def create_chatbot():
    global workflow

    checkpointer = InMemorySaver()
    workflow = graph.compile(checkpointer=checkpointer)

# ================== Public API ==================
def chat_with_codebase(question: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    for msg, meta in workflow.stream(
    {"messages": [HumanMessage(content=question)]},
    config=config,
    stream_mode="messages"
    ):
        if isinstance(msg, AIMessageChunk):
            print(msg.content)
            yield msg.content      
        elif isinstance(msg, AIMessage):
            pass
    
    # print("updating state")
           
    state = workflow.get_state(
            config={"configurable": {"thread_id": thread_id}}
)
    # print(state.values["messages"] )      
                
