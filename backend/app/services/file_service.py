import os
import shutil
import uuid
from pathlib import Path

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import settings

UPLOAD_DIR = "uploads"
TMP_DIR = "tmp_uploads"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpeg",
    ".jpg",
}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


def _is_cloudinary_configured() -> bool:
    return all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    )


def _configure_cloudinary() -> None:
    if not _is_cloudinary_configured():
        return

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def get_file_extension(file: UploadFile) -> str:
    filename = file.filename or ""
    return Path(filename).suffix.lower()


def validate_upload_file(file: UploadFile) -> None:
    extension = get_file_extension(file)

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}."
        )

    max_size = settings.MAX_UPLOAD_MB * 1024 * 1024
    if file.size and file.size > max_size:
        raise ValueError(f"File too large. Max upload size is {settings.MAX_UPLOAD_MB} MB.")


def save_upload_file(file: UploadFile):
    extension = get_file_extension(file)

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        TMP_DIR,
        filename,
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename, file_path


def upload_file_to_cloudinary(file_path: str, public_id: str) -> str:
    if not _is_cloudinary_configured():
        return file_path

    _configure_cloudinary()

    result = cloudinary.uploader.upload(
        file_path,
        public_id=public_id,
        folder=settings.CLOUDINARY_FOLDER,
        resource_type="auto",
        overwrite=True,
    )
    return result["secure_url"]


def cleanup_temp_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)