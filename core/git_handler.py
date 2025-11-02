import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from git import Repo, GitCommandError

import config

BASE_REPO_DIR = config.BASE_REPO_DIR


# ==========================================================
# 🔐 Authentication helpers
# ==========================================================
def inject_github_token(repo_url: str) -> str:
    """Thêm token vào URL nếu là GitHub private"""
    token = os.getenv("GITHUB_TOKEN")
    if token and "github.com" in repo_url and "@" not in repo_url:
        repo_url = re.sub(r"^https://", f"https://{token}@", repo_url)
    return repo_url


def setup_codecommit_gitconfig():
    """Thiết lập credential helper cho AWS CodeCommit"""
    os.system(
        "git config --global credential.helper '!aws codecommit credential-helper $@'"
    )
    os.system("git config --global credential.UseHttpPath true")


# ==========================================================
# 🌀 Clone or pull single repo
# ==========================================================
def clone_or_pull(repo_url: str):
    """
    Clone hoặc pull một repo. 
    Tự động detect GitHub / AWS CodeCommit, xử lý credential và cập nhật branch chính.
    """
    os.makedirs(BASE_REPO_DIR, exist_ok=True)
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = os.path.join(BASE_REPO_DIR, repo_name)

    # Detect type & prepare credentials
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
        return local_path, commit_sha

    except GitCommandError as ge:
        print(f"❌ Git error while processing {repo_name}: {ge}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error while processing {repo_name}: {e}")
        return None, None


# ==========================================================
# ⚡ Process multiple repos in parallel
# ==========================================================
def process_repo_list(repo_list, max_workers=4):
    """Clone/pull nhiều repo song song"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(clone_or_pull, url): url for url in repo_list}
        for future in as_completed(futures):
            repo_url = futures[future]
            try:
                local_path, commit_sha = future.result()
                if local_path:
                    results.append({"repo": repo_url, "path": local_path, "commit": commit_sha})
                    print(f"✅ [{repo_url}] cloned at {commit_sha}")
                else:
                    results.append({"repo": repo_url, "status": "fail"})
            except Exception as e:
                results.append({"repo": repo_url, "error": str(e), "status": "fail"})
                print(f"❌ [{repo_url}] error: {e}")
    return results
