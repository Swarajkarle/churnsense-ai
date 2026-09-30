"""
ChurnSense AI — Prediction Endpoints

POST /predictions/customer      — Individual prediction
POST /predictions/bulk          — Bulk CSV prediction
GET  /predictions               — List prediction history
GET  /predictions/{id}          — Single prediction detail
"""

import csv
import io
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_analyst_or_above
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.orm import MLModel, Prediction, User
from app.schemas.schemas import IndividualPredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

logger = get_logger(__name__)
router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/customer", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def predict_individual(
    payload: IndividualPredictionRequest,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Run churn prediction for a single customer."""
    logger.info(
        "predict_individual endpoint called by user %s for model_id=%s, customer_id=%s, features_count=%d",
        current_user.id, payload.model_id, payload.customer_id, len(payload.features),
    )
    model = await _resolve_model(payload.model_id, current_user, db)
    service = PredictionService()
    result = await service.predict_individual(
        features=payload.features,
        model=model,
        threshold=payload.threshold,
        customer_id=payload.customer_id,
        created_by=str(current_user.id),
        db=db,
    )
    return result


@router.post("/bulk", response_model=List[PredictionResponse], status_code=status.HTTP_201_CREATED)
async def predict_bulk(
    file: UploadFile = File(...),
    model_id: Optional[str] = None,
    threshold: float = 0.5,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Run churn prediction for multiple customers from a CSV file."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted for bulk prediction",
        )

    content = await file.read()
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = list(reader)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV parsing error: {str(e)}",
        )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty",
        )

    if len(rows) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bulk prediction is limited to 10,000 rows per request",
        )

    model = await _resolve_model(model_id, current_user, db)
    service = PredictionService()
    batch_id = str(uuid.uuid4())

    results = []
    for row in rows:
        pred = await service.predict_individual(
            features=dict(row),
            model=model,
            threshold=threshold,
            customer_id=row.get("customer_id"),
            created_by=str(current_user.id),
            db=db,
            batch_id=batch_id,
        )
        results.append(pred)

    return results


@router.get("", response_model=List[PredictionResponse])
async def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List recent predictions for the current user's organization."""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Prediction)
        .options(selectinload(Prediction.explanation), selectinload(Prediction.recommendations))
        .where(Prediction.created_by == str(current_user.id))
        .order_by(Prediction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    return result.scalars().all()


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed prediction result including explanation and recommendations."""
    result = await db.execute(
        select(Prediction)
        .options(selectinload(Prediction.explanation), selectinload(Prediction.recommendations))
        .where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    if prediction.created_by != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return prediction


async def _resolve_model(model_id: Optional[str], current_user: User, db: AsyncSession) -> MLModel:
    """Resolve the model to use: explicit ID, active model, or latest deployed model."""
    if model_id:
        result = await db.execute(
            select(MLModel)
            .options(selectinload(MLModel.metrics))
            .where(MLModel.id == model_id)
        )
        model = result.scalar_one_or_none()
        if not model or model.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
        return model

    # 1. Use active model
    result = await db.execute(
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(
            MLModel.organization_id == current_user.organization_id,
            MLModel.is_active == True,
        )
        .order_by(MLModel.updated_at.desc())
    )
    model = result.scalars().first()
    if model:
        logger.info("Resolved active model %s (%s, algo=%s)", model.id, model.name, model.algorithm)
        return model

    # 2. Fallback to latest deployed model in the organization
    result = await db.execute(
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(
            MLModel.organization_id == current_user.organization_id,
            MLModel.status == "deployed",
        )
        .order_by(MLModel.updated_at.desc())
    )
    model = result.scalars().first()
    if model:
        logger.info("Resolved deployed fallback model %s (%s, algo=%s)", model.id, model.name, model.algorithm)
        return model

    # 3. Fallback to latest trained model
    result = await db.execute(
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(
            MLModel.organization_id == current_user.organization_id,
            MLModel.status == "trained",
        )
        .order_by(MLModel.updated_at.desc())
    )
    model = result.scalars().first()
    if model:
        logger.info("Resolved trained fallback model %s (%s, algo=%s)", model.id, model.name, model.algorithm)
        return model

    logger.warning("No active or deployed model found for organization %s", current_user.organization_id)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No active model found. Train and activate a model first.",
    )
