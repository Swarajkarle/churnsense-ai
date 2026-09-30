# Technology Stack Documentation

This document outlines the complete technology stack used in the development and deployment of **ChurnSense AI**.

---

## 1. Web Application & Frontend

| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 14.2.5 | React enterprise framework (App Router architecture) |
| **React** | 18.x | Declarative component UI library |
| **TypeScript** | 5.x | Static typing and compiler checks |
| **Tailwind CSS** | 3.x | Utility-first styling framework with custom design system |
| **Recharts** | 2.x | Data visualization (ROC curves, risk distributions, trends) |
| **Lucide React** | 0.x | Modern SVG icon system |
| **Zustand** | 4.x | Lightweight client auth state store |
| **TanStack Query** | 5.x | Server state management and background revalidation |
| **React Hook Form** | 7.x | Performant form management |
| **Zod** | 3.x | Client-side schema validation |
| **Sonner** | 1.x | Toast notification alerts |
| **Axios** | 1.x | HTTP client with automatic JWT bearer authorization interceptor |

---

## 2. Backend & API Services

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.9 / 3.11+ | Primary backend programming language |
| **FastAPI** | 0.111.0 | High-performance asynchronous REST API framework |
| **Uvicorn** | 0.30.1 | ASGI server implementation |
| **Pydantic** | 2.7.4 | Request/response data validation and parsing |
| **Pydantic Settings** | 2.3.3 | Typed environment configuration management |
| **SQLAlchemy** | 2.0.31 | Asynchronous Object-Relational Mapping (ORM) |
| **Alembic** | 1.13.2 | Database schema migration engine |
| **AsyncPG** | 0.29.0 | High-speed PostgreSQL async driver |
| **Psycopg2-binary** | 2.9.9 | PostgreSQL sync driver for Alembic migration commands |
| **Python-Jose** | 3.3.0 | JSON Web Token (JWT) encoding and verification |
| **Passlib & BCrypt**| 1.7.4 / 4.1.3 | Cryptographic password hashing |
| **Python-Multipart**| 0.0.9 | Multipart/form-data upload parsing |
| **Aiofiles** | 23.2.1 | Asynchronous filesystem I/O |

---

## 3. Machine Learning & Data Science

| Technology | Version | Purpose |
|---|---|---|
| **Scikit-Learn** | 1.5.1 | Machine learning models, preprocessing pipelines, metrics |
| **XGBoost** | 2.1.0 | Extreme Gradient Boosting classification algorithm |
| **SHAP** | 0.45.1 | Shapley Additive exPlanations (XAI) |
| **Pandas** | 2.2.2 | Data frame structures and tabular transformations |
| **NumPy** | 1.26.4 | Numerical matrix and array computations |
| **Joblib** | 1.4.2 | Pipeline and model binary serialization |
| **Imbalanced-Learn**| 0.12.3 | Class balancing and sampling utilities |
| **SciPy** | 1.13.1 | Statistical operations and distribution modeling |

---

## 4. Testing & Quality Assurance

| Technology | Version | Purpose |
|---|---|---|
| **Pytest** | 8.2.2 | Unit, integration, and API test framework |
| **Pytest-Asyncio** | 0.23.7 | Async test execution support |
| **Pytest-Cov** | 5.0.0 | Test coverage measurement |
| **Next Lint** | 14.x | Frontend ESLint and TypeScript compilation checks |

---

## 5. Database & Infrastructure

| Technology | Version | Purpose |
|---|---|---|
| **PostgreSQL** | 15+ | Primary relational database |
| **Docker & Compose**| 3.8+ | Local and staging containerization stack |
| **Supabase** | Cloud | Managed PostgreSQL provider option |
