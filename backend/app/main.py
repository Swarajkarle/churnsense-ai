"""
ChurnSense AI — FastAPI Application Entry Point

Configures CORS, mounts the API router, sets up OpenAPI documentation,
and defines application lifecycle events.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging("DEBUG" if settings.debug else "INFO")

# ── Create upload directory ───────────────────────────────────────────────────
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.model_store_path, exist_ok=True)

# ── FastAPI Application ───────────────────────────────────────────────────────
app = FastAPI(
    title="ChurnSense AI",
    description=(
        "AI-Powered Customer Churn Intelligence & Retention Platform. "
        "Provides churn prediction, explainability, and retention recommendations."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(content={
        "app": "ChurnSense AI",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    })


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment probes."""
    return {"status": "healthy", "version": settings.app_version}
