"""
ChurnSense AI — Report Endpoints

POST /reports/generate
GET  /reports
GET  /reports/{id}
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_analyst_or_above
from app.core.database import get_db
from app.models.orm import Report, User
from app.schemas.schemas import ReportGenerateRequest, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    payload: ReportGenerateRequest,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new analytics report."""
    service = ReportService()
    report = await service.generate(payload, current_user, db)
    return report


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reports for the organization."""
    result = await db.execute(
        select(Report)
        .where(Report.organization_id == current_user.organization_id)
        .order_by(Report.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific report by ID."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report or report.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
