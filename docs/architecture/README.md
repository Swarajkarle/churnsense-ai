# ChurnSense AI — Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│           Next.js 14 · TypeScript · Tailwind CSS                │
│    Pages: Landing, Login, Register, Dashboard, Customers,       │
│           Datasets, Models, Predictions, Analytics,             │
│           Recommendations, History, Reports, Settings           │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS · REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Application                           │
│                    (Python 3.11+)                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Auth Service │  │Dataset Svc   │  │  Training Service    │  │
│  │ JWT + bcrypt │  │CSV Validation│  │  Background Tasks    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Prediction   │  │Explainability│  │  Recommendation      │  │
│  │   Service    │  │ (SHAP)       │  │     Engine           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Analytics    │  │Report Service│                            │
│  │   Service    │  │              │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ SQLAlchemy async
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                PostgreSQL (Supabase)                            │
│  users · organizations · datasets · dataset_columns            │
│  customers · customer_features · models · model_metrics        │
│  predictions · prediction_explanations · recommendations       │
│  training_runs · reports · audit_logs                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ Joblib
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ML Artifact Store (filesystem)                     │
│  model_<id>.joblib · preprocessor_<id>.joblib                  │
└─────────────────────────────────────────────────────────────────┘
```

## Service Responsibilities

| Service | Responsibility |
|---|---|
| `AuthService` | Registration, login, JWT issuance, password hashing |
| `DatasetService` | CSV validation, column profiling, quality scoring |
| `TrainingService` | Background training orchestration, DB record creation |
| `PredictionService` | Model loading, preprocessing, SHAP explanation, recommendations |
| `ExplainabilityService` | SHAP value computation, factor attribution |
| `RecommendationEngine` | Rule-based retention action generation |
| `AnalyticsService` | Dashboard KPI computation from database |
| `ReportService` | Aggregated report generation |

## Directory Structure

```
churnsense-ai/
├── frontend/                # Next.js 14 + TypeScript
│   ├── app/
│   │   ├── page.tsx         # Landing page
│   │   ├── login/           # Auth pages
│   │   ├── register/
│   │   └── dashboard/       # Protected app pages
│   ├── components/layout/   # Sidebar, Providers
│   ├── lib/                 # API client, Zustand store
│   └── types/               # TypeScript interfaces
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── api/v1/          # Route handlers
│   │   ├── core/            # Config, DB, security, logging
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic services
│   │   └── ml/              # ML pipeline (features, preprocessing, training, evaluation)
│   └── tests/               # pytest test suite
│
├── ml/                      # Standalone ML scripts and notebooks
│   └── data/synthetic/      # Synthetic demo data
│
├── database/migrations/     # Alembic migration scripts
├── docs/                    # All documentation
├── scripts/                 # Utility scripts
└── ...                      # Root config files
```
