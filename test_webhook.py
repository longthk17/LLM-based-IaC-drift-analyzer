import requests
import json
import config

DOMAIN_PUBLIC = config.DOMAIN_PUBLIC

WEBHOOK_URL = f"{DOMAIN_PUBLIC}/webhook/github"

payload = {
    "repository": {"clone_url": "https://github.com/longthk17/terraform-aws-examples"},
    "ref": "refs/heads/main",
    "pusher": {"name": "testuser"},
    "head_commit": {"id": "dummycommit123"},
}

response = requests.post(WEBHOOK_URL, json=payload)
print(json.dumps(response.json(), indent=4, ensure_ascii=False))
