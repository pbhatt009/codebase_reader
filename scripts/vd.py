from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
load_dotenv()

def create_vector_store(chunks, hf_model):
    vector_store = FAISS.from_documents(documents=chunks, embedding=hf_model)
    return vector_store