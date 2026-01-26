# metrics.py
import os
import re
from collections import Counter

## path where repos are cloned
clone_path="scripts/clone_repo/"

## Analyze README metrics to get quality indicators
## sections:
sections=["usage", "install", "architecture"]
def readme_metrics(repo_path: str):
    for name in ["README.md", "README.txt", "README"]:
        path = os.path.join(repo_path, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {
                "exists": True,
                "length": len(content),
                "sections": sum(
                    1 for s in sections
                    if s in content.lower()
                )
            }
    return {"exists": False, "length": 0, "sections": 0}


# analyze code files to get metrics like lines of code, comment density etc.

def analyze_files(files):
        root=files[0]["path"].replace(clone_path,"").split(os.sep)[0] # root folder name
        data=[]
        # code files in root folder
        root_file=0
        for file in files:
            if not file["path"].endswith((".py", ".js", ".cpp", ".ts")):
                continue
            if os.path.exists(file["path"]):
                with open(file["path"], "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
            else:
                content=""

            content = content.splitlines()

            loc = len(content)
            comment_lines = sum(
                1 for line in content
                if line.strip().startswith(("#", "//", "/*", "*"))
            )

            blank_lines = sum(1 for line in content if not line.strip())
            code_lines = loc - comment_lines - blank_lines

            comment_density = comment_lines / max(code_lines, 1)
            
            if len(file["path"].replace(clone_path,"").split(os.sep))==2:
                root_file+=1

            data.append({
                "file_name": file["name"],
                'path': file["path"],
                
                "line_of_code": loc,
                "comment_lines": comment_lines,
                "comment_density": round(comment_density, 3),
            })
        return {"root_file_cnt": root_file, "data": data}


    


## check the depth of the folder structure

def analyze_folder(folder):
    
    
    root=folder[0].replace(clone_path,"").split(os.sep)[0] # root folder name
    data=[]
    for f in folder:
            path = f
            if os.path.exists(path):
                path = path.replace(clone_path, "")
                max_depth = len(path.split(os.sep)) - 1
                data.append({
                    "file_name": f.split(os.sep)[-1],
                    "path": f,
                    "root_folder": root,
                    "depth_of_folder": max_depth
                })

    return data
