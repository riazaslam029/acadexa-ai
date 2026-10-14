from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the study note")
    content: str = Field(..., min_length=1, description="Content body of the note")
    subject: str | None = Field(default=None, max_length=100, description="Optional subject or tag")

    @field_validator("title", "content")
    @classmethod
    def validate_not_blank(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return clean


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, description="Updated title")
    content: str | None = Field(default=None, min_length=1, description="Updated content")
    subject: str | None = Field(default=None, max_length=100, description="Updated subject")

    @field_validator("title", "content")
    @classmethod
    def validate_not_blank_optional(cls, v: str | None) -> str | None:
        if v is not None:
            clean = v.strip()
            if not clean:
                raise ValueError("Field cannot be empty or contain only whitespace.")
            return clean
        return None


class NoteResponse(NoteBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)