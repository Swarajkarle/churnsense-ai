"""
ChurnSense AI — Feature Engineering Pipeline

This module defines and documents engineered features that are derived from
raw customer attributes. Every engineered feature includes a rationale
explaining why it exists and what signal it encodes.

Design: All transformations are deterministic and reproducible.
        No feature is blindly created — each is justified below.
"""

from typing import List

import numpy as np
import pandas as pd


# ── Feature Dictionary ──────────────────────────────────────────────────────

FEATURE_DICTIONARY = {
    "tenure_group": {
        "source": ["tenure"],
        "description": "Categorical grouping of tenure into 4 buckets (0-12, 13-24, 25-48, 49+)",
        "rationale": (
            "Raw tenure is continuous but customer behavior often changes in discrete "
            "phases: new customers (0-12 months) are at highest risk, mid-tenure customers "
            "have lower churn rates, while long-tenure customers tend to be more loyal."
        ),
        "encoding": "ordinal",
    },
    "monthly_to_total_ratio": {
        "source": ["monthly_charges", "total_charges"],
        "description": "Ratio of monthly charges to total charges",
        "rationale": (
            "A high ratio indicates the customer has only recently started (high monthly "
            "relative to total spent), which correlates with higher churn risk. "
            "Customers with more total investment are less likely to leave."
        ),
        "encoding": "numeric",
    },
    "service_count": {
        "source": ["services"],
        "description": "Count of subscribed services",
        "rationale": (
            "Customers subscribed to more services have higher switching costs and "
            "engagement depth, both of which reduce churn probability."
        ),
        "encoding": "numeric",
    },
    "is_month_to_month": {
        "source": ["contract_type"],
        "description": "Binary flag: 1 if contract is month-to-month",
        "rationale": (
            "Month-to-month contracts have no lock-in period, making it trivially easy "
            "to churn. This is one of the strongest single churn signals in telecom data."
        ),
        "encoding": "binary",
    },
    "has_tech_support": {
        "source": ["services"],
        "description": "Binary flag: 1 if TechSupport is in subscribed services",
        "rationale": (
            "Tech support subscription reduces frustration-driven churn from unresolved "
            "technical issues, which are a primary churn driver."
        ),
        "encoding": "binary",
    },
    "charge_per_tenure_month": {
        "source": ["total_charges", "tenure"],
        "description": "Average monthly spend over full tenure",
        "rationale": (
            "Derived from total_charges / max(tenure, 1). Captures whether a customer's "
            "spending has been stable, growing, or declining — a proxy for satisfaction."
        ),
        "encoding": "numeric",
    },
    "is_senior_citizen": {
        "source": ["senior_citizen"],
        "description": "Numeric encoding of senior citizen flag",
        "rationale": (
            "Senior citizens show different churn patterns due to different service needs "
            "and comfort with technology. Including this can improve segment-level predictions."
        ),
        "encoding": "binary",
    },
}


class ChurnFeatureEngineer:
    """
    Applies domain-driven feature engineering to a customer DataFrame.

    Only features supported by the dataset are created.
    Missing source columns are handled gracefully.
    """

    def fit(self, df: pd.DataFrame) -> "ChurnFeatureEngineer":
        """Compute any fit-time statistics (currently none required)."""
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all feature engineering transformations."""
        df = df.copy()
        df = self._add_tenure_group(df)
        df = self._add_monthly_to_total_ratio(df)
        df = self._add_service_count(df)
        df = self._add_contract_flags(df)
        df = self._add_charge_per_tenure(df)
        return df

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)

    # ── Individual feature engineering methods ───────────────────────────────

    def _add_tenure_group(self, df: pd.DataFrame) -> pd.DataFrame:
        """Segment customers by tenure phase."""
        if "tenure" not in df.columns:
            return df

        def _group(t):
            try:
                t = float(t)
            except (TypeError, ValueError):
                return "unknown"
            if t <= 12:
                return "new"        # 0-12 months — highest churn risk
            elif t <= 24:
                return "developing"  # 13-24 months
            elif t <= 48:
                return "established"  # 25-48 months
            else:
                return "loyal"      # 49+ months — lowest churn risk

        df["tenure_group"] = df["tenure"].apply(_group)
        return df

    def _add_monthly_to_total_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ratio of current monthly charges to lifetime total charges."""
        if "monthly_charges" not in df.columns or "total_charges" not in df.columns:
            return df
        # Coerce total_charges to numeric (raw data sometimes has spaces)
        monthly = pd.to_numeric(df["monthly_charges"], errors="coerce")
        total = pd.to_numeric(df["total_charges"], errors="coerce")
        df["monthly_to_total_ratio"] = monthly / total.replace(0, np.nan)
        df["monthly_to_total_ratio"] = df["monthly_to_total_ratio"].fillna(1.0)
        return df

    def _add_service_count(self, df: pd.DataFrame) -> pd.DataFrame:
        """Count binary yes/no service columns."""
        service_cols = [
            c for c in df.columns
            if df[c].dtype == object
            and df[c].str.lower().isin(["yes", "no"]).any()
            and c not in (
                "gender", "partner", "dependents", "phone_service",
                "churn", "senior_citizen",
            )
        ]
        if service_cols:
            df["service_count"] = df[service_cols].apply(
                lambda row: (row.str.lower() == "yes").sum(), axis=1
            )
        else:
            df["service_count"] = 0
        return df

    def _add_contract_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Binary flags for contract type."""
        if "contract" in df.columns:
            df["is_month_to_month"] = (df["contract"].str.lower() == "month-to-month").astype(int)
        elif "contract_type" in df.columns:
            df["is_month_to_month"] = (df["contract_type"].str.lower() == "month-to-month").astype(int)
        return df

    def _add_charge_per_tenure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Average charge per month of tenure."""
        if "total_charges" not in df.columns or "tenure" not in df.columns:
            return df
        total = pd.to_numeric(df["total_charges"], errors="coerce")
        tenure = pd.to_numeric(df["tenure"], errors="coerce").replace(0, 1)
        df["charge_per_tenure_month"] = total / tenure
        df["charge_per_tenure_month"] = df["charge_per_tenure_month"].fillna(0)
        return df
