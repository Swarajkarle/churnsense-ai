"""
ChurnSense AI — Model Training Pipeline

Trains multiple ML models on a prepared dataset, evaluates them,
and persists the results along with their training metadata.

Models implemented:
    1. Logistic Regression
    2. Decision Tree
    3. Random Forest
    4. Gradient Boosting (sklearn)
    5. XGBoost

All models are evaluated using stratified train/test split.
Accuracy alone is NOT used as the selection criterion because
churn datasets can be class-imbalanced. We report F1, ROC-AUC,
Precision, and Recall alongside Accuracy.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.preprocessing.preprocessor import ChurnPreprocessor

logger = get_logger(__name__)
settings = get_settings()

try:
    from xgboost import XGBClassifier
    _XGBOOST_AVAILABLE = True
except Exception:  # Catches ImportError AND dylib loading errors on macOS without libomp
    _XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not available (missing libomp or not installed) — will be skipped if requested")


# ── Model Registry ──────────────────────────────────────────────────────────

def _build_model(algorithm: str) -> Any:
    """
    Factory for creating an untrained model instance.
    Hyperparameters are sensible defaults — production use should tune these.
    """
    registry = {
        "logistic_regression": lambda: LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        ),
        "decision_tree": lambda: DecisionTreeClassifier(
            max_depth=10,
            class_weight="balanced",
            random_state=42,
        ),
        "random_forest": lambda: RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            max_depth=15,
            n_jobs=-1,
            random_state=42,
        ),
        "gradient_boosting": lambda: GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
        ),
    }
    if _XGBOOST_AVAILABLE:
        registry["xgboost"] = lambda: XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )

    if algorithm not in registry:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. "
            f"Supported: {list(registry.keys())}"
        )
    return registry[algorithm]()


# ── Metrics Computation ─────────────────────────────────────────────────────

def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray],
    feature_names: List[str],
    model: Any,
    split: str = "test",
) -> Dict[str, Any]:
    """Compute a comprehensive set of evaluation metrics."""
    acc = round(float(accuracy_score(y_true, y_pred)), 4)
    prec = round(float(precision_score(y_true, y_pred, zero_division=0)), 4)
    rec = round(float(recall_score(y_true, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_true, y_pred, zero_division=0)), 4)
    cm = confusion_matrix(y_true, y_pred).tolist()

    roc_auc = None
    if y_prob is not None:
        try:
            roc_auc = round(float(roc_auc_score(y_true, y_prob)), 4)
        except Exception:
            pass

    # Feature importances (where supported by the model)
    feature_importances: Optional[Dict[str, float]] = None
    if hasattr(model, "feature_importances_") and feature_names:
        fi = model.feature_importances_
        sorted_pairs = sorted(zip(feature_names, fi), key=lambda x: x[1], reverse=True)
        feature_importances = {k: round(float(v), 6) for k, v in sorted_pairs[:20]}

    return {
        "split": split,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": cm,
        "feature_importances": feature_importances,
    }


# ── Training Pipeline ───────────────────────────────────────────────────────

class ModelTrainer:
    """
    Orchestrates end-to-end model training for one algorithm.

    Steps:
        1. Load dataset CSV
        2. Apply preprocessing
        3. Stratified train/test split
        4. Train model
        5. Compute metrics
        6. Persist model + preprocessor artifacts
    """

    def train(
        self,
        csv_path: str,
        target_col: str,
        algorithm: str,
        test_split: float = 0.2,
        random_state: int = 42,
        preprocessing_config: Optional[Dict[str, Any]] = None,
        output_dir: str = "./ml/models",
    ) -> Dict[str, Any]:
        """
        Train a single model and return metadata + metrics.

        Returns:
            dict with keys: model_id, algorithm, artifact_path,
            preprocessor_path, metrics (train + test), feature_names,
            hyperparameters, training_time_seconds
        """
        start = time.time()
        logger.info("Starting training: algorithm=%s, target=%s", algorithm, target_col)

        # 1. Load data
        df = pd.read_csv(csv_path, low_memory=False)

        # 2. Preprocess
        preprocessor = ChurnPreprocessor(config=preprocessing_config or {})
        X, y = preprocessor.fit_transform(df, target_col)

        # 3. Stratified split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_split,
            random_state=random_state,
            stratify=y,
        )
        logger.info("Split: %d train, %d test samples", len(X_train), len(X_test))

        # 4. Build and train model
        model = _build_model(algorithm)
        model.fit(X_train, y_train)

        # 5. Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        y_train_prob = (
            model.predict_proba(X_train)[:, 1]
            if hasattr(model, "predict_proba") else None
        )
        y_test_prob = (
            model.predict_proba(X_test)[:, 1]
            if hasattr(model, "predict_proba") else None
        )

        feature_names = preprocessor.feature_names_out

        # 6. Metrics
        train_metrics = compute_metrics(y_train, y_train_pred, y_train_prob, feature_names, model, "train")
        test_metrics = compute_metrics(y_test, y_test_pred, y_test_prob, feature_names, model, "test")

        logger.info(
            "Test metrics — acc=%.4f, f1=%.4f, roc_auc=%s",
            test_metrics["accuracy"], test_metrics["f1_score"], test_metrics["roc_auc"],
        )

        # 7. Persist artifacts
        os.makedirs(output_dir, exist_ok=True)
        model_id = str(uuid.uuid4())
        artifact_path = os.path.join(output_dir, f"model_{model_id}.joblib")
        preprocessor_path = os.path.join(output_dir, f"preprocessor_{model_id}.joblib")

        joblib.dump(model, artifact_path)
        preprocessor.save(preprocessor_path)

        elapsed = round(time.time() - start, 2)
        logger.info("Training complete in %.2f seconds. Artifacts: %s", elapsed, artifact_path)

        return {
            "model_id": model_id,
            "algorithm": algorithm,
            "artifact_path": artifact_path,
            "preprocessor_path": preprocessor_path,
            "feature_names": feature_names,
            "hyperparameters": model.get_params(),
            "metrics": [train_metrics, test_metrics],
            "training_time_seconds": elapsed,
        }
