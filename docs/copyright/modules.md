# System Modules Documentation

ChurnSense AI is constructed from modular subsystems designed with loose coupling and high cohesion.

---

## 1. Authentication & Identity Module (`backend/app/api/v1/auth.py`, `backend/app/core/security.py`)
- **Password Security:** Hashes passwords using bcrypt with a high work factor.
- **Token Management:** Issues signed HS256 JSON Web Tokens (JWT) with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`).
- **Authorization:** Enforces role-based permissions (`admin`, `analyst`, `viewer`) via FastAPI dependencies.
- **Multi-Tenancy:** Associates users with unique `organization_id` keys to isolate enterprise tenant data.

## 2. Dataset Ingestion & Validation Module (`backend/app/services/dataset_service.py`)
- **File Ingestion:** Validates incoming file extensions, MIME types, and file size limits (50 MB default).
- **Schema Profiling:** Analyzes columns for null counts, uniqueness, distribution statistics, and data types.
- **Quality Score Generator:** Computes heuristic data hygiene scores based on missing values, duplicate records, and target balance.
- **Persistence:** Stores structured metadata in `datasets` and `dataset_columns` tables.

## 3. Feature Engineering Pipeline (`backend/app/ml/features/feature_engineer.py`)
- **Domain Transformation:** Derives predictive domain signals:
  - `tenure_group`: Categorizes customer lifecycle into New, Developing, Established, or Loyal cohorts.
  - `monthly_to_total_ratio`: Computes pricing stability relative to overall spend.
  - `service_count`: Aggregates active digital and phone services.
  - `charges_per_tenure_month`: Detects payment acceleration and billing inflation.
- **Imputation Handling:** Handles missing fields with robust fallback mechanisms.

## 4. Leakage-Free Preprocessing Pipeline (`backend/app/ml/preprocessing/preprocessor.py`)
- **Transformer Construction:** Encapsulates Scikit-learn `ColumnTransformer` with `SimpleImputer` (median), `OneHotEncoder(handle_unknown='ignore')`, and `StandardScaler`.
- **Fit vs. Transform:** Fits strictly on training split; serializes preprocessing artifacts alongside model weights via Joblib to ensure identical inference representation.

## 5. Model Training & Evaluation Engine (`backend/app/ml/training/trainer.py`, `backend/app/services/training_service.py`)
- **Supported Estimators:**
  1. `LogisticRegression` (L2 regularized)
  2. `DecisionTreeClassifier` (bounded depth)
  3. `RandomForestClassifier` (100 estimators, parallelized)
  4. `GradientBoostingClassifier`
  5. `XGBClassifier` (optimized gradient boosting)
- **Evaluation Metrics:** Evaluates Accuracy, Precision, Recall, F1 Score, ROC-AUC, and full Confusion Matrices.
- **Model Registry:** Records runs in `training_runs` and indexes artifacts in `models` and `model_metrics`.

## 6. Prediction Service (`backend/app/services/prediction_service.py`)
- **Inference Modes:** Supports single-record interactive scoring and high-volume batch CSV inference.
- **Risk Stratification:** Classifies probability into actionable risk tiers (`low` < 0.25, `medium` 0.25–0.50, `high` 0.50–0.75, `critical` ≥ 0.75).
- **Database Tracking:** Every prediction is persisted with full input snapshots and active model links.

## 7. Explainability Service (`backend/app/ml/evaluation/explainer.py`)
- **SHAP Integration:** Applies SHAP `TreeExplainer` for tree ensembles and `LinearExplainer` for linear models.
- **Factor Attribution:** Identifies top risk-increasing and protective factors with exact feature values and attribution weights.
- **Human-Readable Explanations:** Formats mathematical SHAP values into clear, plain-language bullet points.

## 8. Retention Recommendation Engine (`backend/app/services/recommendation_engine.py`)
- **Prescriptive Decision Rules:** Maps risk tiers, tenure phases, contract structures, financial metrics, and SHAP factors into prioritized retention strategies.
- **Rule Categories:** Contract upgrades, loyalty incentives, pricing reviews, proactive support, service onboarding, and executive outreach.
- **Rationale Generation:** Includes explicit reasons justifying each recommended intervention.

## 9. Executive Analytics & Reporting Module (`backend/app/services/analytics_service.py`, `report_service.py`)
- **KPI Aggregation:** Computes live platform metrics (overall churn rate, total customers evaluated, active models).
- **Segment Breakdown:** Aggregates risk trends across contract types and payment methods.
- **Export Engine:** Compiles comprehensive audit reports into structured JSON documents.

## 10. Frontend Presentation Layer (`frontend/`)
- **Responsive Dashboard:** Built with Next.js 14 App Router, TypeScript, and Tailwind CSS.
- **Data Visualizations:** Interactive Recharts charts (churn trends, risk distributions, confusion matrices).
- **Customer 360 View:** Individual dossier displaying historical churn metrics, SHAP waterfall cards, and retention checklists.
