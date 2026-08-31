import os

ALLOWED_UPLOAD_CONTENT_TYPES: set[str] = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
