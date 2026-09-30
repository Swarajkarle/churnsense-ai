# ChurnSense AI — Machine Learning Data Directory

This directory contains dataset resources used for training, benchmarking, and demonstrating the **ChurnSense AI** customer churn prediction models.

---

## 1. Synthetic Demonstration Data (`synthetic/`)

- **Files:**
  - `ml/data/synthetic/demo.csv` (1,000 synthetic records)
  - `ml/data/synthetic/demo_customers.csv` (1,000 synthetic records)
- **Origin & Nature:**
  - These datasets are **100% synthetic and programmatically generated** using `scripts/generate_demo_data.py`.
  - They do **NOT** contain, represent, or derive from real customer or corporate records.
  - The statistical generation uses randomized parametric distributions (normal, beta, and binomial distributions) with an artificial logistic churn ground truth function yielding an approximate 26–28% churn rate.
- **Redistribution:**
  - Fully safe for open-source distribution and offline testing.

To generate a new synthetic demonstration dataset of arbitrary size, execute:
```bash
python scripts/generate_demo_data.py --rows 2500 --output ml/data/synthetic/demo_custom.csv
```

---

## 2. Benchmark & Raw Datasets (`raw/`)

- By design, raw third-party datasets or proprietary customer data placed in `raw/` are excluded from Git via `.gitignore` to protect privacy and respect third-party licensing.
- **Recommended Public Benchmark:**
  - **IBM Telco Customer Churn Dataset** (available publicly on Kaggle):
    Users wishing to benchmark the pipeline against public tabular datasets can download `WA_Fn-UseC_-Telco-Customer-Churn.csv` from Kaggle and place it in `ml/data/raw/` or upload it through the web dashboard.
- **Data Privacy Policy:**
  - Never commit real customer PII (names, credit cards, real phone numbers, or corporate emails) to version control.
