"""MinIO (S3-compatible) object storage client."""

from minio import Minio

from app.core.config import settings

_minio_client: Minio | None = None


def get_storage() -> Minio:
    """Return the shared MinIO client, creating it on first call."""
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        # Ensure the default bucket exists
        if not _minio_client.bucket_exists(settings.minio_bucket):
            _minio_client.make_bucket(settings.minio_bucket)
    return _minio_client
