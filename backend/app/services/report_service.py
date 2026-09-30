"""
ChurnSense AI — Report Generation Service
"""

from app.models.orm import MLModel, Report, User
from app.schemas.schemas import ReportGenerateRequest, ReportResponse
from app.services.analytics_service import AnalyticsService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone


class ReportService:
    async def generate(
        self,
        payload: ReportGenerateRequest,
        current_user: User,
        db: AsyncSession,
    ) -> Report:
        analytics = AnalyticsService()
        overview = await analytics.get_overview(current_user.organization_id, db)
        segments = await analytics.get_segment_analytics(current_user.organization_id, db)

        content = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": current_user.email,
            "report_type": payload.report_type,
            "overview": overview.model_dump(),
            "segments": segments.model_dump(),
        }

        if payload.model_id:
            model_result = await db.execute(
                select(MLModel).where(MLModel.id == payload.model_id)
            )
            model = model_result.scalar_one_or_none()
            if model:
                content["model"] = {
                    "name": model.name,
                    "algorithm": model.algorithm,
                    "version": model.version,
                    "hyperparameters": model.hyperparameters,
                    "feature_names": model.feature_names,
                }

        report = Report(
            organization_id=current_user.organization_id or "00000000-0000-0000-0000-000000000000",
            created_by=str(current_user.id),
            title=payload.title,
            report_type=payload.report_type,
            model_id=payload.model_id,
            dataset_id=payload.dataset_id,
            content=content,
        )
        db.add(report)
        await db.flush()
        return report
