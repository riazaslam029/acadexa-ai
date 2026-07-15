# Acadexa AI

A production-ready AI-powered learning assistant with document intelligence, adaptive study tooling, and a modern SaaS dashboard.

## Tech Stack

### Frontend
- React + Vite + TypeScript
- Tailwind CSS
- React Router
- React Query
- Framer Motion
- Recharts	
- Axios

### Backend
- FastAPI
- SQLAlchemy 2.x
- Alembic
- JWT Authentication
- Structured logging + global exception handling
- SlowAPI rate limiting
- Cloudinary integration

### Database
- PostgreSQL (Neon)

### AI
- Google Gemini API
- OCR via PyTesseract + Tesseract

## Features

- Authentication (register/login/JWT/protected routes)
- Upload + document extraction (PDF, DOCX, TXT, PNG, JPEG, JPG)
- AI summary and grounded document chat
- Chat history persistence
- AI generation modules:
	- Flashcards
	- MCQs
	- Key Points
	- Study Notes
	- Quizzes
	- Translation
	- Explain Like I am Five
	- Learning Roadmap
	- Study Planner
- Full-text document search
- User profile and dashboard statistics APIs
- Frontend SaaS shell with all requested page routes
- Frontend testing with Vitest + React Testing Library
- Backend testing with Pytest

## Quick Start

See detailed setup docs:
- docs/INSTALLATION.md

Run checks:
- Backend: python -m pytest -q
- Frontend: npm run typecheck && npm run lint && npm run test && npm run build

## Documentation

- docs/ARCHITECTURE.md
- docs/API.md
- docs/DEPLOYMENT.md
- docs/CONTRIBUTING.md

## Status

Active development with production-focused architecture and tooling.