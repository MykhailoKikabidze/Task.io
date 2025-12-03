from minio import Minio
from config import get_settings

settings = get_settings()

minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False  # True if HTTPS
)


def upload_file(bucket_name: str, file_data, file_name: str, content_type: str) -> str:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    minio_client.put_object(
        bucket_name,
        file_name,
        file_data,
        length=-1,
        part_size=10*1024*1024,
        content_type=content_type
    )

    return f"http://{settings.MINIO_PUBLIC_HOST}/{bucket_name}/{file_name}"
