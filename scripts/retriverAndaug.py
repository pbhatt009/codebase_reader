from langchain_core.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda
import os
from dotenv import load_dotenv
load_dotenv()
g_api=os.getenv("GOOGLE_API_KEY")

chat = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # use gemini-pro or gemini-1.5-pro if available
    google_api_key=g_api,
    temperature=0.7,
    max_tokens=10000




)



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
    
    


def get_response(store,query,k=4):
    
    retriver=store.as_retriever(search_type="similarity",search_kwargs={"k":k})
    chain=chain_llm(retriver)
    data=chain.invoke(query)
    print(type(data["raw"]), data["raw"])

    result={
        'answer':data['main'],
        'source_documents':data['raw']
       
    }
    
    return result