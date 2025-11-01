import requests
import json

# URL của API FastAPI (đang chạy trên local)
API_URL = "http://127.0.0.1:8000/analyze"

# Payload mẫu
payload = {"repos": ["https://github.com/haihpse150218/terraform-on-aws-ec2.git"]}

print("🚀 Sending request to API...")

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()

    print("✅ Response status:", response.status_code)
    data = response.json()
    print(json.dumps(data, indent=4, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print("❌ Error calling API:", e)
