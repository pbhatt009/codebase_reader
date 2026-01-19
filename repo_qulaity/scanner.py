# scanner.py
import os

IGNORE_DIRS = {
    ".git", "node_modules", "venv", "__pycache__", "dist", "build"
}

IGNORE_EXT = {
    ".min.js", ".lock", ".bin"
}

def scan_repo(repo_path: str):
    files = []
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path {repo_path} does not exist.")
    folders = set()

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for d in dirs:
            folders.add(os.path.join(root, d))

        for file in filenames:
            if any(file.endswith(ext) for ext in IGNORE_EXT):
                continue

            full_path = os.path.join(root, file)

            

            files.append({
                "path": full_path,
                "name": file,
                "ext": os.path.splitext(file)[1],
                
            })

    return {
        "files": files,
        "folders": list(folders)
    }
