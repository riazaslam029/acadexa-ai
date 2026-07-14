# Installation Guide

## Prerequisites
- Python 3.12+ (project currently runs in venv with Python 3.14)
- Node.js 20+
- PostgreSQL (Neon or local)
- Tesseract OCR binary for image text extraction

## 1. Clone and setup backend
1. Create virtual environment in backend folder.
2. Install dependencies:
   - pip install -r backend/requirements.txt
3. Configure environment variables in backend/.env:
   - DATABASE_URL
   - SECRET_KEY
   - GEMINI_API_KEY
   - CLOUDINARY_CLOUD_NAME (optional)
   - CLOUDINARY_API_KEY (optional)
   - CLOUDINARY_API_SECRET (optional)

## 2. Run migrations
- cd backend
- alembic upgrade head

## 3. Start backend
- uvicorn app.main:app --reload

## 4. Setup frontend
- cd frontend
- npm install
- add frontend/.env with VITE_API_BASE_URL
- npm run dev

## 5. Optional OCR setup (Fedora)
- sudo dnf install tesseract tesseract-langpack-eng
