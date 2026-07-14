# API Documentation Guide

Interactive Swagger UI is available at:
- /docs

OpenAPI JSON:
- /openapi.json

## Core endpoints

### Auth
- POST /api/v1/auth/register
- POST /api/v1/auth/login

### Users
- GET /api/v1/users/me
- PATCH /api/v1/users/me
- POST /api/v1/users/me/change-password
- DELETE /api/v1/users/me
- GET /api/v1/users/dashboard

### Documents
- POST /api/v1/documents/upload
- GET /api/v1/documents
- GET /api/v1/documents/{id}
- DELETE /api/v1/documents/{id}
- GET /api/v1/documents/search?q=...

### Chat
- POST /api/v1/documents/{id}/chat
- GET /api/v1/documents/{id}/chat/history

### AI generation
- POST + GET /api/v1/documents/{id}/flashcards
- POST + GET /api/v1/documents/{id}/mcqs
- POST + GET /api/v1/documents/{id}/key-points
- POST + GET /api/v1/documents/{id}/notes
- POST + GET /api/v1/documents/{id}/quiz
- POST + GET /api/v1/documents/{id}/translation
- POST + GET /api/v1/documents/{id}/eli5
- POST + GET /api/v1/documents/{id}/roadmap
- POST + GET /api/v1/documents/{id}/study-plan
- DELETE /api/v1/documents/artifacts/{artifact_id}
