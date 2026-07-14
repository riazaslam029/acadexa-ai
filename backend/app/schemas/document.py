from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_path: str
    file_size: int
    file_type: str
    extracted_text: str | None
    summary: str | None
    processing_status: str
    owner_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }