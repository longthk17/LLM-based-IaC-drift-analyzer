import os
import json

import config
from core.drift_analyzer import run_drift_analyzer
from core.jsonl_writer import write_jsonl_safely

OUTPUT_DIR = config.OUTPUT_DIR
OUTPUT_FILE = config.OUTPUT_FILE

if __name__ == "__main__":
    repos = [
        "https://github.com/longthk17/terraform-aws-examples",
    ]

    print(f"🚀 Starting IaC Drift Analyzer for {len(repos)} repo(s)...")
    results = run_drift_analyzer(repos)
    print(f"✅ Processed {len(results)} IaC chunks")

    # Đảm bảo thư mục output tồn tại
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ghi file JSON tổng hợp
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"📦 Output written to {OUTPUT_FILE}")
