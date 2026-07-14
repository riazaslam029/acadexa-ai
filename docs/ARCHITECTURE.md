# Architecture Documentation

## Backend layers
- API layer: FastAPI routes under backend/app/api/v1
- Service layer: business logic under backend/app/services
- CRUD layer: SQLAlchemy queries under backend/app/crud
- Models: SQLAlchemy entities under backend/app/models
- Schemas: request/response contracts under backend/app/schemas

## Core patterns
- Dependency injection via FastAPI Depends
- JWT auth with OAuth2PasswordBearer
- Structured logging via structlog
- Global exception handlers for validation and unexpected errors
- Rate limiting for AI endpoints via slowapi

## AI data model
- chat_history table stores per-document conversations
- ai_artifacts table stores generated outputs:
  - flashcards
  - mcqs
  - key_points
  - study_notes
  - quizzes
  - translations
  - eli5
  - roadmap
  - study_plan

## File ingestion flow
1. Validate file type and size
2. Save temporary file
3. Upload to Cloudinary if configured
4. Extract text from PDF/DOCX/TXT/IMG
5. Generate summary with Gemini
6. Persist document + AI output metadata
