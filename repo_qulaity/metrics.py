# metrics.py
import os
import re
from collections import Counter

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
                    1 for s in ["usage", "install", "architecture"]
                    if s in content.lower()
                )
            }
    return {"exists": False, "length": 0, "sections": 0}

