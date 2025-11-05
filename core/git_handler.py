import os
import shutil
import stat
from git import Repo, GitCommandError
import config

BASE_REPO_DIR = config.BASE_REPO_DIR


def remove_readonly(func, path, _):
    """
    Fix lỗi PERMISSION DENIED khi delete repo .git trên Windows.
    Linux không cần nhưng vẫn tương thích.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def safe_rmtree(path):
    """Cross-OS safe remove directory."""
    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)


def clone_or_pull(repo_url: str):
    """
    CHỈ dành cho GitHub public repos.
    - Repo tồn tại -> XÓA -> CLONE.
    - Clone shallow depth=1 để phân tích drift.
    - Hoạt động đúng trên cả Windows & Linux.
    """
    os.makedirs(BASE_REPO_DIR, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = os.path.join(BASE_REPO_DIR, repo_name)

    try:
        # Always re-clone
        if os.path.exists(local_path):
            print(f"♻️  Removing old repo: {repo_name}")
            safe_rmtree(local_path)

        print(f"🔹 Cloning {repo_name} (depth=1)...")
        Repo.clone_from(repo_url, local_path, depth=1)  # ✅ always shallow clone

        repo = Repo(local_path)
        commit_sha = repo.head.commit.hexsha[:7]
        print(f"✅ Clone OK: {repo_name} @ {commit_sha}")
        return local_path, commit_sha

    except GitCommandError as e:
        print(f"❌ Git error while cloning {repo_name}: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, None
