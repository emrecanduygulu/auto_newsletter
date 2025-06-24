# utils/r2_uploader.py

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_REGION = os.getenv("R2_REGION")

def upload_to_r2(file_path, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_path)

    r2_endpoint = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        region_name=R2_REGION,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        endpoint_url=r2_endpoint,
    )

    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, R2_BUCKET_NAME, object_name)
        print(f"☁️ Uploaded {object_name} to R2 bucket: {R2_BUCKET_NAME}")
