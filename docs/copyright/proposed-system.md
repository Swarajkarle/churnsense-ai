# Proposed System — ChurnSense AI

## 1. Problem Context

In modern subscription businesses, customer acquisition costs (CAC) typically exceed customer retention costs by five to seven times. Despite this economic imperative, organizations struggle to intervene proactively because:

- Predictions occur in analytical silos disconnected from customer success workflows.
- Predictions lack interpretability, leaving account managers uncertain *why* a customer is flagged.
- Predictive scores fail to translate into tangible, policy-compliant retention offers.

## 2. Proposed System Overview

**ChurnSense AI** introduces an integrated end-to-end architecture bridging statistical machine learning, explainable AI (XAI), and operational decision support. 

### Key Pillars of the Proposed Solution

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   PREDICTION    │ ───►  │ EXPLAINABILITY  │ ───►  │ RECOMMENDATION  │
│  (ML Pipeline)  │       │ (SHAP Analysis) │       │ (Decision Logic)│
└─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │                         │
         ▼                         ▼                         ▼
Probabilistic churn       Specific contributing     Prioritized retention
score & risk tier         drivers (risk/protective) actions with rationale
```

1. **Multi-Model Pipeline Architecture:** 
   Rather than hardcoding a single estimator, the system supports training, empirical benchmarking, and activation across five algorithms:
   - Logistic Regression (linear baseline)
   - Decision Tree (transparent rule-based partitioner)
   - Random Forest (bagging ensemble)
   - Gradient Boosting (sequential residual boosting)
   - XGBoost (regularized gradient boosting)

2. **Per-Prediction Attribution (SHAP):**
   Utilizes TreeExplainer and LinearExplainer with fallback heuristics to compute precise additive contributions for each customer attribute, demystifying the model output.

3. **Contextual Retention Recommendation Engine:**
   An original rule-based engine that evaluates:
   - Customer tenure tier (new onboarding, developing, established, loyal)
   - Contract structure and billing preferences
   - Financial commitment (monthly-to-total charge ratios)
   - Service ecosystem utilization (e.g., tech support, online security)
   - Top SHAP factor attribution
   Each recommendation provides a business rationale, priority score, and action description.

4. **Multi-Tenant Enterprise Foundation:**
   - Multi-tenant data segregation by organization.
   - Role-Based Access Control (RBAC): Admin, Analyst, Viewer.
   - Comprehensive audit logging and exportable reporting (JSON/PDF-ready).
