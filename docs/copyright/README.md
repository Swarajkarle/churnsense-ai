# ChurnSense AI — Copyright Preparation Documentation

**Project Title:** AI-Based Customer Churn Prediction and Retention Recommendation System  
**Software Product Name:** ChurnSense AI  
**Author:** Swaraj Karle  
**Institution:** [Your College Name]  
**Academic Year:** 2025–2026  
**Date of Creation:** September 2026

---

> **IMPORTANT DISCLAIMER:**
>
> The purpose of this documentation is to support the copyright registration of an
> original software implementation. The following statements are factually accurate:
>
> - The general concept of customer churn prediction is NOT claimed as proprietary.
> - The underlying mathematical algorithms (logistic regression, decision trees,
>   random forests, gradient boosting, XGBoost, SHAP) are NOT claimed as proprietary.
>   They are well-established techniques in the public domain or open-source libraries.
> - The open-source libraries used (scikit-learn, XGBoost, SHAP, FastAPI, Next.js,
>   React, etc.) are NOT claimed as proprietary.
>
> The software implementation, source code, documentation, UI elements,
> original feature engineering pipeline, explainability integration, recommendation
> engine logic, database schema, API design, and supporting documentation
> created by the authors are intended to constitute the copyrightable portions
> of the work, subject to applicable law and the determination of the Copyright Office.
>
> This project does not fabricate research results, does not claim guaranteed
> copyright registration, and does not claim ownership of any public dataset.

---

## 1. Abstract

ChurnSense AI is an original full-stack web-based software platform designed to help
organizations identify customers who are likely to churn (discontinue their subscription
or service), understand the contributing factors, and take data-driven retention actions.

The platform integrates a machine-learning prediction pipeline, a SHAP-based explainability
layer, an original rule-based recommendation engine, a normalized relational database,
a REST API, and a modern web dashboard — all developed as a single, cohesive software product.

---

## 2. Problem Statement

Customer churn — the loss of a client or subscriber — is one of the most significant
business challenges in subscription-based and service-oriented industries. Acquiring
a new customer is typically 5–7× more expensive than retaining an existing one.

Despite this, most organizations lack actionable, integrated tools to:
1. Predict *which* customers are likely to leave before they do.
2. Understand *why* those customers are at risk (interpretable predictions).
3. Take *specific, data-driven, and explainable* retention actions.

ChurnSense AI addresses all three gaps through an integrated, original software implementation.

---

## 3. Proposed System — ChurnSense AI

ChurnSense AI is a web-based AI platform with the following original components:

| Component | Description |
|---|---|
| **Frontend** | Next.js 14 + TypeScript SaaS dashboard with original design system |
| **Backend** | FastAPI REST API with JWT auth, Pydantic validation, SQLAlchemy ORM |
| **ML Pipeline** | Multi-model training, stratified evaluation, artifact persistence |
| **Feature Engineering** | Documented, domain-driven feature creation with a feature dictionary |
| **Explainability** | SHAP-based per-prediction factor attribution |
| **Recommendation Engine** | Original rule-based retention action generator |
| **Database** | Normalized PostgreSQL schema (14 tables) with UUID keys and indexes |
| **Testing** | Unit, API, and ML pipeline tests |
| **Documentation** | Architecture, API, copyright, user guide, feature dictionary |

---

## 4. Objectives

1. Build a complete, end-to-end churn prediction platform (not a notebook).
2. Train and compare multiple ML models using documented evaluation criteria.
3. Produce per-prediction SHAP explanations interpretable by non-technical users.
4. Generate explainable, prioritized retention recommendations.
5. Store all predictions, models, explanations, and recommendations in a structured database.
6. Provide an executive analytics dashboard with real computed metrics.
7. Implement secure authentication and role-based access control.
8. Build the system as a reusable platform (not hardcoded to one dataset).
9. Prepare comprehensive copyright documentation.

---

## 5. Scope

**In Scope:**
- CSV-based dataset upload, validation, and preprocessing
- Multi-model ML training and evaluation (5 algorithms)
- Individual and bulk churn prediction
- SHAP-based explainability
- Original rule-based recommendation engine
- Customer 360 profile view
- Executive analytics dashboard
- Report generation and export
- JWT authentication and role-based access
- PostgreSQL database with full schema
- Synthetic demo dataset generator
- Unit, API, and ML pipeline tests
- Deployment configuration for Vercel + Render + Supabase

**Out of Scope:**
- Real-time streaming data ingestion
- Mobile native app
- Reinforcement-learning-based recommendation (designed as future extension)
- Guaranteed churn prevention (predictions are probabilistic estimates)

---

## 6. System Architecture

```
User Browser
     ↓
Next.js 14 Frontend (TypeScript + Tailwind + Recharts)
     ↓
FastAPI REST API (Python 3.11)
     ↓
 ┌──────────────────────────────────────────┐
 │  Auth Service (JWT + bcrypt)             │
 │  Dataset Service (CSV validation)        │
 │  Training Service (background tasks)     │
 │  Prediction Service (model + SHAP)       │
 │  Recommendation Engine (rule-based)      │
 │  Analytics Service (computed from DB)    │
 │  Report Service (aggregated output)      │
 └──────────────────────────────────────────┘
     ↓
PostgreSQL (Supabase) — 14 tables
     ↓
ML Artifact Store (Joblib files on disk)
```

---

## 7. Module Descriptions

### 7.1 Authentication Module
- JWT-based access and refresh tokens
- bcrypt password hashing
- Role-based access: admin, analyst, viewer
- Per-organization data isolation

### 7.2 Dataset Module
- CSV upload with size and format validation
- Column profiling (type detection, null analysis, uniqueness)
- Heuristic data quality score computation
- Preprocessing configuration (not silently applied)

### 7.3 Feature Engineering Module
- Tenure group classification (new/developing/established/loyal)
- Monthly-to-total charge ratio
- Service count aggregation
- Contract type binary flags
- Charge-per-tenure-month
- Feature dictionary with documented rationale for each feature

### 7.4 Preprocessing Pipeline
- sklearn ColumnTransformer with median imputation, OneHot encoding, StandardScaler
- Fitted at training time, serialized, and loaded identically at inference (no data leakage)

### 7.5 Model Training Module
- 5 algorithms: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost
- Stratified train/test split
- Evaluation: Accuracy, Precision, Recall, F1 Score, ROC-AUC, Confusion Matrix
- Feature importance extraction
- Background task execution

### 7.6 Prediction Module
- Individual and bulk prediction
- Risk level classification (low / medium / high / critical) — heuristic thresholds
- Prediction stored with input features and model reference

### 7.7 Explainability Module (SHAP)
- TreeExplainer for tree-based models
- LinearExplainer for logistic regression
- KernelExplainer as fallback
- Human-readable factor descriptions
- Clear disclaimer: explanations describe model behavior, not causal guarantees

### 7.8 Recommendation Engine (Original)
- Rule-based engine with 6 rule categories
- Rules: contract type, tenure phase, monthly charges, service engagement, risk-level outreach, SHAP-driven factors
- Each recommendation includes a rationale field
- Clear disclaimer: recommendations do not guarantee churn prevention
- Designed for future ML/RL replacement

### 7.9 Analytics Module
- Overview KPIs computed from real database records
- Monthly churn trend from prediction history
- Segment analysis by contract type and payment method
- Risk distribution from predictions

### 7.10 Report Module
- Aggregated JSON reports combining analytics + model + segment data
- Export to JSON

---

## 8. Functional Requirements

| FR-ID | Requirement |
|---|---|
| FR-01 | System shall allow user registration with email, password, and organization name |
| FR-02 | System shall authenticate users via JWT tokens |
| FR-03 | System shall allow CSV dataset upload |
| FR-04 | System shall validate uploaded datasets and produce a quality report |
| FR-05 | System shall allow training of multiple ML models on an uploaded dataset |
| FR-06 | System shall evaluate trained models using F1, ROC-AUC, Precision, Recall, Accuracy |
| FR-07 | System shall allow activation of one model as the prediction model |
| FR-08 | System shall predict churn probability for individual customers |
| FR-09 | System shall predict churn for multiple customers from a CSV file |
| FR-10 | System shall classify each prediction into a risk level |
| FR-11 | System shall generate SHAP-based explanations for each prediction |
| FR-12 | System shall generate prioritized retention recommendations for each prediction |
| FR-13 | System shall display an executive analytics dashboard with real computed metrics |
| FR-14 | System shall maintain prediction history |
| FR-15 | System shall allow report generation and JSON export |
| FR-16 | System shall provide a Customer 360 profile view |
| FR-17 | System shall allow dataset deletion with file cleanup |
| FR-18 | System shall log audit events |

---

## 9. Non-Functional Requirements

| NFR-ID | Requirement |
|---|---|
| NFR-01 | API response time < 2s for prediction (excluding training) |
| NFR-02 | Passwords stored only as bcrypt hashes |
| NFR-03 | JWT tokens expire in 60 minutes by default |
| NFR-04 | File upload limited to 50 MB |
| NFR-05 | Bulk prediction limited to 10,000 rows |
| NFR-06 | All secrets loaded from environment variables |
| NFR-07 | CORS configured to restrict origins |
| NFR-08 | SQL injection prevented via SQLAlchemy ORM |
| NFR-09 | Frontend supports mobile-responsive layout |
| NFR-10 | Empty states displayed when no data is available |
| NFR-11 | No customer data sent to external AI services |

---

## 10. Technology Stack

See [ATTRIBUTIONS.md](../../ATTRIBUTIONS.md) for full library list and licenses.

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript 5, Tailwind CSS 3, shadcn/ui, Recharts |
| State | TanStack Query v5, Zustand v4 |
| Backend | Python 3.11, FastAPI 0.111, Pydantic v2, SQLAlchemy 2, Alembic |
| Auth | python-jose (JWT), passlib + bcrypt |
| ML | scikit-learn, XGBoost, SHAP, Pandas, NumPy, Joblib |
| Database | PostgreSQL 15 via Supabase |
| Deployment | Vercel (frontend), Render/Railway (backend), Supabase (DB) |

---

## 11. Database Design

See [ER Diagram](../diagrams/er_diagram.md) for the entity-relationship diagram.

14 tables: users, organizations, datasets, dataset_columns, customers,
customer_features, models, model_metrics, predictions, prediction_explanations,
recommendations, training_runs, reports, audit_logs.

All primary keys are UUIDs. All tables include created_at timestamps.
Foreign keys use appropriate cascading behavior.

---

## 12. ML Methodology

### Model Selection Rationale
Five algorithms were implemented to allow empirical comparison:

1. **Logistic Regression** — Fast, interpretable baseline; good for linear relationships
2. **Decision Tree** — Non-linear, rule-based; highly interpretable but prone to overfitting
3. **Random Forest** — Ensemble of trees; robust to overfitting; provides feature importances
4. **Gradient Boosting** — Sequential boosting; high performance on tabular data
5. **XGBoost** — Optimized gradient boosting; often strongest performer on structured data

### Evaluation Strategy
- Stratified train/test split prevents class imbalance issues in evaluation
- Accuracy is NOT the sole metric due to class imbalance in churn datasets
- **F1 Score and ROC-AUC are the primary evaluation metrics**
- Confusion matrix is stored for each model

### Prediction Threshold
The default threshold of 0.5 is a starting point. Users can adjust it.
Threshold choice involves a precision/recall tradeoff appropriate to business context.
No single threshold is claimed to be universally correct.

---

## 13. Explainable AI Methodology

ChurnSense AI uses SHAP (SHapley Additive exPlanations) to explain individual predictions.

**How it works:**
- For tree-based models: TreeExplainer (efficient)
- For logistic regression: LinearExplainer
- Fallback: KernelExplainer or feature-importance approximation

**Disclaimer displayed to users:**
> "These explanations describe the model's behavior on this input.
>  They are not guaranteed causal explanations of why the customer
>  will or will not churn."

SHAP values show each feature's contribution to the deviation from the base prediction.
Positive SHAP values increase churn probability; negative values decrease it.

---

## 14. Recommendation Engine Documentation

The retention recommendation engine is an original rule-based system. It is NOT
a copy of any existing recommendation system.

**Design:**
- 6 rule categories: contract_upgrade, loyalty_incentive, pricing_review,
  personalized_support, service_resolution, success_outreach
- Inputs: churn probability, risk level, customer features, SHAP top factors
- Each recommendation includes a `rationale` field explaining why it was generated
- Deduplication by category (highest priority per category shown)
- Maximum 6 recommendations per prediction

**Important:**
> "These recommendations are suggested actions informed by model predictions.
>  They do not guarantee that a customer will or will not churn."

**Extensibility:** The engine implements a `generate()` interface that a future
ML or reinforcement-learning module can replace without changing the API contract.

---

## 15. Testing Documentation

| Test Category | File | Coverage |
|---|---|---|
| Auth API | `tests/api/test_auth.py` | Register, login, wrong password, invalid token, unauthorized access |
| ML Pipeline | `tests/unit/test_ml_pipeline.py` | Feature engineering, preprocessing, model training, recommendations |
| Data Validation | `tests/unit/test_ml_pipeline.py` | Missing columns, empty dataset, preprocessing consistency |

Run tests: `cd backend && pytest tests/ -v --cov=app`

---

## 16. Originality Statement

This software implementation — ChurnSense AI — is an original creative work.
Specifically, the following elements were created by the author and are original:

1. **Application Architecture**: The specific layered design with service-oriented
   backend, separate ML pipeline, and frontend application structure.

2. **Source Code**: All Python, TypeScript, and configuration files in this repository,
   written by the author with AI tools used as development assistants.

3. **UI/UX Design**: The original dark-theme glassmorphism design system, including
   color palette, component styles, animation system, and page layouts.

4. **Feature Engineering Pipeline**: The specific combination and implementation of
   engineered features, documented in the feature dictionary.

5. **Explainability Integration**: The specific way SHAP is integrated with
   fallback handling and human-readable description generation.

6. **Recommendation Engine**: The rule-based engine with its specific rule set,
   prioritization logic, rationale generation, and extensibility interface.

7. **Database Schema**: The specific 14-table normalized schema with UUID keys,
   relationships, and indexing strategy.

8. **API Structure**: The specific REST endpoint design and organization.

9. **Documentation**: All documentation files in this repository.

**What is NOT claimed as original:**
- The general concept of churn prediction
- The mathematical algorithms (logistic regression, random forests, etc.)
- The open-source libraries used as dependencies
- The synthetic dataset schema (inspired by publicly described subscription business attributes)

---

## 17. Third-Party Attribution

See [ATTRIBUTIONS.md](../../ATTRIBUTIONS.md) for the complete list of third-party
libraries, fonts, icons, and resources with their respective licenses.

---

## 18. Development History

This project was developed systematically between July 2026 and September 2026
following an eight-phase development methodology:

1. Architecture & project scaffold
2. Database schema & backend foundation
3. ML pipeline (preprocessing, feature engineering, training)
4. Prediction, explainability, and recommendation engine
5. Frontend (design system, pages, charts)
6. Integration
7. Testing
8. Documentation

Development was performed by Swaraj Karle with AI tools used as code-writing assistants.
All code was reviewed, integrated, and understood by the author.

---

*End of Copyright Documentation*
