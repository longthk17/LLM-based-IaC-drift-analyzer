import requests
import json

# ----------------------------
# Test /analyze
# ----------------------------
ANALYZE_URL = "http://127.0.0.1:8000/analyze"
payload_analyze = {
    "repos": ["https://github.com/haihpse150218/terraform-on-aws-ec2.git"]
}

# print("🚀 Sending request to /analyze API...")
# try:
#     resp = requests.post(ANALYZE_URL, json=payload_analyze)
#     resp.raise_for_status()
#     data = resp.json()
#     print("✅ /analyze response:")
#     print(json.dumps(data, indent=4, ensure_ascii=False))
# except requests.exceptions.RequestException as e:
#     print("❌ Error calling /analyze:", e)


# ----------------------------
# Test /webhook/github
# ----------------------------
WEBHOOK_URL = "http://127.0.0.1:8000/webhook/github"

# Giả lập payload GitHub push/release
payload_webhook = {
    "repository": {
        "clone_url": "https://github.com/haihpse150218/terraform-on-aws-ec2.git"
    },
    "ref": "refs/heads/main",
    "pusher": {"name": "testuser"},
    "head_commit": {"id": "dummycommit123"},
}

print("\n🚀 Sending request to /webhook/github API...")
try:
    resp = requests.post(WEBHOOK_URL, json=payload_webhook)
    resp.raise_for_status()
    data = resp.json()
    print("✅ /webhook/github response:")
    print(json.dumps(data, indent=4, ensure_ascii=False))
except requests.exceptions.RequestException as e:
    print("❌ Error calling /webhook/github:", e)
