"""
ChurnSense AI — Analytics Endpoints

GET /analytics/overview
GET /analytics/churn
GET /analytics/segments
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.orm import User
from app.schemas.schemas import (
    ChurnTrendPoint,
    OverviewAnalyticsResponse,
    SegmentAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService
from typing import List

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalyticsResponse)
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return top-level KPIs for the executive dashboard."""
    service = AnalyticsService()
    return await service.get_overview(current_user.organization_id, db)


@router.get("/churn", response_model=List[ChurnTrendPoint])
async def get_churn_trend(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return churn trend data by time period."""
    service = AnalyticsService()
    return await service.get_churn_trend(current_user.organization_id, db)


@router.get("/segments", response_model=SegmentAnalyticsResponse)
async def get_segments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return churn breakdown by customer segments."""
    service = AnalyticsService()
    return await service.get_segment_analytics(current_user.organization_id, db)
