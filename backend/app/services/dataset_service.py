"""
ChurnSense AI — Dataset Service

Handles CSV validation, column profiling, quality scoring,
and preprocessing pipeline orchestration.

Design principle: never silently modify user data.
All detected actions are explicitly reported.
"""

import io
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.orm import Dataset, DatasetColumn
from app.schemas.schemas import (
    DatasetColumnSchema,
    DatasetValidationResult,
    PreprocessingConfigRequest,
)

logger = get_logger(__name__)


class DatasetService:
    """Service for dataset validation and preprocessing."""

    async def validate(self, dataset: Dataset, db: AsyncSession) -> DatasetValidationResult:
        """
        Read a dataset CSV and produce a detailed validation report.

        Returns quality metrics, column profiles, and detected issues.
        Does not modify the file.
        """
        if not os.path.exists(dataset.file_path):
            raise FileNotFoundError(f"Dataset file not found: {dataset.file_path}")

        df = pd.read_csv(dataset.file_path, low_memory=False)

        issues: List[Dict[str, Any]] = []
        warnings: List[str] = []

        # ── Row / column counts ──────────────────────────────────────────────
        row_count, col_count = df.shape

        if row_count == 0:
            issues.append({"severity": "error", "message": "Dataset has no rows"})
        if col_count == 0:
            issues.append({"severity": "error", "message": "Dataset has no columns"})

        # ── Duplicate rows ───────────────────────────────────────────────────
        duplicate_count = int(df.duplicated().sum())
        if duplicate_count > 0:
            warnings.append(f"{duplicate_count} duplicate rows detected")

        # ── Missing values ───────────────────────────────────────────────────
        missing_total = int(df.isnull().sum().sum())
        missing_by_col = df.isnull().sum()
        for col, cnt in missing_by_col[missing_by_col > 0].items():
            pct = round(cnt / row_count * 100, 1)
            severity = "error" if pct > 50 else "warning"
            issues.append({
                "severity": severity,
                "message": f"Column '{col}' has {cnt} missing values ({pct}%)",
                "column": col,
                "missing_count": int(cnt),
                "missing_pct": pct,
            })

        # ── Column type classification ───────────────────────────────────────
        numeric_cols, categorical_cols, boolean_cols = [], [], []
        column_profiles: List[DatasetColumnSchema] = []

        for col in df.columns:
            dtype = df[col].dtype
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())

            if dtype in ("float64", "int64", "float32", "int32"):
                data_type = "numeric"
                numeric_cols.append(col)
                profile = DatasetColumnSchema(
                    column_name=col,
                    data_type=data_type,
                    is_target=False,
                    null_count=null_count,
                    unique_count=unique_count,
                    mean=round(float(df[col].mean()), 4) if not df[col].isnull().all() else None,
                    std=round(float(df[col].std()), 4) if not df[col].isnull().all() else None,
                    min_value=round(float(df[col].min()), 4) if not df[col].isnull().all() else None,
                    max_value=round(float(df[col].max()), 4) if not df[col].isnull().all() else None,
                    top_values=None,
                )
            elif unique_count <= 2 and dtype == "object":
                data_type = "boolean"
                boolean_cols.append(col)
                top = df[col].value_counts().head(5).reset_index().rename(
                    columns={col: "value", "count": "count"}
                ).to_dict("records")
                profile = DatasetColumnSchema(
                    column_name=col,
                    data_type=data_type,
                    is_target=False,
                    null_count=null_count,
                    unique_count=unique_count,
                    mean=None, std=None, min_value=None, max_value=None,
                    top_values=top,
                )
            else:
                data_type = "categorical"
                categorical_cols.append(col)
                top = (
                    df[col].value_counts().head(10).reset_index()
                    .rename(columns={col: "value", "count": "count"})
                    .to_dict("records")
                )
                profile = DatasetColumnSchema(
                    column_name=col,
                    data_type=data_type,
                    is_target=False,
                    null_count=null_count,
                    unique_count=unique_count,
                    mean=None, std=None, min_value=None, max_value=None,
                    top_values=top,
                )

            column_profiles.append(profile)

        # ── Quality score computation ────────────────────────────────────────
        # Score is reduced for missing values, duplicates, and errors.
        # This is a heuristic, not a scientifically established threshold.
        quality_score = 100.0
        missing_pct_total = missing_total / max(row_count * col_count, 1) * 100
        quality_score -= min(missing_pct_total * 2, 40)
        quality_score -= min(duplicate_count / max(row_count, 1) * 100, 20)
        error_count = sum(1 for i in issues if i.get("severity") == "error")
        quality_score -= error_count * 10
        quality_score = max(0.0, round(quality_score, 1))

        # ── Persist column profiles ──────────────────────────────────────────
        dataset.row_count = row_count
        dataset.column_count = col_count
        dataset.quality_score = quality_score
        dataset.status = "validated"
        dataset.validation_report = {
            "issues": issues,
            "warnings": warnings,
            "quality_score": quality_score,
        }
        from sqlalchemy import delete
        await db.execute(delete(DatasetColumn).where(DatasetColumn.dataset_id == str(dataset.id)))

        for profile in column_profiles:
            col_record = DatasetColumn(
                dataset_id=str(dataset.id),
                column_name=profile.column_name,
                data_type=profile.data_type,
                is_target=False,
                null_count=profile.null_count,
                unique_count=profile.unique_count,
                mean=profile.mean,
                std=profile.std,
                min_value=profile.min_value,
                max_value=profile.max_value,
                top_values=profile.top_values,
            )
            db.add(col_record)

        await db.flush()
        logger.info(
            "Dataset %s validated: %d rows, %d cols, quality=%.1f",
            dataset.id, row_count, col_count, quality_score,
        )

        return DatasetValidationResult(
            is_valid=error_count == 0,
            quality_score=quality_score,
            row_count=row_count,
            column_count=col_count,
            missing_values_total=missing_total,
            duplicate_rows=duplicate_count,
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            boolean_columns=boolean_cols,
            issues=issues,
            warnings=warnings,
            column_profiles=column_profiles,
        )

    async def preprocess(
        self,
        dataset: Dataset,
        config: PreprocessingConfigRequest,
        db: AsyncSession,
    ) -> None:
        """
        Record preprocessing configuration on the dataset record.
        Actual preprocessing is executed at training time via the ML pipeline.
        """
        dataset.target_column = config.target_column
        dataset.preprocessing_config = config.model_dump()
        dataset.status = "ready"
        await db.flush()
        logger.info("Dataset %s configured for preprocessing with target='%s'", dataset.id, config.target_column)
