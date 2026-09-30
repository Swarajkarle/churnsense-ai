"""
ChurnSense AI — Analytics Service

Computes KPIs and chart data from real database records.
No fake or hardcoded metrics are returned.
If no data exists, appropriate zeros and empty states are returned.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.orm import Customer, MLModel, ModelMetric, Prediction
from app.schemas.schemas import (
    ChurnTrendPoint,
    OverviewAnalyticsResponse,
    SegmentAnalyticsResponse,
)

logger = get_logger(__name__)


class AnalyticsService:
    """Computes analytics KPIs from database records."""

    async def get_overview(
        self, organization_id: Optional[str], db: AsyncSession
    ) -> OverviewAnalyticsResponse:
        """Compute executive dashboard KPIs."""
        # Customer counts
        total_customers = await db.scalar(
            select(func.count()).select_from(Customer).where(
                Customer.organization_id == organization_id
            )
        ) or 0

        # Customers with predictions
        at_risk = await db.scalar(
            select(func.count()).select_from(Prediction).where(
                Prediction.risk_level.in_(["high", "critical"])
            )
        ) or 0

        predicted_churners = await db.scalar(
            select(func.count()).select_from(Prediction).where(
                Prediction.churn_prediction == True
            )
        ) or 0

        avg_prob_result = await db.execute(
            select(func.avg(Prediction.churn_probability))
        )
        avg_prob = float(avg_prob_result.scalar() or 0.0)

        # Active model metrics
        model_result = await db.execute(
            select(MLModel).where(
                MLModel.organization_id == organization_id,
                MLModel.is_active == True,
            )
        )
        active_model = model_result.scalar_one_or_none()

        model_name = None
        accuracy = precision = recall = f1 = roc_auc = None

        if active_model:
            model_name = active_model.name
            metrics_result = await db.execute(
                select(ModelMetric).where(
                    ModelMetric.model_id == str(active_model.id),
                    ModelMetric.split == "test",
                )
            )
            test_metrics = metrics_result.scalar_one_or_none()
            if test_metrics:
                accuracy = test_metrics.accuracy
                precision = test_metrics.precision
                recall = test_metrics.recall
                f1 = test_metrics.f1_score
                roc_auc = test_metrics.roc_auc

        return OverviewAnalyticsResponse(
            total_customers=total_customers,
            customers_at_risk=at_risk,
            predicted_churners=predicted_churners,
            average_churn_probability=round(avg_prob, 4),
            retention_opportunity_count=at_risk,
            active_model_accuracy=accuracy,
            active_model_precision=precision,
            active_model_recall=recall,
            active_model_f1=f1,
            active_model_roc_auc=roc_auc,
            active_model_name=model_name,
        )

    async def get_churn_trend(
        self, organization_id: Optional[str], db: AsyncSession
    ) -> List[ChurnTrendPoint]:
        """Return monthly churn trend from prediction history."""
        # Group predictions by month
        result = await db.execute(
            select(
                func.to_char(Prediction.created_at, "YYYY-MM").label("period"),
                func.count().label("total"),
                func.sum(func.cast(Prediction.churn_prediction, type_=int)).label("churned"),
            )
            .group_by("period")
            .order_by("period")
            .limit(12)
        )
        rows = result.all()

        trend = []
        for row in rows:
            total = int(row.total or 0)
            churned = int(row.churned or 0)
            trend.append(ChurnTrendPoint(
                period=str(row.period),
                total=total,
                churned=churned,
                churn_rate=round(churned / max(total, 1), 4),
            ))
        return trend

    async def get_segment_analytics(
        self, organization_id: Optional[str], db: AsyncSession
    ) -> SegmentAnalyticsResponse:
        """Return churn breakdown by segment dimensions."""
        # By contract type
        contract_result = await db.execute(
            select(
                Customer.contract_type,
                func.count().label("total"),
                func.sum(func.cast(Customer.churn_label, type_=int)).label("churned"),
            )
            .where(Customer.organization_id == organization_id)
            .group_by(Customer.contract_type)
        )
        by_contract = [
            {
                "contract_type": r.contract_type or "Unknown",
                "total": r.total,
                "churned": int(r.churned or 0),
                "churn_rate": round((r.churned or 0) / max(r.total, 1), 4),
            }
            for r in contract_result.all()
        ]

        # By payment method
        payment_result = await db.execute(
            select(
                Customer.payment_method,
                func.count().label("total"),
                func.sum(func.cast(Customer.churn_label, type_=int)).label("churned"),
            )
            .where(Customer.organization_id == organization_id)
            .group_by(Customer.payment_method)
        )
        by_payment = [
            {
                "payment_method": r.payment_method or "Unknown",
                "total": r.total,
                "churned": int(r.churned or 0),
                "churn_rate": round((r.churned or 0) / max(r.total, 1), 4),
            }
            for r in payment_result.all()
        ]

        # Risk distribution from predictions
        risk_result = await db.execute(
            select(
                Prediction.risk_level,
                func.count().label("count"),
            )
            .group_by(Prediction.risk_level)
        )
        risk_distribution = [
            {"risk_level": r.risk_level, "count": r.count}
            for r in risk_result.all()
        ]

        return SegmentAnalyticsResponse(
            by_contract=by_contract,
            by_tenure_group=[],  # Extended in future versions
            by_payment_method=by_payment,
            risk_distribution=risk_distribution,
        )
