import json
import requests
import config

DOMAIN_PUBLIC = config.DOMAIN_PUBLIC


ANALYZE_URL = f"{DOMAIN_PUBLIC}/analyze"
payload_analyze = {"repos": ["https://github.com/longthk17/terraform-aws-examples"]}

print("🚀 Sending request to /analyze API...")
try:
    resp = requests.post(ANALYZE_URL, json=payload_analyze)
    resp.raise_for_status()
    data = resp.json()
    print("✅ /analyze response:")
    print(json.dumps(data, indent=4, ensure_ascii=False))
except requests.exceptions.RequestException as e:
    print("❌ Error calling /analyze:", e)
