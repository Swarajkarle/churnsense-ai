"""
ChurnSense AI — SHAP-Based Explainability Service

Produces human-readable explanations of individual predictions
using SHAP (SHapley Additive exPlanations).

Important disclaimer (displayed in UI):
"Explanations describe the model's behavior on this input.
They are not guaranteed causal explanations of why the customer
will or will not churn."
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.core.logging import get_logger
from app.schemas.schemas import PredictionExplanationSchema, PredictionFactorSchema

logger = get_logger(__name__)

try:
    import shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False
    logger.warning("SHAP not available — falling back to feature importance explanations")


class ExplainabilityService:
    """
    Generates SHAP-based explanations for individual customer predictions.

    Strategy:
        - TreeExplainer for tree-based models (RF, GB, XGBoost) — efficient
        - LinearExplainer for Logistic Regression
        - KernelExplainer as universal fallback (slower, use for small inputs)
    """

    def explain(
        self,
        model: Any,
        X_instance: np.ndarray,
        feature_names: List[str],
        background_data: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Compute SHAP values for a single prediction instance.

        Parameters:
            model:          Fitted sklearn/XGBoost estimator
            X_instance:     Shape (1, n_features) — the single input to explain
            feature_names:  Names corresponding to columns in X_instance
            background_data: Optional sample of training data for KernelExplainer

        Returns:
            dict with shap_values, top_risk_factors, top_protective_factors, base_value
        """
        if not _SHAP_AVAILABLE:
            return self._feature_importance_fallback(model, X_instance, feature_names)

        try:
            return self._shap_explain(model, X_instance, feature_names, background_data)
        except Exception as e:
            logger.warning("SHAP explanation failed (%s), using fallback", str(e))
            return self._feature_importance_fallback(model, X_instance, feature_names)

    def _shap_explain(
        self,
        model: Any,
        X_instance: np.ndarray,
        feature_names: List[str],
        background_data: Optional[np.ndarray],
    ) -> Dict[str, Any]:
        """SHAP-based explanation for a supported model type."""
        model_type = type(model).__name__.lower()

        if any(t in model_type for t in ("forest", "tree", "gradient", "xgb")):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_instance)
            if hasattr(explainer.expected_value, "__len__"):
                base_value = float(explainer.expected_value[1] if len(explainer.expected_value) > 1 else explainer.expected_value[0])
            else:
                base_value = float(explainer.expected_value)

            # For binary classifiers, TreeExplainer returns 3D array (1, n_features, 2) or list [class0, class1]
            if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3 and shap_values.shape[2] == 2:
                sv = shap_values[0, :, 1]
            elif isinstance(shap_values, list) and len(shap_values) == 2:
                sv = shap_values[1][0]
            else:
                sv = shap_values[0] if shap_values.ndim > 1 else shap_values

        elif "logistic" in model_type or "linear" in model_type:
            if background_data is not None:
                bg = shap.maskers.Independent(background_data[:100])
            else:
                bg = shap.maskers.Independent(X_instance)
            explainer = shap.LinearExplainer(model, masker=bg)
            shap_values = explainer.shap_values(X_instance)
            base_value = float(explainer.expected_value)
            sv = shap_values[0] if shap_values.ndim > 1 else shap_values

        else:
            # Universal fallback: KernelExplainer (slower)
            bg = background_data[:50] if background_data is not None else X_instance
            explainer = shap.KernelExplainer(model.predict_proba, bg)
            shap_values = explainer.shap_values(X_instance, nsamples=100)
            base_value = float(explainer.expected_value[1])
            sv = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]

        return self._build_explanation(sv, X_instance[0], feature_names, base_value, method="shap")

    def _feature_importance_fallback(
        self,
        model: Any,
        X_instance: np.ndarray,
        feature_names: List[str],
    ) -> Dict[str, Any]:
        """
        When SHAP is unavailable, use feature importances as a coarse approximation.
        These are model-global importances multiplied by feature value signs,
        NOT SHAP values, and should be labeled accordingly.
        """
        if hasattr(model, "feature_importances_"):
            fi = model.feature_importances_
        elif hasattr(model, "coef_"):
            fi = np.abs(model.coef_[0])
        else:
            fi = np.ones(X_instance.shape[1])

        instance_vals = X_instance[0]
        approx_sv = fi * np.sign(instance_vals - instance_vals.mean())
        return self._build_explanation(approx_sv, instance_vals, feature_names, base_value=0.0, method="feature_importance")

    def _build_explanation(
        self,
        shap_values: np.ndarray,
        feature_values: np.ndarray,
        feature_names: List[str],
        base_value: float,
        method: str = "shap",
    ) -> Dict[str, Any]:
        """Format SHAP values into risk/protective factor lists."""
        min_len = min(len(shap_values), len(feature_values), len(feature_names))
        sv = shap_values[:min_len]
        fv = feature_values[:min_len]
        fn = feature_names[:min_len]

        shap_dict = {fn[i]: float(sv[i]) for i in range(min_len)}

        # Sort by absolute SHAP value
        sorted_items = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        risk_factors: List[PredictionFactorSchema] = []
        protective_factors: List[PredictionFactorSchema] = []

        for feat, sv_val in sorted_items[:12]:
            idx = fn.index(feat) if feat in fn else 0
            raw_val = float(fv[idx]) if idx < len(fv) else 0.0
            direction = "positive" if sv_val > 0 else "negative"
            description = _human_readable_description(feat, raw_val, sv_val)

            factor = PredictionFactorSchema(
                feature=feat,
                value=round(raw_val, 4),
                shap_value=round(sv_val, 6),
                direction=direction,
                description=description,
            )

            if sv_val > 0:
                risk_factors.append(factor)
            else:
                protective_factors.append(factor)

        return {
            "shap_values": shap_dict,
            "top_risk_factors": [f.model_dump() for f in risk_factors[:5]],
            "top_protective_factors": [f.model_dump() for f in protective_factors[:5]],
            "base_value": round(base_value, 6),
            "explanation_method": method,
        }


def _human_readable_description(feature: str, value: float, shap_value: float) -> str:
    """Generate a brief human-readable description of a feature contribution."""
    feature_descriptions = {
        "is_month_to_month": "Month-to-month contract (high churn flexibility)",
        "tenure": f"Customer tenure: {value:.0f} months",
        "monthly_charges": f"Monthly charges: ₹{value:.2f}",
        "total_charges": f"Total lifetime charges: ₹{value:.2f}",
        "service_count": f"Number of subscribed services: {value:.0f}",
        "monthly_to_total_ratio": f"Monthly-to-total charge ratio: {value:.3f}",
        "charge_per_tenure_month": f"Average monthly spend: ₹{value:.2f}",
    }
    direction_word = "increases" if shap_value > 0 else "decreases"
    base = feature_descriptions.get(feature, f"{feature}: {value:.3f}")
    return f"{base} — {direction_word} churn probability"
