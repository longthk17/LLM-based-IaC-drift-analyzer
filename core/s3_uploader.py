import os
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")


def clear_repo_output_in_s3(bucket: str, repo_name: str):
    """
    Xóa toàn bộ object thuộc repo_name trên S3.
    VD: s3://bucket/iac_config/terraform-aws-examples/*
    """
    prefix = f"iac_config/{repo_name}/"
    print(f"🧹 Clearing old output for repo: s3://{bucket}/{prefix}")

    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in response:
        print("✅ Không có dữ liệu cũ để xóa.")
        return

    for obj in response["Contents"]:
        print(f"   ❌ deleting {obj['Key']}")
        s3.delete_object(Bucket=bucket, Key=obj["Key"])

    print("✅ Done clearing old output.\n")


def upload_folder_to_s3(local_folder: str, bucket: str, prefix: str):
    uploaded = []

    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = f"{prefix}/{relative_path}"

            try:
                print(f"⬆️ Uploading {local_path} → s3://{bucket}/{s3_key}")
                s3.upload_file(local_path, bucket, s3_key)
                uploaded.append(s3_key)

            except ClientError as e:
                print(f"❌ Upload failed: {local_path} → {e}")
                return {"status": "failed", "error": str(e), "uploaded": uploaded}

    return {"status": "success", "uploaded": uploaded}
