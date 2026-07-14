from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ArtifactType = Literal[
    "flashcards",
    "mcqs",
    "key_points",
    "study_notes",
    "quizzes",
    "translations",
    "eli5",
    "roadmap",
    "study_plan",
]

DifficultyLevel = Literal["easy", "medium", "hard"]

LanguageCode = Literal["english", "urdu", "arabic", "french", "german"]


class ArtifactGenerateRequest(BaseModel):
    difficulty: DifficultyLevel | None = None
    language: LanguageCode | None = None
    count: int = Field(default=10, ge=1, le=50)


class AIArtifactResponse(BaseModel):
    id: int
    artifact_type: ArtifactType
    title: str | None
    difficulty: str | None
    language: str | None
    payload: dict[str, Any]
    document_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class DeleteResponse(BaseModel):
    message: str
