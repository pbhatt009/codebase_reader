from git import Repo
import os
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
    repo_path = os.path.join(clone_dir, repo_name)
    
    if os.path.exists(repo_path):
        print(f"Repository already cloned at {repo_path}")
    else:
        print(f"Cloning repository from {repo_url} to {repo_path}")
        Repo.clone_from(repo_url, repo_path)
    
    return repo_path