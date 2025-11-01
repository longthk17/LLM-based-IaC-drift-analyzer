import os
from git import Repo

import config

BASE_REPO_DIR = config.BASE_REPO_DIR


def clone_or_pull(repo_url):
    os.makedirs(BASE_REPO_DIR, exist_ok=True)
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(BASE_REPO_DIR, repo_name)

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
