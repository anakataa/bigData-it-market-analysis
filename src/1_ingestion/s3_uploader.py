import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_s3_client():
    """
    Create and return AWS S3 client.
    """

    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )



def upload_file_to_s3(local_path: str, s3_key: str):
    """
    Upload local file to AWS S3.

    Args:
        local_path: local file path
        s3_key: destination path inside S3 bucket
    """

    s3_client = get_s3_client()

    try:
        # Upload file into configured bucket
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"Uploaded {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
    # Handle AWS upload errors
    except ClientError as error:
        print(f"S3 upload error: {error}")