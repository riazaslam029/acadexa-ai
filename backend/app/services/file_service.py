import os
import shutil
import uuid

from fastapi import UploadFile

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload_file(file: UploadFile):
    extension = file.filename.split(".")[-1]

    filename = f"{uuid.uuid4()}.{extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename, file_path