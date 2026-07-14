from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.rate_limit import limiter

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-ready backend APIs for Acadexa AI.",
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
register_exception_handlers(app)

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