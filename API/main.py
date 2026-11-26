"""
FastAPI Entry Point for Rafael Supabase Integration.
Provides a REST API to manage conversations and messages with Supabase Auth and Row Level Security.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from API.config import settings
from API.routers import (
    auth_router,
    conversations_router,
    conversation_messages_router,
    messages_router,
    chat_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown lifecycle management.
    """
    # Startup validation
    try:
        supabase_url = settings.get_supabase_url()
        supabase_key = settings.get_supabase_key()
        print(f"[Rafael API] Initialized with Supabase URL: {supabase_url}")
        print(f"[Rafael API] Supabase API key loaded (starts with: {supabase_key[:12]}...)")
    except ValueError as e:
        print(f"[Rafael API] WARNING: Configuration issue detected: {e}")

    yield

    # Shutdown logic (if any)
    print("[Rafael API] Shutting down Rafael Supabase API.")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base health & info endpoints
@app.get("/", tags=["General"], summary="API Root Status")
async def root():
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "online",
        "documentation": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health", tags=["General"], summary="Health Check")
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "supabase_configured": bool(settings.SUPABASE_URL and (settings.SUPABASE_KEY or settings.SUPABASE_PUBLISHABLE_KEY or settings.SUPABASE_ANON_KEY)),
        },
    )


# Include Routers directly
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(conversation_messages_router)
app.include_router(messages_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "API.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
