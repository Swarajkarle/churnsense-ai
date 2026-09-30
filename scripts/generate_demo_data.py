#!/usr/bin/env python3
"""
ChurnSense AI — Synthetic Demo Dataset Generator

Generates a clearly labeled synthetic customer dataset for demonstration.

IMPORTANT:
  - This data is SYNTHETIC and does NOT represent real customers.
  - It was generated programmatically using statistical distributions.
  - It is NOT derived from or representative of any real organization.
  - It is provided solely to allow the system to run without private data.

Usage:
    python scripts/generate_demo_data.py --rows 1000 --output ml/data/synthetic/demo_customers.csv

Dataset fields are inspired by publicly described subscription business attributes
and are not copied from any proprietary dataset.
"""

import argparse
import random
from datetime import datetime

import numpy as np
import pandas as pd


def generate_synthetic_churn_dataset(n_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic customer churn dataset.

    Churn probability is calculated from a logistic function over
    synthetic features, producing a realistic (but artificial) churn rate
    of approximately 26-30%.

    Returns:
        DataFrame with labeled synthetic customer records
    """
    np.random.seed(seed)
    random.seed(seed)

    # ── Basic demographics ─────────────────────────────────────────────────
    gender = np.random.choice(["Male", "Female"], n_rows, p=[0.50, 0.50])
    senior_citizen = np.random.choice([0, 1], n_rows, p=[0.84, 0.16])
    partner = np.random.choice(["Yes", "No"], n_rows, p=[0.48, 0.52])
    dependents = np.random.choice(["Yes", "No"], n_rows, p=[0.30, 0.70])

    # ── Service subscription ───────────────────────────────────────────────
    tenure = np.random.randint(1, 73, n_rows)
    phone_service = np.random.choice(["Yes", "No"], n_rows, p=[0.90, 0.10])
    multiple_lines = np.where(
        phone_service == "No", "No phone service",
        np.random.choice(["Yes", "No"], n_rows, p=[0.42, 0.58])
    )
    internet_service = np.random.choice(
        ["DSL", "Fiber optic", "No"], n_rows, p=[0.34, 0.44, 0.22]
    )

    def internet_addon(internet_svc, yes_prob=0.30):
        return np.where(
            internet_svc == "No", "No internet service",
            np.random.choice(["Yes", "No"], n_rows, p=[yes_prob, 1 - yes_prob])
        )

    online_security = internet_addon(internet_service, 0.29)
    online_backup = internet_addon(internet_service, 0.34)
    device_protection = internet_addon(internet_service, 0.34)
    tech_support = internet_addon(internet_service, 0.29)
    streaming_tv = internet_addon(internet_service, 0.38)
    streaming_movies = internet_addon(internet_service, 0.39)

    # ── Contract & billing ─────────────────────────────────────────────────
    contract = np.random.choice(
        ["Month-to-month", "One year", "Two year"], n_rows, p=[0.55, 0.21, 0.24]
    )
    paperless_billing = np.random.choice(["Yes", "No"], n_rows, p=[0.59, 0.41])
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n_rows, p=[0.34, 0.23, 0.22, 0.21]
    )

    # ── Charges ───────────────────────────────────────────────────────────
    base_monthly = np.where(internet_service == "No", 20.0, 50.0)
    fiber_premium = np.where(internet_service == "Fiber optic", 20.0, 0.0)
    addon_premium = (
        (online_security == "Yes").astype(float) * 7 +
        (online_backup == "Yes").astype(float) * 7 +
        (device_protection == "Yes").astype(float) * 7 +
        (tech_support == "Yes").astype(float) * 7 +
        (streaming_tv == "Yes").astype(float) * 7 +
        (streaming_movies == "Yes").astype(float) * 7 +
        (multiple_lines == "Yes").astype(float) * 10
    )
    monthly_charges = base_monthly + fiber_premium + addon_premium + np.random.normal(0, 3, n_rows)
    monthly_charges = np.clip(monthly_charges, 18.0, 120.0).round(2)
    total_charges = (monthly_charges * tenure + np.random.normal(0, 50, n_rows)).round(2)
    total_charges = np.clip(total_charges, 18.0, None)

    # ── Synthetic churn probability (logistic function) ────────────────────
    # These coefficients are synthetic — they are not fitted to real data.
    logit = (
        -2.5
        + 0.02 * (monthly_charges - 65)
        - 0.03 * tenure
        + 1.2 * (contract == "Month-to-month")
        + 0.4 * (internet_service == "Fiber optic")
        + 0.5 * (payment_method == "Electronic check")
        - 0.5 * (online_security == "Yes")
        - 0.4 * (tech_support == "Yes")
        + 0.3 * senior_citizen
        + np.random.normal(0, 0.5, n_rows)
    )
    churn_prob = 1 / (1 + np.exp(-logit))
    churn = np.where(np.random.uniform(0, 1, n_rows) < churn_prob, "Yes", "No")

    customer_ids = [f"SYN-{i:05d}" for i in range(1, n_rows + 1)]

    df = pd.DataFrame({
        "customerID": customer_ids,
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "Churn": churn,
    })

    print(f"✅ Generated {n_rows} synthetic customer records")
    print(f"   Churn rate: {(churn == 'Yes').mean():.1%}")
    print(f"   ⚠️  This data is SYNTHETIC — not real customer data")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic ChurnSense demo data")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to generate")
    parser.add_argument("--output", type=str, default="ml/data/synthetic/demo_customers.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    df = generate_synthetic_churn_dataset(n_rows=args.rows, seed=args.seed)
    df.to_csv(args.output, index=False)
    print(f"   Saved to: {args.output}")
