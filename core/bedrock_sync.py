import boto3
import time
from botocore.exceptions import ClientError

import config

bedrock = boto3.client("bedrock-agent", region_name="us-east-1")

# ⚙️ Knowledge Base ID cố định của bạn
KNOWLEDGE_BASE_ID = config.KNOWLEDGE_BASE_ID


def sync_data_source_by_repo(s3_repo_path: str):
    """
    Sync hoặc tạo mới Data Source cho từng repo trong Bedrock Knowledge Base.
    :param s3_repo_path: ví dụ 's3://drift-iac-kb/repoA/'
    """
    # Chuẩn hóa path
    s3_repo_path = s3_repo_path.rstrip("/") + "/"

    # Tách bucket và prefix chính xác
    no_scheme = s3_repo_path.replace("s3://", "")
    bucket_name, prefix = no_scheme.split("/", 1)
    repo_name = prefix.rstrip("/").split("/")[-1]

    print(f"🔍 Checking data source for repo: {repo_name}")

    # 1️⃣ Lấy danh sách data source hiện có
    existing_sources = bedrock.list_data_sources(knowledgeBaseId=KNOWLEDGE_BASE_ID)
    ds = next(
        (
            d
            for d in existing_sources.get("dataSourceSummaries", [])
            if d.get("name") == repo_name
        ),
        None,
    )

    # 2️⃣ Nếu chưa có → tạo mới Data Source
    if not ds:
        print(f"🆕 Creating new data source for {repo_name}")

        ds = bedrock.create_data_source(
            name=repo_name,
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceConfiguration={
                "type": "S3",  # ✅ BẮT BUỘC
                "s3Configuration": {
                    "bucketArn": f"arn:aws:s3:::{bucket_name}",
                    "inclusionPrefixes": [prefix],  # ✅ SỬA LẠI CHỖ NÀY
                },
            },
            description=f"Data source for {repo_name}",
            dataDeletionPolicy="DELETE",  # hoặc "RETAIN"
        )["dataSource"]

        data_source_id = ds["dataSourceId"]
        print(f"✅ Created new data source: {data_source_id}")

    else:
        data_source_id = ds["dataSourceId"]
        print(f"♻️ Found existing data source: {data_source_id}")

    # 3️⃣ Bắt đầu sync (ingestion job)
    print(f"🚀 Starting ingestion job for {repo_name}...")
    try:
        job = bedrock.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID, dataSourceId=data_source_id
        )

        job_id = job["ingestionJob"]["ingestionJobId"]
        print(f"✅ Ingestion job {job_id} started successfully.")
        return {
            "repo": repo_name,
            "data_source_id": data_source_id,
            "ingestion_job_id": job_id,
            "status": "STARTED",
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConflictException":
            print(
                f"⚠️ Job already running for {data_source_id}, skipping new ingestion."
            )
            return {"status": "already_running", "data_source_id": data_source_id}
        else:
            raise e
