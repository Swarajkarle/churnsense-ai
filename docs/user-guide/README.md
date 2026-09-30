# ChurnSense AI — User Guide

## Getting Started

### 1. Register an Account

Navigate to `/register`. Enter your:
- Full name
- Work email
- Organization name
- Password (minimum 8 characters, 1 uppercase, 1 digit)

Your organization is created automatically.

---

### 2. Upload a Dataset

Go to **Datasets** in the sidebar.

- Click **Choose CSV** and select your CSV file.
- Enter a dataset name and optional description.
- Click **Upload Dataset**.

Your data is stored on your configured server — it is not sent to external AI services.

**Supported format:** CSV files up to 50 MB.

**Tip:** Use the synthetic demo dataset for testing:
```bash
python scripts/generate_demo_data.py --rows 2000 --output ml/data/synthetic/demo.csv
```

---

### 3. Validate Your Dataset

After uploading, click the **✓** (validate) button next to your dataset.

The validation report shows:
- Row and column counts
- Missing values per column
- Duplicate rows
- Column data types
- Data quality score (0–100, heuristic)

---

### 4. Train Models

Go to **Models** in the sidebar.

1. Select your validated dataset.
2. Enter the target column name (e.g., `Churn`).
3. Choose one or more algorithms.
4. Set the test split percentage.
5. Click **Start Training**.

Training runs in the background. Refresh to see results.

**Evaluation:** F1 Score and ROC-AUC are the primary metrics because churn
datasets are class-imbalanced. Do not rely on accuracy alone.

---

### 5. Activate a Model

In the **Models** table, click **Activate** next to a trained model.

Only one model can be active at a time. The active model is used for all predictions.

---

### 6. Predict Churn

Go to **Predictions**.

**Individual Mode:**
- Enter customer features in the form.
- Click **Predict Churn**.
- View the probability, risk level, SHAP factors, and recommendations.

**Bulk Mode:**
- Upload a CSV file with customer features.
- Click **Run Bulk Prediction**.
- Results are displayed in a table.

---

### 7. View Customer Details

Go to **Customers** and click **View** next to any customer.

The Customer 360 view shows:
- Customer profile information
- Churn probability gauge
- SHAP risk factors and protective factors
- Retention recommendations
- Prediction history

---

### 8. Dashboard

The Dashboard shows:
- Total customers, at-risk count, predicted churners
- Average churn probability
- Active model metrics (Accuracy, Precision, Recall, F1, ROC-AUC)
- Monthly churn trend chart
- Risk distribution pie chart
- Churn rate by contract type

Metrics are computed from real database records. Empty states are shown if no data exists.

---

### 9. Generate Reports

Go to **Reports** and click **Generate Report**.

Reports aggregate dashboard metrics and segment analytics into a structured JSON document.
Click **Export JSON** to download.

---

## Important Notes

### About Predictions
Churn predictions are probabilistic estimates based on historical patterns in training data.
They are not deterministic facts. A customer predicted to churn may not churn, and vice versa.

### About Explanations
SHAP explanations describe the model's behavior on a given input.
They are not guaranteed causal explanations of why a customer will or will not churn.

### About Recommendations
Retention recommendations are data-informed suggestions. They do not guarantee
that a customer will stay. Use them as starting points for your retention strategy.

### About Privacy
- Customer data is stored on your own database.
- Data is not sent to external AI services.
- Datasets can be deleted at any time.
- Use data minimization — remove unnecessary PII before uploading where possible.
