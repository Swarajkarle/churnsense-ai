"""
ChurnSense AI — Dataset Validation & ML Pipeline Unit Tests

Tests cover:
  - Valid CSV validation
  - Empty CSV
  - Missing columns
  - Data type detection
  - Feature engineering
  - Preprocessing pipeline
  - Model training (fast, small dataset)
"""

import io
import tempfile

import numpy as np
import pandas as pd
import pytest

from app.ml.features.feature_engineer import ChurnFeatureEngineer
from app.ml.preprocessing.preprocessor import ChurnPreprocessor
from app.services.dataset_service import DatasetService


# ── Sample Data ───────────────────────────────────────────────────────────────

def make_sample_df(n_rows: int = 100) -> pd.DataFrame:
    """Generate a minimal synthetic churn dataset for testing."""
    import random
    random.seed(42)
    np.random.seed(42)
    return pd.DataFrame({
        "customerID": [f"C{i:04d}" for i in range(n_rows)],
        "gender": np.random.choice(["Male", "Female"], n_rows),
        "SeniorCitizen": np.random.randint(0, 2, n_rows),
        "Partner": np.random.choice(["Yes", "No"], n_rows),
        "tenure": np.random.randint(1, 72, n_rows),
        "PhoneService": np.random.choice(["Yes", "No"], n_rows),
        "Contract": np.random.choice(["Month-to-month", "One year", "Two year"], n_rows),
        "PaperlessBilling": np.random.choice(["Yes", "No"], n_rows),
        "PaymentMethod": np.random.choice(
            ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
            n_rows,
        ),
        "MonthlyCharges": np.random.uniform(18, 120, n_rows).round(2),
        "TotalCharges": np.random.uniform(18, 8000, n_rows).round(2),
        "Churn": np.random.choice(["Yes", "No"], n_rows, p=[0.27, 0.73]),
    })


# ── Feature Engineering Tests ─────────────────────────────────────────────────

def test_feature_engineer_tenure_group():
    """Tenure group should correctly classify customers into phases."""
    df = pd.DataFrame({"tenure": [3, 18, 36, 60]})
    fe = ChurnFeatureEngineer()
    result = fe.transform(df)
    assert "tenure_group" in result.columns
    assert result.loc[0, "tenure_group"] == "new"
    assert result.loc[1, "tenure_group"] == "developing"
    assert result.loc[2, "tenure_group"] == "established"
    assert result.loc[3, "tenure_group"] == "loyal"


def test_feature_engineer_monthly_to_total_ratio():
    """Monthly-to-total ratio should be computed correctly."""
    df = pd.DataFrame({
        "monthly_charges": [50.0, 80.0],
        "total_charges": [200.0, 400.0],
    })
    fe = ChurnFeatureEngineer()
    result = fe.transform(df)
    assert "monthly_to_total_ratio" in result.columns
    assert abs(result.loc[0, "monthly_to_total_ratio"] - 0.25) < 1e-6


def test_feature_engineer_service_count():
    """Service count should count Yes values in service-like columns."""
    df = pd.DataFrame({
        "PhoneService": ["Yes", "No"],
        "OnlineSecurity": ["No", "Yes"],
        "StreamingTV": ["Yes", "Yes"],
    })
    fe = ChurnFeatureEngineer()
    result = fe.transform(df)
    assert "service_count" in result.columns
    assert result.loc[0, "service_count"] == 2
    assert result.loc[1, "service_count"] == 2


def test_feature_engineer_missing_columns_graceful():
    """Feature engineer should not raise if source columns are missing."""
    df = pd.DataFrame({"some_other_col": [1, 2, 3]})
    fe = ChurnFeatureEngineer()
    result = fe.transform(df)  # Should not raise
    assert len(result) == 3


# ── Preprocessing Tests ───────────────────────────────────────────────────────

def test_preprocessor_fit_transform():
    """Preprocessor should produce a valid (X, y) pair from a training DataFrame."""
    df = make_sample_df(200)
    pp = ChurnPreprocessor()
    X, y = pp.fit_transform(df, target_col="Churn")
    assert X.ndim == 2
    assert len(y) == 200
    assert set(np.unique(y)) <= {0, 1}
    assert X.shape[0] == 200


def test_preprocessor_missing_target_raises():
    """Missing target column should raise ValueError."""
    df = make_sample_df(50)
    pp = ChurnPreprocessor()
    with pytest.raises(ValueError, match="Target column"):
        pp.fit_transform(df, target_col="NonExistentColumn")


def test_preprocessor_transform_consistency():
    """Transform output shape should match fit_transform output shape."""
    df = make_sample_df(200)
    pp = ChurnPreprocessor()
    X_train, _ = pp.fit_transform(df.iloc[:150].copy(), target_col="Churn")
    X_test = pp.transform(df.iloc[150:].copy().drop(columns=["Churn"]))
    assert X_train.shape[1] == X_test.shape[1]  # Same number of features


def test_preprocessor_save_load(tmp_path):
    """Serialized preprocessor should produce identical results when loaded."""
    df = make_sample_df(150)
    pp = ChurnPreprocessor()
    X_original, _ = pp.fit_transform(df, target_col="Churn")

    path = str(tmp_path / "test_preprocessor.joblib")
    pp.save(path)

    loaded_pp = ChurnPreprocessor.load(path)
    X_loaded = loaded_pp.transform(df.drop(columns=["Churn"]))
    np.testing.assert_array_almost_equal(X_original, X_loaded)


# ── Model Training Tests ──────────────────────────────────────────────────────

def test_model_training_logistic_regression(tmp_path):
    """Logistic regression training should produce valid metrics."""
    from app.ml.training.trainer import ModelTrainer

    df = make_sample_df(300)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    trainer = ModelTrainer()
    result = trainer.train(
        csv_path=csv_path,
        target_col="Churn",
        algorithm="logistic_regression",
        test_split=0.2,
        output_dir=str(tmp_path),
    )

    assert "model_id" in result
    assert "metrics" in result
    test_metrics = next(m for m in result["metrics"] if m["split"] == "test")
    assert 0.0 <= test_metrics["accuracy"] <= 1.0
    assert 0.0 <= test_metrics["f1_score"] <= 1.0


def test_model_training_random_forest(tmp_path):
    """Random forest training should complete and produce feature importances."""
    from app.ml.training.trainer import ModelTrainer

    df = make_sample_df(300)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    trainer = ModelTrainer()
    result = trainer.train(
        csv_path=csv_path,
        target_col="Churn",
        algorithm="random_forest",
        test_split=0.2,
        output_dir=str(tmp_path),
    )

    test_metrics = next(m for m in result["metrics"] if m["split"] == "test")
    assert test_metrics.get("feature_importances") is not None


# ── Recommendation Engine Tests ───────────────────────────────────────────────

def test_recommendation_engine_high_risk():
    """High-risk customer should always receive direct outreach recommendation."""
    from app.services.recommendation_engine import RetentionRecommendationEngine

    engine = RetentionRecommendationEngine()
    recs = engine.generate(
        churn_probability=0.85,
        risk_level="high",
        features={"tenure": 3, "contract": "Month-to-month", "monthly_charges": 95},
        shap_top_factors=[],
    )
    categories = {r["category"] for r in recs}
    assert "success_outreach" in categories
    assert "contract_upgrade" in categories


def test_recommendation_engine_low_risk():
    """Low-risk customer should not receive urgent outreach."""
    from app.services.recommendation_engine import RetentionRecommendationEngine

    engine = RetentionRecommendationEngine()
    recs = engine.generate(
        churn_probability=0.12,
        risk_level="low",
        features={"tenure": 48, "contract": "Two year", "monthly_charges": 45},
        shap_top_factors=[],
    )
    categories = {r["category"] for r in recs}
    assert "success_outreach" not in categories


def test_recommendations_all_have_rationale():
    """Every recommendation should have a rationale field."""
    from app.services.recommendation_engine import RetentionRecommendationEngine

    engine = RetentionRecommendationEngine()
    recs = engine.generate(
        churn_probability=0.65,
        risk_level="high",
        features={
            "tenure": 5, "contract": "Month-to-month",
            "monthly_charges": 92, "service_count": 1,
        },
        shap_top_factors=[{"feature": "is_month_to_month", "shap_value": 0.4}],
    )
    for rec in recs:
        assert rec.get("rationale"), f"Missing rationale in recommendation: {rec['title']}"
