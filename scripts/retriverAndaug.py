from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline,HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
import os
from dotenv import load_dotenv
load_dotenv()
g_api=os.getenv("GOOGLE_API_KEY")
HUGGINGFACEHUB_ACCESS_TOKEN=os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")


# chat = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",  # use gemini-pro or gemini-1.5-pro if available
#     google_api_key=g_api,
#     temperature=0.7,
#     max_tokens=10000,
#     streaming=True
# )




# )
chat = HuggingFaceEndpoint(
    api_key=HUGGINGFACEHUB_ACCESS_TOKEN,
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    max_new_tokens=5000,
    do_sample=False,
    
)
# chat = HuggingFacePipeline.from_model_id(
#     model_id="gpt2",
#     task='text-generation',
#     model_kwargs={"temperature":0.7, "max_length":1002},
    
# )



prompt=PromptTemplate(
    template="""
    You are a helpful assistant. Please provide an answer to the following question based on the given context.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
   

    Context: {context}
    Question: {question}

    Answer: """,
    input_variables=["context", "question"]
)


def return_context(docs):
  context="\n\n".join(doc.page_content for doc in docs)
  return context



def parser(result):
    return result.content


def chain_llm(retriver):
   Parallel_chain=RunnableParallel({
       'context':retriver| RunnableLambda(return_context),
       'question':RunnablePassthrough()
   }
   )
   chain=RunnableParallel({
      'main': Parallel_chain |prompt | chat | RunnableLambda(parser),
      'raw':RunnablePassthrough()
   }
   )
   return chain
    
def add_vector_store(store):
    global vector_store
    vector_store=store    


def get_chain():
    
    print("Vector store:", vector_store)
    retriver=vector_store.as_retriever(search_type="similarity",search_kwargs={"k":4})
    
    chain=chain_llm(retriver)
    return chain
        

    
    
