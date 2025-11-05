import os
import json

import config
from core.drift_analyzer import run_drift_analyzer
from core.jsonl_writer import write_jsonl_safely

OUTPUT_DIR = config.OUTPUT_DIR
OUTPUT_FILE = config.OUTPUT_FILE

REPOS_FILE = "repos.json"  # đường dẫn file repos


def load_repos_from_file():
    """Đọc danh sách repo từ repos.json"""
    if not os.path.exists(REPOS_FILE):
        raise FileNotFoundError(f"⚠️ Không tìm thấy file {REPOS_FILE}")

    with open(REPOS_FILE, "r", encoding="utf-8") as f:
        repos = json.load(f)

    if not isinstance(repos, list):
        raise ValueError("❌ repos.json phải là list dạng array JSON")

    return repos


if __name__ == "__main__":
    repos = load_repos_from_file()

    print(f"🚀 Starting IaC Drift Analyzer for {len(repos)} repo(s)...")
    results = run_drift_analyzer(repos)
    print(f"✅ Processed {len(results)} IaC chunks")

    # Đảm bảo thư mục output tồn tại
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ghi file JSON tổng hợp
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"📦 Output written to {OUTPUT_FILE}")
