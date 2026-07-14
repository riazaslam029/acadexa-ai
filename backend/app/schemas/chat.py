from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class ChatResponse(BaseModel):
    answer: str


class ChatHistoryResponse(BaseModel):
    id: int
    document_id: int
    owner_id: int
    question: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }