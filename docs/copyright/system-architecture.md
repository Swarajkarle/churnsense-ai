# System Architecture Documentation

The architecture of **ChurnSense AI** adheres to a clean, multi-layered design separating presentation, API routing, business services, analytical pipelines, and persistence.

---

## 1. High-Level Architectural Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER WEB CLIENT                                │
│    Desktop Browser / Mobile Viewport (Next.js 14 + React 18 UI)       │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTPS / JSON REST
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND GATEWAY                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ CORS Middleware | Request Logging | Exception Handlers | Auth    │  │
│  └─────────────────────────────────┬────────────────────────────────┘  │
│                                    ▼                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       API V1 ROUTERS                             │  │
│  │  /auth   /datasets   /models   /predictions   /analytics  /reports│  │
│  └─────────────────────────────────┬────────────────────────────────┘  │
└────────────────────────────────────┼───────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│        SERVICE LAYER            │   │      MACHINE LEARNING STACK      │
│ ┌─────────────────────────────┐ │   │ ┌──────────────────────────────┐ │
│ │ DatasetService              │ │   │ │ FeatureEngineer              │ │
│ │ TrainingService             │ │   │ │ ChurnPreprocessor (Impute/OH)│ │
│ │ PredictionService           │ │   │ │ ModelTrainer (LR/DT/RF/GB/XG)│ │
│ │ RecommendationEngine        │ │   │ │ ExplainabilityService (SHAP) │ │
│ │ AnalyticsService            │ │   │ └──────────────────────────────┘ │
│ └─────────────────────────────┘ │   └──────────────────────────────────┘
└────────────────┬────────────────┘                      │
                 │                                       │
                 ▼                                       ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│     PERSISTENCE (POSTGRESQL)    │   │      MODEL ARTIFACT STORE        │
│ 14 Relational Tables via        │   │ Serialized joblib pipelines      │
│ SQLAlchemy 2.0 AsyncPG ORM      │   │ & preprocessor transformers      │
└─────────────────────────────────┘   └──────────────────────────────────┘
```

---

## 2. Layered Architecture Breakdown

### 1. Presentation Tier (`frontend/`)
- Built using **Next.js 14 App Router** with full React Server Component and Client Component separation.
- Component architecture organized into atomic directories: `ui/`, `charts/`, `forms/`, `layout/`, and `tables/`.
- Styling driven by **Tailwind CSS** with a custom dark-mode token palette and glassmorphism cards.
- Server state managed via **TanStack React Query**, ensuring client-side caching and responsive revalidation.

### 2. API Routing & Middleware Tier (`backend/app/api/`)
- Built on **FastAPI**, leveraging Python asynchronous execution (`async`/`await`).
- Request serialization and response validation enforced strictly via **Pydantic v2 schemas**.
- Global middleware stack:
  - CORS Middleware: Configured via environment-controlled origin lists.
  - Exception Handlers: Standardized JSON error response formatting.
  - Dependency Injection: Centralized database sessions and JWT user identity injection.

### 3. Business Service Tier (`backend/app/services/`)
- Encapsulates domain logic independently of transport protocols.
- Handles dataset ingestion, validation rules, model training orchestration in background tasks, metric computation, and report aggregation.

### 4. Machine Learning & Inference Tier (`backend/app/ml/`)
- Operates as a modular analytical engine.
- Implements strict separation between transformation (`fit_transform`) during training and inference scoring (`transform`).
- Integrates SHAP explainer objects capable of interpreting tree models and linear baselines.

### 5. Data Persistence Tier (`database/`)
- Backed by **PostgreSQL 15+**.
- Database queries use **SQLAlchemy 2.0** async engine with `asyncpg` connection pooling.
- Schema evolution tracked through **Alembic** migrations with bidirectional `upgrade()` and `downgrade()` capabilities.
