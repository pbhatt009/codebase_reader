from langchain_community.document_loaders import TextLoader
from pathlib import Path
import os

def load_code(repo_dir=str) -> list:
    docs = []
    
    for file in Path(repo_dir).rglob("*.*"):
        if file.suffix in [".py", ".ipynb", ".md", ".txt", ".csv", ".json",".js",".html",".css",".java",".cpp",""]:
            try:
                loader = TextLoader(
                    str(file),
                    encoding="utf-8",
                    
                )
                docs.extend(loader.load())
            except Exception as e:
                print(f"Skipping {file}: {e}")

    return docs