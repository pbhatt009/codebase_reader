from git import Repo
import os
import requests
from repo_qulaity.score_cal import calculate_score

def flattree(github_tree):
   
    root = []

    for item in github_tree:
        # We only care about files (folders are implied by paths)
        if item["type"] != "blob":
            continue

        parts = item["path"].split("/")
        current_level = root
        current_path = ""

        for i, part in enumerate(parts):
            current_path = f"{current_path}/{part}" if current_path else f"/{part}"

            # Check if node already exists
            node = next((n for n in current_level if n["name"] == part), None)

            if not node:
                is_file = i == len(parts) - 1
                node = {
                    "name": part,
                    "type": "file" if is_file else "folder",
                    "path": current_path,
                    "url":item["url"]
                }

                if not is_file:
                    node["children"] = []

                current_level.append(node)

            # Move deeper if folder
            if node["type"] == "folder":
                current_level = node["children"]

    return root

    

def gettree(repo_owner,repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/main?recursive=1"
    headers = {}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()["tree"]
    result=flattree(data)
    return result
  
  

def repodetail(repo_owner,repo_name):
    url=f"https://api.github.com/repos/{repo_owner}/{repo_name}" 
    headers = {}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return {"id":data["id"],"repo_name":data["name"],"private":data["private"],"owner_name":data["owner"]["login"],"owner_avatar url":data["owner"]["avatar_url"],"description":data["description"]}


    
def clone_github_repo(repo_url: str, clone_dir:str="scripts/clone_repo") -> str:
    """
    Clones a GitHub repository to a specified directory.

    Args:
        repo_url (str): The URL of the GitHub repository.
        clone_dir (str): The directory where the repository should be cloned.

    Returns:
        str: The path to the cloned repository.
    """
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
    
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_owner=repo_url.split("/")[-2]
    
    repo_path = os.path.join(clone_dir, repo_name)
    
    if os.path.exists(repo_path):
        print(f"Repository already cloned at {repo_path}")
    else:
        print(f"Cloning repository from {repo_url} to {repo_path}")
        Repo.clone_from(repo_url, repo_path)
    score=calculate_score(repo_path)
        
    tree=gettree(repo_owner,repo_name)
    repo_info=repodetail(repo_owner,repo_name)
    repo_info["score"]=score
    repo_info["url"]=repo_url
    
    
    return {"path":repo_path,"tree":tree,"repo_info":repo_info}