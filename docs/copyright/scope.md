# Project Scope

## 1. System In-Scope Capabilities

### Data Ingestion and Validation
- Uploading tabular customer datasets in standard comma-separated value (CSV) format.
- Automatic column type inference (numeric, categorical, boolean, datetime).
- Calculation of dataset quality metrics (completeness, duplicate rate, outlier detection).
- Dataset versioning and metadata indexing.

### Machine Learning and Predictive Analytics
- Offline and on-demand model training on arbitrary uploaded customer datasets.
- Support for 5 diverse classification algorithms (Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost).
- Stratified train/test splitting preserving class ratios.
- Comprehensive metric evaluation (Accuracy, Precision, Recall, F1 Score, ROC-AUC, Confusion Matrix).
- Dynamic model activation allowing analysts to select the active production model.
- Real-time single customer churn inference.
- High-throughput batch inference on uploaded customer rosters.
- Four-tier risk level classification (Low, Medium, High, Critical) with configurable decision thresholds.

### Explainability and Prescriptive Actions
- Per-prediction SHAP factor attribution displaying top risk and protective drivers.
- Human-readable narrative summaries explaining feature impacts.
- Rule-based retention action engine prioritizing interventions with concrete business rationale.

### Enterprise Web Application
- JWT-based authentication with auto-refreshing sessions.
- Multi-organization data isolation.
- Role-based permissions (Admin, Analyst, Viewer).
- Interactive visual dashboards featuring KPIs, monthly churn trends, and segment breakdowns.
- Customer 360 detailed dossier pages.
- Analytical reports generation and JSON export.
- Full responsive design supporting desktop and tablet viewports.

---

## 2. System Out-of-Scope Boundaries

To maintain software integrity and avoid overclaiming, the following aspects are explicitly defined as out of scope:

1. **Real-Time Event Stream Ingestion:**
   The platform processes tabular snapshots and batch files; it does not implement continuous streaming message queues (e.g., Apache Kafka / Apache Flink).
2. **Guaranteed Churn Prevention:**
   Predictions and recommendations are probabilistic estimates and heuristic suggestions; they do not claim deterministic or guaranteed business outcomes.
3. **Automated Marketing Campaign Dispatch:**
   The platform outputs prioritized recommendations; direct email/SMS delivery integration (e.g., via Twilio or SendGrid) is deferred to future API webhooks.
4. **Native Mobile Applications:**
   The interface is a mobile-responsive Progressive Web App (PWA); native iOS and Android packages are not included.
