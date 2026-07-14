from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GEMINI_API_KEY: str
    APP_ENV: str = "development"
    APP_NAME: str = "Acadexa AI API"

    CORS_ORIGINS: str = "http://localhost:5173"

    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    CLOUDINARY_FOLDER: str = "acadexa-ai"

    AI_RATE_LIMIT: str = "30/minute"
    MAX_UPLOAD_MB: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()