from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile_image: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    profile_image: str | None = None


class UserPasswordChange(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserDashboardStats(BaseModel):
    total_documents: int
    total_flashcards: int
    total_quizzes: int
    total_mcqs: int
    total_ai_requests: int
    storage_used_bytes: int


class DashboardResponse(BaseModel):
    stats: UserDashboardStats
    recent_uploads: list[dict]
