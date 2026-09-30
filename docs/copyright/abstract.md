# Abstract

**Project Title:** AI-Based Customer Churn Prediction and Retention Recommendation System  
**Software Name:** ChurnSense AI  
**Author:** Swaraj Karle  
**Academic Year:** 2025–2026  

---

## Executive Summary

Customer churn represents one of the most critical operational challenges for subscription-based, recurring-revenue, and telecommunications businesses. Traditional churn mitigation approaches often rely either on retrospective exit surveys after a customer has canceled, or on complex machine learning models whose inner predictions remain an opaque "black box" to business and customer success teams.

**ChurnSense AI** is an original full-stack intelligence platform engineered to address this gap. The platform unites:

1. **Automated Data Profiling and Validation:** Validates uploaded customer datasets, performs quality scoring, and executes leakage-free preprocessing.
2. **Multi-Model Machine Learning Pipeline:** Trains, evaluates, and benchmarks multiple predictive algorithms (Logistic Regression, Decision Trees, Random Forests, Gradient Boosting, and XGBoost) using stratified splits and class-imbalance-resilient metrics (F1 Score, ROC-AUC).
3. **Transparent Explainability Layer:** Implements SHapley Additive exPlanations (SHAP) to attribute individual risk factors and protective factors for each specific customer prediction.
4. **Actionable Retention Recommendation Engine:** Features an original rule-based prescriptive engine that maps customer profiles, churn probabilities, and top SHAP risk factors into targeted, prioritized retention actions accompanied by clear rationales.
5. **Modern Reactive Web Application:** Delivers an intuitive executive dashboard, interactive Customer 360 views, batch and single prediction interfaces, and automated analytical reports built on Next.js 14, React 18, and Tailwind CSS.
6. **Robust Relational Backend:** Backed by an asynchronous FastAPI REST API and a normalized 14-table PostgreSQL schema managed through SQLAlchemy 2.0 and Alembic.

The complete software suite is developed as an integrated, reproducible platform to provide data-driven, interpretable, and proactive customer retention capabilities.
