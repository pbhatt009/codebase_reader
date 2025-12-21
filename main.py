from dotenv import load_dotenv
import os
load_dotenv()
import uvicorn
from fastapi import FastAPI


## todo add the methods for calling 


from scripts.github_repo_loader import clone_github_repo
from scripts.loader import load_code


repo_path = clone_github_repo("https://github.com/pbhatt009/Ml-Model-Streamlit.git")
documents = load_code(repo_path)

# for doc in documents:
#     print(doc.page_content)
    
