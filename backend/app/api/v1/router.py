"""
ChurnSense AI — API v1 Router
Assembles all endpoint routers under /api/v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, analytics, customers, datasets, models, predictions, reports

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(models.router)
api_router.include_router(predictions.router)
api_router.include_router(customers.router)
api_router.include_router(analytics.router)
api_router.include_router(reports.router)
