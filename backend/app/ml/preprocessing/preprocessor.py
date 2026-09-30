"""
ChurnSense AI — Preprocessing Pipeline

Builds a reusable sklearn Pipeline/ColumnTransformer that:
1. Applies feature engineering
2. Encodes categorical features
3. Scales numeric features
4. Handles class imbalance where configured

Critical design rule: The same pipeline fitted on training data is
serialized and used identically at inference time to prevent data leakage.
"""

from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from app.core.logging import get_logger
from app.ml.features.feature_engineer import ChurnFeatureEngineer

logger = get_logger(__name__)


class ChurnPreprocessor:
    """
    Encapsulates the entire data preprocessing pipeline for churn prediction.

    Usage:
        preprocessor = ChurnPreprocessor()
        X_train, y_train = preprocessor.fit_transform(df_train, target_col="Churn")
        X_test = preprocessor.transform(df_test)
        preprocessor.save(path)

    The preprocessor can be loaded from disk at inference time:
        preprocessor = ChurnPreprocessor.load(path)
        X = preprocessor.transform(customer_df)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.feature_engineer = ChurnFeatureEngineer()
        self.column_transformer: Optional[ColumnTransformer] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.numeric_features: List[str] = []
        self.categorical_features: List[str] = []
        self.feature_names_out: List[str] = []
        self._is_fitted = False

    def fit_transform(
        self, df: pd.DataFrame, target_col: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit the preprocessor on training data and return (X, y).

        Raises ValueError if target column is missing or y has fewer than 2 classes.
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset. "
                             f"Available columns: {list(df.columns)}")

        df = df.copy()
        y_raw = df.pop(target_col)
        y = self._encode_target(y_raw)

        if len(np.unique(y)) < 2:
            raise ValueError("Target column must have at least 2 distinct classes for classification")

        # Apply feature engineering
        df = self.feature_engineer.fit_transform(df)

        # Infer column types
        self._identify_columns(df)

        # Build and fit column transformer
        self.column_transformer = self._build_column_transformer()
        X = self.column_transformer.fit_transform(df)
        self.feature_names_out = self._get_feature_names()
        self._is_fitted = True

        logger.info(
            "Preprocessor fitted: %d numeric, %d categorical features → %d output features",
            len(self.numeric_features), len(self.categorical_features), X.shape[1],
        )
        return X, y

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Apply the fitted preprocessing pipeline to new data."""
        if not self._is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform()")
        df = df.copy()

        # Apply feature engineering first
        df = self.feature_engineer.transform(df)

        # Ensure all columns required by the column transformer exist
        for col in self.numeric_features:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in self.categorical_features:
            if col not in df.columns:
                df[col] = "Unknown"
            else:
                df[col] = df[col].fillna("Unknown").astype(str)

        return self.column_transformer.transform(df)

    def _encode_target(self, y_raw: pd.Series) -> np.ndarray:
        """Encode target column to binary (0/1)."""
        self.label_encoder = LabelEncoder()
        if y_raw.dtype == object:
            # Map Yes/No, yes/no, True/False to 1/0
            mapping = {"yes": 1, "no": 0, "true": 1, "false": 0, "1": 1, "0": 0, "churn": 1}
            y_lower = y_raw.str.lower().map(mapping)
            if y_lower.isnull().any():
                y_lower = pd.to_numeric(y_raw, errors="coerce")
            return y_lower.fillna(0).astype(int).values
        return pd.to_numeric(y_raw, errors="coerce").fillna(0).astype(int).values

    def _identify_columns(self, df: pd.DataFrame) -> None:
        """Classify DataFrame columns into numeric and categorical."""
        self.numeric_features = [
            c for c in df.columns if df[c].dtype in ("float64", "int64", "float32", "int32")
        ]
        self.categorical_features = [
            c for c in df.columns
            if df[c].dtype == object and c not in self.numeric_features
        ]

    def _build_column_transformer(self) -> ColumnTransformer:
        """Build the sklearn ColumnTransformer with imputation, encoding, and scaling."""
        scale_type = self.config.get("scale_numeric", "standard")
        scaler = StandardScaler() if scale_type == "standard" else None

        numeric_pipeline_steps = [("imputer", SimpleImputer(strategy="median"))]
        if scaler:
            numeric_pipeline_steps.append(("scaler", scaler))
        numeric_pipeline = Pipeline(numeric_pipeline_steps)

        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])

        transformers = []
        if self.numeric_features:
            transformers.append(("numeric", numeric_pipeline, self.numeric_features))
        if self.categorical_features:
            transformers.append(("categorical", categorical_pipeline, self.categorical_features))

        return ColumnTransformer(transformers=transformers, remainder="drop")

    def _get_feature_names(self) -> List[str]:
        """Extract human-readable output feature names from fitted transformer."""
        names = []
        for name, transformer, cols in self.column_transformer.transformers_:
            if name == "numeric":
                names.extend(cols)
            elif name == "categorical":
                ohe = transformer.named_steps["encoder"]
                names.extend(ohe.get_feature_names_out(cols).tolist())
        return names

    def save(self, path: str) -> None:
        """Serialize the fitted preprocessor to disk using joblib."""
        joblib.dump(self, path)
        logger.info("Preprocessor saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "ChurnPreprocessor":
        """Load a previously fitted preprocessor from disk."""
        obj = joblib.load(path)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not a ChurnPreprocessor: {type(obj)}")
        return obj
