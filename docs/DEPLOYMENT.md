# Deployment Guide

## Backend on Render
1. Create a new Web Service from the backend directory.
2. Build command:
   - pip install -r requirements.txt
3. Start command:
   - alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
4. Set required environment variables:
   - DATABASE_URL
   - SECRET_KEY
   - GEMINI_API_KEY
   - CORS_ORIGINS
   - CLOUDINARY_* (optional)

## Frontend on Vercel
1. Import repository and select frontend directory.
2. Build command:
   - npm run build
3. Output directory:
   - dist
4. Environment variables:
   - VITE_API_BASE_URL

## Database on Neon
- Provision PostgreSQL database.
- Use SSL connection string in DATABASE_URL.
- Run migrations before serving traffic.
