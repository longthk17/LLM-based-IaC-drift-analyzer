import requests
import json

WEBHOOK_URL = (
    "https://uncontributory-jacquline-schmalziest.ngrok-free.dev/webhook/github"
)

payload = {
    "repository": {
        "clone_url": "https://github.com/haihpse150218/terraform-on-aws-ec2.git"
    },
    "ref": "refs/heads/main",
    "pusher": {"name": "testuser"},
    "head_commit": {"id": "dummycommit123"},
}

response = requests.post(WEBHOOK_URL, json=payload)
print(json.dumps(response.json(), indent=4, ensure_ascii=False))
