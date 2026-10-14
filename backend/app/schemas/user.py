from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (at least 8 characters)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Name must be at least 2 non-whitespace characters.")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if v.strip() != v:
            raise ValueError("Password cannot start or end with whitespace.")
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile_image: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100, description="Updated full name")
    profile_image: str | None = Field(default=None, max_length=500, description="Profile image URL")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            clean = v.strip()
            if len(clean) < 2:
                raise ValueError("Name must be at least 2 non-whitespace characters.")
            return clean
        return None


class UserPasswordChange(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128, description="Current account password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New account password")

    @model_validator(mode="after")
    def verify_passwords_differ(self) -> "UserPasswordChange":
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password.")
        return self


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
