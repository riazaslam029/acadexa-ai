from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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
    difficulty: DifficultyLevel | None = Field(default=None, description="Difficulty level (easy, medium, hard)")
    language: LanguageCode | None = Field(default=None, description="Target language")
    count: int = Field(default=10, ge=1, le=50, description="Number of items to generate (1 to 50)")


class AIArtifactResponse(BaseModel):
    id: int
    artifact_type: ArtifactType
    title: str | None = None
    difficulty: str | None = None
    language: str | None = None
    payload: dict[str, Any]
    document_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    message: str
