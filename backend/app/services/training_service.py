"""
ChurnSense AI — Training Orchestration Service

Bridges the API layer and the ML training pipeline.
Handles database record creation, artifact path management,
and background task execution.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import AsyncSessionFactory
from app.core.logging import get_logger
from app.ml.training.trainer import ModelTrainer
from app.models.orm import Dataset, MLModel, ModelMetric, TrainingRun, User
from app.schemas.schemas import TrainingRequest

logger = get_logger(__name__)
settings = get_settings()


class TrainingService:
    """Orchestrates model training between the API and the ML pipeline."""

    async def start_training(
        self,
        payload: TrainingRequest,
        current_user: User,
        db: AsyncSession,
    ) -> str:
        """Create a training run record and return its ID."""
        run = TrainingRun(
            status="queued",
        )
        db.add(run)
        await db.flush()
        logger.info("Training run %s queued for dataset %s", run.id, payload.dataset_id)
        return str(run.id)

    async def run_training_pipeline(
        self,
        run_id: str,
        payload: TrainingRequest,
        organization_id: Optional[str],
    ) -> None:
        """
        Execute training for all requested algorithms.
        This runs as a FastAPI BackgroundTask — it opens its own DB session.
        """
        async with AsyncSessionFactory() as db:
            try:
                # Update run status
                result = await db.execute(select(TrainingRun).where(TrainingRun.id == run_id))
                run = result.scalar_one_or_none()
                if not run:
                    logger.error("Training run %s not found", run_id)
                    return

                run.status = "running"
                run.started_at = datetime.now(timezone.utc)
                await db.commit()

                # Fetch dataset
                ds_result = await db.execute(select(Dataset).where(Dataset.id == payload.dataset_id))
                dataset = ds_result.scalar_one_or_none()
                if not dataset or not os.path.exists(dataset.file_path):
                    raise FileNotFoundError(f"Dataset file not found: {payload.dataset_id}")

                trainer = ModelTrainer()
                output_dir = settings.model_store_path

                for algorithm in payload.algorithms:
                    logger.info("Training %s for run %s", algorithm, run_id)
                    try:
                        result_data = trainer.train(
                            csv_path=dataset.file_path,
                            target_col=payload.target_column,
                            algorithm=algorithm,
                            test_split=payload.test_split,
                            random_state=payload.random_state,
                            preprocessing_config=(
                                payload.preprocessing_config.model_dump()
                                if payload.preprocessing_config else {}
                            ),
                            output_dir=output_dir,
                        )

                        # Persist model record
                        model_name = f"{algorithm.replace('_', ' ').title()} v{str(uuid.uuid4())[:8]}"
                        ml_model = MLModel(
                            id=result_data["model_id"],
                            organization_id=organization_id or "00000000-0000-0000-0000-000000000000",
                            name=model_name,
                            algorithm=algorithm,
                            version="1.0.0",
                            status="trained",
                            is_active=False,
                            artifact_path=result_data["artifact_path"],
                            preprocessing_artifact_path=result_data["preprocessor_path"],
                            feature_names=result_data["feature_names"],
                            hyperparameters=result_data["hyperparameters"],
                            training_dataset_id=payload.dataset_id,
                            training_dataset_version=dataset.version,
                            test_split=payload.test_split,
                            random_state=payload.random_state,
                            notes=payload.notes,
                        )
                        db.add(ml_model)
                        await db.flush()

                        # Persist metrics
                        for metric_data in result_data["metrics"]:
                            metric = ModelMetric(
                                model_id=str(ml_model.id),
                                split=metric_data["split"],
                                accuracy=metric_data.get("accuracy"),
                                precision=metric_data.get("precision"),
                                recall=metric_data.get("recall"),
                                f1_score=metric_data.get("f1_score"),
                                roc_auc=metric_data.get("roc_auc"),
                                confusion_matrix=metric_data.get("confusion_matrix"),
                                feature_importances=metric_data.get("feature_importances"),
                            )
                            db.add(metric)

                        await db.flush()
                        logger.info("Model %s (%s) saved successfully", ml_model.id, algorithm)

                    except Exception as e:
                        logger.error("Algorithm %s failed: %s", algorithm, str(e))

                run.status = "completed"
                run.completed_at = datetime.now(timezone.utc)
                if run.started_at:
                    run.duration_seconds = (
                        run.completed_at - run.started_at
                    ).total_seconds()
                await db.commit()
                logger.info("Training run %s completed", run_id)

            except Exception as e:
                logger.error("Training run %s failed: %s", run_id, str(e))
                async with AsyncSessionFactory() as err_db:
                    err_result = await err_db.execute(
                        select(TrainingRun).where(TrainingRun.id == run_id)
                    )
                    err_run = err_result.scalar_one_or_none()
                    if err_run:
                        err_run.status = "failed"
                        err_run.error_message = str(e)
                        err_run.completed_at = datetime.now(timezone.utc)
                        await err_db.commit()
