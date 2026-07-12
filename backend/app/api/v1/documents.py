from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.crud.document import create_document
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.file_service import save_upload_file

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filename, file_path = save_upload_file(file)

    document = create_document(
        db,
        filename=filename,
        original_name=file.filename,
        file_path=file_path,
        file_size=file.size or 0,
        file_type=Path(file.filename).suffix.lower(),
        owner_id=current_user.id,
    )

    return document