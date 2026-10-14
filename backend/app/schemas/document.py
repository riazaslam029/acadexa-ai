from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_path: str
    file_size: int
    file_type: str
    extracted_text: str | None = None
    summary: str | None = None
    processing_status: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)