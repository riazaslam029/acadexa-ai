from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router

app = FastAPI(
    title="Acadexa AI API",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API v1 routes
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Acadexa AI API 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/test")
def test():
    return {
        "success": True,
        "message": "React is connected to FastAPI 🎉"
    }