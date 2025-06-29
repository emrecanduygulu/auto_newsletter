# utils/r2_uploader.py

import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

def require_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable '{name}' is missing or empty!")
    return value

# --- Load secrets from environment
R2_ACCOUNT_ID = require_env("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = require_env("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = require_env("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = require_env("R2_BUCKET_NAME")
R2_REGION = require_env("R2_REGION")

# --- Set endpoint for R2 S3-compatible API
R2_ENDPOINT = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# --- Create boto3 S3 client
session = boto3.session.Session()
s3 = session.client(
    service_name="s3",
    region_name=R2_REGION,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    endpoint_url=R2_ENDPOINT,
)

def upload_to_r2(file_path, object_name=None):
    """
    Upload the daily JSON file to the bucket,
    and update the index.json file to include this new day.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    print(f"DEBUG: Uploading to bucket '{R2_BUCKET_NAME}' at account '{R2_ACCOUNT_ID}'")

    #  Upload the new daily file
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, R2_BUCKET_NAME, object_name)
        print(f"✅ Uploaded {object_name} to R2 bucket: {R2_BUCKET_NAME}")

    # Extract date from filename (ex: 2025-06-30.json → 2025-06-30)
    new_day = object_name.replace(".json", "").strip()

    # Load current index.json from R2
    index_key = "index.json"
    index_data = []

    try:
        response = s3.get_object(Bucket=R2_BUCKET_NAME, Key=index_key)
        index_bytes = response["Body"].read()
        index_data = json.loads(index_bytes)
        print(f"✅ Loaded existing index.json from R2 with {len(index_data)} entries")
    except s3.exceptions.NoSuchKey:
        print("⚠️ index.json does not exist yet in R2—creating new one")
    except Exception as e:
        print(f"❌ Failed to load index.json: {e}")
        raise

    # Append new day if it's not already present
    if new_day not in index_data:
        index_data.append(new_day)
        index_data.sort()
    else:
        print(f"ℹ️ {new_day} already in index.json")

    # Upload updated index.json back to R2
    updated_index_bytes = json.dumps(index_data, indent=2).encode("utf-8")
    s3.put_object(Bucket=R2_BUCKET_NAME, Key=index_key, Body=updated_index_bytes)
    print(f"✅ Updated index.json in R2 with {len(index_data)} total entries")

