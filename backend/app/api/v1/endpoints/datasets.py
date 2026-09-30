"""
ChurnSense AI — Dataset Management Endpoints

POST /datasets/upload
GET  /datasets
GET  /datasets/{id}
DELETE /datasets/{id}
POST /datasets/{id}/validate
POST /datasets/{id}/preprocess
"""

import os
import uuid
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_analyst_or_above
from app.core.config import get_settings
from app.core.database import get_db
from app.models.orm import Dataset, User
from app.schemas.schemas import (
    DatasetResponse,
    DatasetValidationResult,
    MessageResponse,
    PreprocessingConfigRequest,
)
from app.services.dataset_service import DatasetService

router = APIRouter(prefix="/datasets", tags=["Datasets"])
settings = get_settings()


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form("Unnamed Dataset"),
    description: str = Form(""),
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV dataset file."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted",
        )

    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {settings.max_upload_size_mb} MB limit",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}.csv")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    dataset = Dataset(
        organization_id=current_user.organization_id or "00000000-0000-0000-0000-000000000000",
        uploaded_by=str(current_user.id),
        name=name,
        description=description,
        file_path=file_path,
        file_size_bytes=len(content),
        status="uploaded",
    )
    db.add(dataset)
    await db.flush()
    await db.refresh(dataset, ["columns"])
    return dataset


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all datasets for the current user's organization."""
    org_id = current_user.organization_id
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.organization_id == org_id)
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific dataset by ID."""
    dataset = await _get_dataset_or_404(dataset_id, current_user, db)
    return dataset


@router.delete("/{dataset_id}", response_model=MessageResponse)
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Delete a dataset and its associated file."""
    dataset = await _get_dataset_or_404(dataset_id, current_user, db)
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    await db.delete(dataset)
    return MessageResponse(message="Dataset deleted successfully")


@router.post("/{dataset_id}/validate", response_model=DatasetValidationResult)
async def validate_dataset(
    dataset_id: str,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Run validation analysis on the uploaded dataset."""
    dataset = await _get_dataset_or_404(dataset_id, current_user, db)
    service = DatasetService()
    result = await service.validate(dataset, db)
    return result


@router.post("/{dataset_id}/preprocess", response_model=MessageResponse)
async def preprocess_dataset(
    dataset_id: str,
    config: PreprocessingConfigRequest,
    current_user: User = Depends(require_analyst_or_above),
    db: AsyncSession = Depends(get_db),
):
    """Apply preprocessing pipeline and prepare dataset for training."""
    dataset = await _get_dataset_or_404(dataset_id, current_user, db)
    service = DatasetService()
    await service.preprocess(dataset, config, db)
    return MessageResponse(message="Dataset preprocessing initiated successfully")


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_dataset_or_404(
    dataset_id: str,
    current_user: User,
    db: AsyncSession,
) -> Dataset:
    result = await db.execute(
        select(Dataset).options(selectinload(Dataset.columns)).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    if dataset.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return dataset
