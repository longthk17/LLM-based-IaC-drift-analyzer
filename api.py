from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

from core.drift_analyzer import run_drift_analyzer
from config import OUTPUT_DIR, OUTPUT_FILE  # Nếu vẫn muốn giữ file tổng hợp

app = FastAPI(
    title="IaC Drift Analyzer API",
    description="API phát hiện drift trong IaC configuration (Terraform)",
    version="1.0.0",
)


class AnalyzeRequest(BaseModel):
    repos: List[str]


@app.get("/")
def root():
    return {"message": "IaC Drift Analyzer API is running 🚀"}


@app.post("/analyze")
def analyze_iac(request: AnalyzeRequest):
    if not request.repos:
        raise HTTPException(status_code=400, detail="Danh sách repo không được rỗng")

    print(f"🚀 Start analyzing {len(request.repos)} repo(s)...")

    try:
        # 🔹 Gọi hàm đồng bộ
        results = run_drift_analyzer(request.repos)

        # Ghi file JSON tổng hợp (tuỳ chọn)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        print(f"✅ Done. {len(results)} IaC chunks processed.")

        # Lấy danh sách owner đã detect
        owners = sorted(set(r["owner"] for r in results if r.get("owner")))

        return {
            "status": "success",
            "message": f"Processed {len(results)} IaC chunks",
            "repos_analyzed": request.repos,
            "owners_detected": owners,
            "output_dir": OUTPUT_DIR,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
