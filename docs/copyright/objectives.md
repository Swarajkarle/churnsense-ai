# Project Objectives

The primary engineering and analytical objectives of **ChurnSense AI** are:

## 1. Primary Objectives

1. **End-to-End Operationalization:**
   Build a complete, production-grade web application platform that integrates dataset management, machine learning lifecycle, inference serving, and user interaction into a cohesive system rather than fragmented research scripts.

2. **Empirical Model Comparison:**
   Provide automated training, cross-validation, and benchmarking across diverse model families (Linear, Decision Trees, Ensembles, Gradient Boosting) using rigorous classification metrics (F1 Score, ROC-AUC, Precision, Recall) resilient to class imbalance.

3. **Leakage-Free Preprocessing:**
   Design and implement a serialized feature engineering and preprocessing transformer that fits strictly on training partitions and applies identical transformations during batch and single-customer inference.

4. **Transparent Predictions (Explainable AI):**
   Integrate SHAP (SHapley Additive exPlanations) to decompose single and batch predictions into human-interpretable risk drivers and protective factors.

5. **Decision Support & Retention Recommendations:**
   Engineer an original prescriptive recommendation system that translates quantitative predictions and SHAP factor weights into actionable, prioritized customer retention steps.

6. **Normalized Relational Data Persistence:**
   Architect a normalized 14-table PostgreSQL schema capturing users, organizations, datasets, column profiles, trained models, metrics, predictions, explanations, recommendations, and audit logs.

7. **Executive & Analytical Visualization:**
   Create an intuitive, responsive frontend dashboard providing real-time KPI metrics, cohort distributions, model performance comparisons, and individual Customer 360 dossiers.

8. **Security & Governance:**
   Implement industry-standard security including bcrypt password hashing, stateless JWT authentication, role-based access control (RBAC), and strict environment-based secrets management.
