import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from git import Repo

import config

BASE_REPO_DIR = config.BASE_REPO_DIR


def inject_github_token(repo_url: str) -> str:
    """Thêm token nếu repo GitHub private"""
    token = os.getenv("GITHUB_TOKEN")
    if token and "github.com" in repo_url and "@" not in repo_url:
        return re.sub(r"^https://", f"https://{token}@", repo_url)
    return repo_url


def setup_codecommit_gitconfig():
    """Thiết lập AWS CodeCommit credential helper"""
    os.system(
        "git config --global credential.helper '!aws codecommit credential-helper $@'"
    )
    os.system("git config --global credential.UseHttpPath true")


def clone_or_pull(repo_url):
    os.makedirs(BASE_REPO_DIR, exist_ok=True)
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(BASE_REPO_DIR, repo_name)

    # Detect type
    if "github.com" in repo_url:
        repo_url = inject_github_token(repo_url)
    elif "codecommit" in repo_url:
        setup_codecommit_gitconfig()

    try:
        if os.path.exists(local_path):
            print(f"🔄 Updating existing repo: {repo_name}")
            repo = Repo(local_path)
            repo.git.fetch("--all")
            try:
                default_branch = repo.active_branch.name
            except Exception:
                default_branch = "main"
            repo.git.reset("--hard", f"origin/{default_branch}")
            repo.remotes.origin.pull()
        else:
            print(f"🔹 Cloning new repo: {repo_name}")
            Repo.clone_from(repo_url, local_path, depth=1)

        repo = Repo(local_path)
        commit_sha = repo.head.commit.hexsha[:7]
        return {"repo": repo_name, "commit": commit_sha, "status": "ok"}

    except Exception as e:
        return {"repo": repo_name, "error": str(e), "status": "fail"}


def process_repo_list(repo_list, max_workers=4):
    """Clone/pull nhiều repo song song"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(clone_or_pull, url): url for url in repo_list}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result["status"] == "ok":
                print(f"✅ [{result['repo']}] cloned at {result['commit']}")
            else:
                print(f"❌ [{result['repo']}] error: {result['error']}")
    return results


if __name__ == "__main__":
    # Load list repo từ file JSON
    with open("repos.json") as f:
        repo_list = json.load(f)

    results = process_repo_list(repo_list)
    print("\n📦 Summary:")
    for r in results:
        print(r)
