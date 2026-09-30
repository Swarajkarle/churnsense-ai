# ChurnSense AI — API Reference

## Base URL
```
http://localhost:8000/api/v1
```

Interactive docs available at: `http://localhost:8000/docs`

---

## Authentication

All protected endpoints require a JWT Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Auth

#### `POST /auth/register`
Register a new user and organization.

**Request:**
```json
{
  "email": "you@company.com",
  "password": "SecurePass1",
  "full_name": "Swaraj Karle",
  "organization_name": "Acme Corp"
}
```
**Response 201:**
```json
{
  "id": "uuid",
  "email": "you@company.com",
  "full_name": "Swaraj Karle",
  "role": "admin",
  "organization_id": "uuid"
}
```

#### `POST /auth/login`
Login and receive JWT tokens.

**Request:**
```json
{ "email": "you@company.com", "password": "SecurePass1" }
```
**Response 200:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### `GET /auth/me` 🔒
Get the currently authenticated user.

#### `PUT /auth/me` 🔒
Update user profile (full_name only).

---

### Datasets

#### `POST /datasets/upload` 🔒
Upload a CSV dataset.

**Content-Type:** `multipart/form-data`  
**Form fields:** `file` (CSV), `name` (string), `description` (optional string)  
**Response 201:** Dataset record

#### `GET /datasets` 🔒
List all datasets for the organization.

#### `GET /datasets/{id}` 🔒
Get dataset details including column profiles.

#### `POST /datasets/{id}/validate` 🔒
Trigger dataset validation and quality scoring.

**Response 200:** Validation report with quality_score, column profiles, issues list.

#### `POST /datasets/{id}/preprocess` 🔒
Configure preprocessing for a dataset.

**Request:**
```json
{
  "categorical_cols": ["Contract", "PaymentMethod"],
  "numeric_cols": ["tenure", "MonthlyCharges"],
  "drop_cols": ["customerID"]
}
```

#### `DELETE /datasets/{id}` 🔒
Delete a dataset and its file.

---

### Models

#### `POST /models/train` 🔒
Start model training.

**Request:**
```json
{
  "dataset_id": "uuid",
  "target_column": "Churn",
  "algorithms": ["random_forest", "xgboost"],
  "test_split": 0.2,
  "random_state": 42
}
```
**Response 202:** `{ "run_id": "uuid", "status": "queued" }`

Supported algorithms: `logistic_regression`, `decision_tree`, `random_forest`, `gradient_boosting`, `xgboost`

#### `GET /models` 🔒
List all models with their metrics.

#### `GET /models/{id}` 🔒
Get model details and full metrics.

#### `POST /models/{id}/activate` 🔒
Set this model as the active prediction model.

#### `DELETE /models/{id}` 🔒
Delete a model record and its artifacts.

---

### Predictions

#### `POST /predictions/customer` 🔒
Run individual churn prediction.

**Request:**
```json
{
  "features": {
    "tenure": 12,
    "Contract": "Month-to-month",
    "MonthlyCharges": 85.5,
    "TotalCharges": 1026.0,
    "InternetService": "Fiber optic"
  },
  "threshold": 0.5,
  "customer_id": "optional-uuid"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "churn_probability": 0.742,
  "churn_prediction": true,
  "risk_level": "high",
  "prediction_threshold": 0.5,
  "explanation": {
    "top_risk_factors": [...],
    "top_protective_factors": [...]
  },
  "recommendations": [...]
}
```

#### `POST /predictions/bulk` 🔒
Run bulk prediction from CSV.

**Content-Type:** `multipart/form-data`  
**Form fields:** `file` (CSV), `threshold` (float, optional), `model_id` (optional)  
**Response 200:** Array of prediction objects (max 10,000 rows)

#### `GET /predictions` 🔒
List prediction history. Query params: `page`, `page_size`.

#### `GET /predictions/{id}` 🔒
Get a single prediction with explanation and recommendations.

---

### Customers

#### `GET /customers` 🔒
List customers. Query params: `page`, `page_size`, `search`, `risk_level`.

#### `GET /customers/{id}` 🔒
Get customer 360 view with latest prediction, explanation, recommendations, history.

#### `GET /customers/{id}/explanation` 🔒
Get the SHAP explanation for the customer's latest prediction.

#### `GET /customers/{id}/recommendations` 🔒
Get retention recommendations for the customer's latest prediction.

---

### Analytics

#### `GET /analytics/overview` 🔒
Get dashboard KPIs.

**Response 200:**
```json
{
  "total_customers": 1247,
  "customers_at_risk": 312,
  "predicted_churners": 178,
  "average_churn_probability": 0.284,
  "active_model_accuracy": 0.812,
  "active_model_f1": 0.741,
  "active_model_roc_auc": 0.856,
  "active_model_name": "Random Forest v1.0.0"
}
```

#### `GET /analytics/churn` 🔒
Get monthly churn trend data (last 12 months).

#### `GET /analytics/segments` 🔒
Get churn breakdown by contract type, payment method, and risk distribution.

---

### Reports

#### `POST /reports/generate` 🔒
Generate a report.

**Request:**
```json
{
  "title": "Q3 2026 Churn Report",
  "report_type": "overview",
  "model_id": "optional-uuid",
  "dataset_id": "optional-uuid"
}
```

#### `GET /reports` 🔒
List all reports.

#### `GET /reports/{id}` 🔒
Get a single report with full content.

---

## Error Responses

| Status | Meaning |
|---|---|
| 400 | Bad request (validation error, invalid file format) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (role restriction) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email) |
| 422 | Unprocessable entity (schema validation failure) |
| 500 | Internal server error |

All errors return: `{ "detail": "Human-readable error message" }`

---

## Health Check

`GET /health` — Returns `{ "status": "healthy", "version": "1.0.0" }` (no auth required)
