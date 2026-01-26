from repo_qulaity.scanner import scan_repo
from repo_qulaity.metrics import readme_metrics, analyze_files, analyze_folder


def calculate_score(path):
    score = 0
    good = []
    bad = []

    # NEW
    file_scores = []
    folder_scores = []
    issues_found = []

    issue_counters = {
        "low_comment_files": 0,
        "large_files": 0,
        "dead_folders": 0,
        "missing_readme_sections": 0
    }

    files_folder_data = scan_repo(path)

    # ---------------- README METRICS ----------------
    readme = readme_metrics(path)

    if readme["exists"]:
        score += 10
        good.append("README file exists")
    else:
        bad.append("README file is missing")
        issues_found.append("README file is missing")

    if readme["length"] >= 300:
        score += 10
        good.append("README has sufficient content")
    else:
        bad.append("README content is too short")

    if readme["sections"] >= 3:
        score += 10
        good.append("README is well structured with sections")
    else:
        issue_counters["missing_readme_sections"] += 1
        bad.append("README lacks proper sections")

    # ---------------- FILE METRICS ----------------
    file_metrics = analyze_files(files_folder_data["files"])
    files = file_metrics["data"]

    if files:
        score += 10
        good.append("Source files are present")
    else:
        bad.append("No source files found")

    total_loc = 0
    total_comment_density = 0

    for f in files:
        f_score = 0
        f_issues = []

        loc = f["line_of_code"]
        density = f["comment_density"]

        total_loc += loc
        total_comment_density += density

        # Comment density
        if density >= 0.20:
            f_score += 4
        elif density < 0.05:
            issue_counters["low_comment_files"] += 1
            f_issues.append("Comment density < 5%")

        # File size
        if loc <= 400:
            f_score += 3
        else:
            issue_counters["large_files"] += 1
            f_issues.append("File exceeds 400 LOC")

        # Has comments
        if f["comment_lines"] > 0:
            f_score += 2

        # Filename sanity
        f_score += 1

        file_scores.append({
            "file": f["file_name"],
            "path": f["path"],
            "loc": loc,
            "comment_density": round(density, 2),
            "score": f_score,
            "issues": f_issues
        })

    avg_comment_density = (
        total_comment_density / len(files) if files else 0
    )

    if avg_comment_density >= 0.2:
        score += 25
        good.append("Code is well commented")
    else:
        bad.append("Low overall comment density")

    if total_loc >= 100:
        score += 15
        good.append("Project has sufficient code complexity")
    else:
        bad.append("Project codebase is too small")

    # ---------------- FOLDER METRICS ----------------
    folder_metrics = analyze_folder(files_folder_data["folders"])

    if folder_metrics:
        score += 10
        good.append("Project uses folders")
    else:
        bad.append("Project lacks folder structure")

    total_depth = 0

    for f in folder_metrics:
        f_score = 0
        f_issues = []

        depth = f["depth_of_folder"]
        total_depth += depth

        if depth <= 4:
            f_score += 4
        else:
            f_issues.append("Deep folder nesting")

        # dead folder check (optional heuristic)
        if f.get("file_count", 1) == 0:
            issue_counters["dead_folders"] += 1
            f_issues.append("Dead folder")
        else:
            f_score += 6

        folder_scores.append({
            "folder": f["path"],
            "depth": depth,
            "score": f_score,
            "issues": f_issues
        })

    avg_depth = (
        total_depth / len(folder_metrics) if folder_metrics else 0
    )

    if avg_depth >= 2:
        score += 10
        good.append("Folder structure is well organized")
    else:
        bad.append("Folder structure is too shallow")

    # ---------------- FINAL ISSUE SUMMARY ----------------
    if issue_counters["low_comment_files"]:
        issues_found.append(
            f"{issue_counters['low_comment_files']} files have comment density < 5%"
        )

    if issue_counters["large_files"]:
        issues_found.append(
            f"{issue_counters['large_files']} files exceed 400 LOC"
        )

    if issue_counters["dead_folders"]:
        issues_found.append(
            f"Dead code detected in {issue_counters['dead_folders']} folder(s)"
        )

    if issue_counters["missing_readme_sections"]:
        issues_found.append(
            "README missing important sections (Usage / Architecture)"
        )

    return {
        "final_score": min(score, 100),
        "good": good,
        "bad": bad,
        "file_scores": file_scores,
        "folder_scores": folder_scores,
        "issues_found": issues_found,
        "issue_counters": issue_counters
    }
