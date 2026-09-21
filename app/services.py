import os
import uuid
import boto3
from fastapi import HTTPException, UploadFile, status

# Read environment variables
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")  # e.g., https://pub-xxx.r2.dev

# Initialize S3 Client configured for Cloudflare R2
s3_client = boto3.client(
    service_name="s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)


def upload_image_to_r2(file: UploadFile, folder: str = "products") -> str:
    """Uploads an image to Cloudflare R2 and returns its public URL."""
    # 1. Validate file extension
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed formats: {', '.join(allowed_extensions)}",
        )

    # 2. Generate a unique filename using UUID to prevent collisions
    unique_filename = f"{folder}/{uuid.uuid4().hex}.{file_ext}"

    try:
        # 3. Upload file stream directly to R2
        s3_client.upload_fileobj(
            file.file,
            R2_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image to Cloudflare R2: {str(e)}",
        )

    # 4. Clean up trailing slash on public URL if present
    base_url = R2_PUBLIC_URL.rstrip("/")
    return f"{base_url}/{unique_filename}"