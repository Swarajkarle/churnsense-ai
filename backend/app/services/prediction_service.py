"""
ChurnSense AI — Prediction Service

Orchestrates individual and bulk churn predictions:
  1. Load model and preprocessor from disk
  2. Preprocess input features
  3. Get churn probability
  4. Classify risk level
  5. Generate SHAP explanation
  6. Generate retention recommendations
  7. Persist prediction, explanation, and recommendations to database
"""

import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.evaluation.explainer import ExplainabilityService
from app.ml.preprocessing.preprocessor import ChurnPreprocessor
from app.models.orm import MLModel, Prediction, PredictionExplanation, Recommendation
from app.schemas.schemas import PredictionResponse
from app.services.recommendation_engine import RetentionRecommendationEngine

logger = get_logger(__name__)
settings = get_settings()


def _classify_risk_level(probability: float, threshold: float = 0.5) -> str:
    """
    Map a churn probability to a risk category.

    Thresholds used here are configurable and have not been validated
    as scientifically established cutoffs — they are operational heuristics
    that can be adjusted per business context.
    """
    if probability >= 0.75:
        return "critical"
    elif probability >= threshold:
        return "high"
    elif probability >= 0.3:
        return "medium"
    else:
        return "low"


class PredictionService:
    """Runs end-to-end prediction with explanation and recommendations."""

    def __init__(self):
        self._model_cache: Dict[str, Any] = {}
        self._preprocessor_cache: Dict[str, ChurnPreprocessor] = {}
        self._explainer = ExplainabilityService()
        self._recommendation_engine = RetentionRecommendationEngine()

    async def predict_individual(
        self,
        features: Dict[str, Any],
        model: MLModel,
        threshold: float,
        customer_id: Optional[str],
        created_by: str,
        db: AsyncSession,
        batch_id: Optional[str] = None,
    ) -> Prediction:
        """
        Run a single prediction and persist all results to the database.
        """
        logger.info(
            "Prediction requested: model_id=%s, model_name=%s, algorithm=%s, features_count=%d",
            model.id, model.name, model.algorithm, len(features),
        )

        # 1. Load artifacts (cached in memory for performance)
        sklearn_model = self._load_model(str(model.id), model.artifact_path)
        preprocessor = self._load_preprocessor(str(model.id), model.preprocessing_artifact_path)

        # 2. Build feature DataFrame
        df = pd.DataFrame([features])

        # 3. Align features with preprocessor expectation
        if hasattr(preprocessor, "numeric_features") and hasattr(preprocessor, "categorical_features"):
            for col in preprocessor.numeric_features:
                if col not in df.columns:
                    df[col] = 0.0
                else:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

            for col in preprocessor.categorical_features:
                if col not in df.columns:
                    df[col] = "Unknown"
                else:
                    df[col] = df[col].fillna("Unknown").astype(str)

        # 4. Preprocess
        try:
            X = preprocessor.transform(df)
            logger.info("Features preprocessed successfully: X.shape=%s", X.shape)
        except Exception as e:
            logger.error("Preprocessing failed for model %s: %s", model.id, str(e), exc_info=True)
            raise RuntimeError(f"Preprocessing error: {str(e)}")

        if X.shape[0] == 0:
            raise RuntimeError("Preprocessing produced empty feature matrix")

        # 5. Predict
        try:
            churn_prob = float(sklearn_model.predict_proba(X)[0][1]) if hasattr(sklearn_model, "predict_proba") else float(sklearn_model.predict(X)[0])
            churn_pred = churn_prob >= threshold
            risk_level = _classify_risk_level(churn_prob, threshold)
            logger.info(
                "Prediction result: churn_prob=%.4f, churn_pred=%s, risk_level=%s",
                churn_prob, churn_pred, risk_level,
            )
        except Exception as e:
            logger.error("Model inference failed for model %s: %s", model.id, str(e), exc_info=True)
            raise RuntimeError(f"Model inference error: {str(e)}")

        # 6. Create Prediction record
        prediction = Prediction(
            customer_id=customer_id,
            model_id=str(model.id),
            created_by=created_by,
            churn_probability=round(churn_prob, 6),
            churn_prediction=churn_pred,
            risk_level=risk_level,
            prediction_threshold=threshold,
            input_features=features,
            mode="bulk" if batch_id else "individual",
            batch_id=batch_id,
        )
        db.add(prediction)
        await db.flush()

        # 7. SHAP explanation
        try:
            feature_names = getattr(preprocessor, "feature_names_out", None) or list(features.keys())
            exp_data = self._explainer.explain(sklearn_model, X, feature_names)

            explanation = PredictionExplanation(
                prediction_id=str(prediction.id),
                shap_values=exp_data.get("shap_values"),
                top_risk_factors=exp_data.get("top_risk_factors"),
                top_protective_factors=exp_data.get("top_protective_factors"),
                base_value=exp_data.get("base_value"),
                explanation_method=exp_data.get("explanation_method", "shap"),
            )
            db.add(explanation)

            # 8. Recommendations
            recs = self._recommendation_engine.generate(
                churn_probability=churn_prob,
                risk_level=risk_level,
                features=features,
                shap_top_factors=exp_data.get("top_risk_factors", []),
            )
            for i, rec in enumerate(recs):
                db.add(Recommendation(
                    prediction_id=str(prediction.id),
                    category=rec["category"],
                    title=rec["title"],
                    description=rec["description"],
                    rationale=rec.get("rationale"),
                    priority=rec.get("priority", i + 1),
                ))
            await db.flush()
        except Exception as e:
            logger.error("Explanation/recommendation generation failed: %s", str(e), exc_info=True)

        await db.refresh(prediction, ["explanation", "recommendations"])
        return prediction

    def _resolve_artifact_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        if os.path.isabs(path) and os.path.exists(path):
            return path
        if os.path.exists(path):
            return os.path.abspath(path)
        basename = os.path.basename(path)
        candidates = [
            os.path.join(settings.model_store_path, basename),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml", "models", basename),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "backend", "ml", "models", basename),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "ml", "models", basename),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return path

    def _load_model(self, model_id: str, artifact_path: Optional[str]) -> Any:
        if model_id in self._model_cache:
            return self._model_cache[model_id]
        resolved_path = self._resolve_artifact_path(artifact_path)
        if not resolved_path or not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Model artifact not found: {artifact_path} (resolved: {resolved_path})")
        loaded = joblib.load(resolved_path)
        self._model_cache[model_id] = loaded
        return loaded

    def _load_preprocessor(self, model_id: str, preprocessor_path: Optional[str]) -> ChurnPreprocessor:
        cache_key = f"{model_id}_pre"
        if cache_key in self._preprocessor_cache:
            return self._preprocessor_cache[cache_key]
        resolved_path = self._resolve_artifact_path(preprocessor_path)
        if not resolved_path or not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Preprocessor artifact not found: {preprocessor_path} (resolved: {resolved_path})")
        preprocessor = ChurnPreprocessor.load(resolved_path)
        self._preprocessor_cache[cache_key] = preprocessor
        return preprocessor
