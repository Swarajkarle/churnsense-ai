"""
ChurnSense AI — Model Training & Management Endpoints

POST /models/train
GET  /models
GET  /models/{id}
GET  /models/{id}/metrics
POST /models/{id}/activate
DELETE /models/{id}
"""

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_analyst_or_above
from app.core.database import get_db
from app.models.orm import MLModel, User
from app.schemas.schemas import (
    MessageResponse,
    MLModelResponse,
    ModelActivateRequest,
    TrainingRequest,
)
from app.services.training_service import TrainingService

router = APIRouter(prefix="/models", tags=["Models"])


@router.post("/train", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def train_models(
    payload: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Initiate model training as a background task."""
    service = TrainingService()
    run_id = await service.start_training(payload, current_user, db)
    background_tasks.add_task(service.run_training_pipeline, run_id, payload, current_user.organization_id)
    return MessageResponse(message=f"Training initiated. Run ID: {run_id}")


@router.get("", response_model=List[MLModelResponse])
async def list_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all trained models for the organization."""
    result = await db.execute(
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(MLModel.organization_id == current_user.organization_id)
        .order_by(MLModel.created_at.desc())
    )
    models = result.scalars().all()
    return models


@router.get("/{model_id}", response_model=MLModelResponse)
async def get_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a model by ID with its metrics."""
    model = await _get_model_or_404(model_id, current_user, db)
    return model


@router.post("/{model_id}/activate", response_model=MessageResponse)
async def activate_model(
    model_id: str,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Activate a trained model for predictions (deactivates the previous active model)."""
    model = await _get_model_or_404(model_id, current_user, db)
    if model.status != "trained":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only fully trained models can be activated",
        )
    # Deactivate other models in org
    result = await db.execute(
        select(MLModel).where(
            MLModel.organization_id == current_user.organization_id,
            MLModel.is_active == True,
        )
    )
    for m in result.scalars().all():
        m.is_active = False

    model.is_active = True
    model.status = "deployed"
    await db.flush()
    return MessageResponse(message=f"Model '{model.name}' is now the active prediction model")


@router.delete("/{model_id}", response_model=MessageResponse)
async def delete_model(
    model_id: str,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Archive/delete a model (prevents deletion of active model)."""
    model = await _get_model_or_404(model_id, current_user, db)
    if model.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the currently active model. Activate another model first.",
        )
    model.status = "archived"
    await db.flush()
    return MessageResponse(message="Model archived successfully")


async def _get_model_or_404(model_id: str, current_user: User, db: AsyncSession) -> MLModel:
    result = await db.execute(
        select(MLModel).options(selectinload(MLModel.metrics)).where(MLModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    if model.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return model
