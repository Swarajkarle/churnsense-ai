"""
ChurnSense AI — Customer Endpoints

GET /customers
GET /customers/{id}
GET /customers/{id}/explanation
GET /customers/{id}/recommendations
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.orm import Customer, Prediction, User
from app.schemas.schemas import (
    CustomerDetailResponse,
    CustomerResponse,
    PredictionExplanationSchema,
    RecommendationSchema,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List customers with optional search and risk-level filtering."""
    query = select(Customer).where(Customer.organization_id == current_user.organization_id)
    if search:
        search_pattern = f"%{search}%"
        from sqlalchemy import or_
        query = query.where(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.external_id.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
            )
        )
    offset = (page - 1) * page_size
    query = query.order_by(Customer.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full Customer 360 profile including latest prediction and history."""
    customer = await _get_customer_or_404(customer_id, current_user, db)

    # Latest prediction
    pred_result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    latest = pred_result.scalar_one_or_none()

    # History (last 10)
    hist_result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(Prediction.created_at.desc())
        .limit(10)
    )
    history = hist_result.scalars().all()

    return CustomerDetailResponse(
        **CustomerResponse.model_validate(customer).model_dump(),
        latest_prediction=latest,
        prediction_history=history,
    )


@router.get("/{customer_id}/explanation", response_model=PredictionExplanationSchema)
async def get_customer_explanation(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest SHAP-based prediction explanation for a customer."""
    from app.models.orm import PredictionExplanation

    customer = await _get_customer_or_404(customer_id, current_user, db)
    pred_result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    prediction = pred_result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No predictions found for this customer",
        )

    exp_result = await db.execute(
        select(PredictionExplanation).where(
            PredictionExplanation.prediction_id == str(prediction.id)
        )
    )
    explanation = exp_result.scalar_one_or_none()
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No explanation available for the latest prediction",
        )
    return explanation


@router.get("/{customer_id}/recommendations", response_model=List[RecommendationSchema])
async def get_customer_recommendations(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get retention recommendations for the customer's latest prediction."""
    from app.models.orm import Recommendation

    customer = await _get_customer_or_404(customer_id, current_user, db)
    pred_result = await db.execute(
        select(Prediction)
        .where(Prediction.customer_id == customer_id)
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    prediction = pred_result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No predictions found for this customer",
        )

    rec_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.prediction_id == str(prediction.id))
        .order_by(Recommendation.priority)
    )
    return rec_result.scalars().all()


async def _get_customer_or_404(customer_id: str, current_user: User, db: AsyncSession) -> Customer:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if customer.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return customer
