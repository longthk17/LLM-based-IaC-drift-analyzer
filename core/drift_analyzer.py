import re
import uuid
from datetime import datetime, timezone

import config
from .git_handler import clone_or_pull
from .terraform_parser import process_directory
from .jsonl_writer import write_jsonl_safely


def extract_owner_repo(repo_url: str):
    """Lấy owner và repo name từ URL GitHub."""
    match = re.search(
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$", repo_url
    )
    if match:
        return match.group("owner"), match.group("repo")
    return "unknown", "unknown"


def normalize_chunk(chunk, repo_url, commit_sha, timestamp):
    """Chuẩn hoá 1 resource block về format chuẩn."""
    owner, repo_name = extract_owner_repo(repo_url)

    return {
        "repo": repo_url,
        "commit": commit_sha,
        "file": chunk.get("file", "unknown"),
        "lines": chunk.get("lines", "0-0"),
        "resource_address": chunk.get("resource_address", "unknown"),
        "resource_type": chunk.get("resource_type", "unknown"),
        "module": chunk.get("module", "root"),
        "account": owner,
        "region": chunk.get("region", "unknown"),
        "content": chunk.get("content", ""),
        "type": "iac_configuration",
        "id": str(uuid.uuid1()),
        "update_at": timestamp,
        "owner": owner,
        "metadata": {
            "repo": repo_url,
            "commit": commit_sha,
            "owner": owner,
            "region": chunk.get("region", "unknown"),
            "account": owner,
        },
    }


def run_drift_analyzer(repos):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_chunks = []

    for repo_url in repos:
        repo_dir, commit_sha = clone_or_pull(repo_url)
        print(f"🔍 Processing repo: {repo_url} @ {commit_sha}")

        if repo_dir is None:
            print(f"⚠️ Bỏ qua {repo_url} vì clone thất bại.\n")
            continue  # <-- Quan trọng: tránh đưa None vào process_directory()
        chunks = process_directory(repo_dir)
        normalized_chunks = []
        for chunk in chunks:
            normalized = normalize_chunk(chunk, repo_url, commit_sha, timestamp)
            normalized_chunks.append(normalized)
            all_chunks.append(normalized)

        # Ghi file theo repo_name trong folder riêng
        _, repo_name = extract_owner_repo(repo_url)
        repo_output_dir = f"output/{repo_name}"
        write_jsonl_safely(
            normalized_chunks,
            repo_output_dir,
            base_name=repo_name,
        )
        print(f"📄 {len(normalized_chunks)} chunks written to {repo_output_dir}")

    print(
        f"✅ Done. Tổng cộng {len(all_chunks)} chunks đã được ghi trong các folder repo riêng."
    )
    return all_chunks
