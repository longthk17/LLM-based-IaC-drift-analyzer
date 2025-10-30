import os
import json
import uuid
from datetime import datetime, timezone
from git import Repo
import hcl2

BASE_REPO_DIR = "repos"
OUTPUT_FILE = "drift_output.json"
OWNER = "haihpse150218"


# ===============================================
# Git clone or pull
# ===============================================
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
    commit_sha = repo.head.commit.hexsha[:7]  # lấy SHA ngắn
    return local_path, commit_sha


# ===============================================
# Terraform utilities
# ===============================================
def detect_file_type(file_path):
    if file_path.endswith(".tf"):
        return "terraform"
    elif file_path.endswith(".tfvars"):
        return "tfvars"
    return "unknown"


def get_region(config):
    if not config:
        return "unknown"
    try:
        for block in config.get("provider", []):
            for provider_name, provider_body in block.items():
                if "region" in provider_body:
                    return provider_body["region"]
    except Exception:
        pass
    return "unknown"


def get_module(file_path):
    parts = file_path.split(os.sep)
    if "modules" in parts:
        idx = parts.index("modules")
        return "/".join(parts[idx:])
    return "root"


def calculate_lines(file_path, content):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        start = 1
        end = len(lines)
        return f"{start}-{end}"
    except Exception:
        return "0-0"


def fallback_chunking(file_path):
    """Fallback: tách theo keyword 'resource '"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = []
    for block in content.split("resource "):
        if not block.strip():
            continue
        chunks.append(("resource " + block.strip(), "resource", "unknown"))
    return chunks


# ===============================================
# Parse Terraform config
# ===============================================
def process_directory(directory, tfvars_path=None):
    chunks = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_type = detect_file_type(file_path)
            if file_type not in ["terraform", "tfvars"]:
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            # Parse file AST
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config = hcl2.load(f)
            except Exception:
                config = None

            region = get_region(config)
            module = get_module(file_path)

            # Nếu parse được thì coi toàn file là 1 chunk
            if config:
                chunks.append(
                    {
                        "content": raw_content.strip(),
                        "file": file_path,
                        "block_type": "terraform",
                        "block_name": "terraform",
                        "lines": calculate_lines(file_path, raw_content),
                        "module": module,
                        "region": region,
                    }
                )
            else:
                # fallback
                file_chunks = fallback_chunking(file_path)
                for chunk_content, block_type, block_name in file_chunks:
                    chunks.append(
                        {
                            "content": chunk_content,
                            "file": file_path,
                            "block_type": block_type,
                            "block_name": block_name,
                            "lines": calculate_lines(file_path, chunk_content),
                            "module": module,
                            "region": region,
                        }
                    )
    return chunks


# ===============================================
# Main runner
# ===============================================
def run_drift_analyzer(repos):
    all_chunks = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for repo_url in repos:
        repo_dir, commit_sha = clone_or_pull(repo_url)
        print(f"🔍 Processing repo: {repo_url} @ {commit_sha}")

        try:
            tfvars_path = None
            for root, _, files in os.walk(repo_dir):
                if "vars.tfvars" in files:
                    tfvars_path = os.path.join(root, "vars.tfvars")
                    break

            chunks = process_directory(repo_dir, tfvars_path)
            for chunk in chunks:
                chunk.update(
                    {
                        "repo": repo_url,
                        "commit": commit_sha,
                        "type": "iac_configuration",
                        "id": str(uuid.uuid1()),
                        "updated_at": timestamp,
                        "owner": OWNER,
                    }
                )
            all_chunks.extend(chunks)

        except Exception as e:
            print(f"[ERROR] Failed processing {repo_url}: {e}")

    return all_chunks


# ===============================================
# Entry point
# ===============================================
if __name__ == "__main__":
    repos = [
        "https://github.com/haihpse150218/terraform-on-aws-ec2.git",
    ]

    print(f"🚀 Starting IaC Drift Analyzer for {len(repos)} repo(s)...")
    results = run_drift_analyzer(repos)
    print(f"✅ Processed {len(results)} IaC chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"📦 Output written to {OUTPUT_FILE}")
