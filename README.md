# ChurnSense AI

> **AI-Powered Customer Churn Intelligence & Retention Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-teal.svg)](https://fastapi.tiangolo.com)

---

## 📌 Project Overview

**ChurnSense AI** is a full-stack, production-quality AI platform built as a college software project for copyright registration. It helps organizations identify customers who are likely to churn, understand *why* they are at risk, and receive explainable retention recommendations.

> ⚠️ **Originality Notice**: This software implementation — including its source code, architecture, UI/UX design, feature engineering pipeline, explainability layer, recommendation engine, and documentation — is an original work created by the authors. It does not copy any existing GitHub repository or commercial product.
>
> General-purpose libraries (scikit-learn, XGBoost, SHAP, FastAPI, Next.js, etc.) are open-source tools used as dependencies; ownership of those libraries is not claimed.

---

## 🔴 Problem Statement

Customer churn — the loss of a client or subscriber — is one of the most significant challenges for subscription-based and service-oriented businesses. Acquiring a new customer is typically 5–7× more expensive than retaining an existing one. Yet most organizations lack actionable tools to:

1. Identify *which* customers are likely to leave before they do.
2. Understand *why* those customers are at risk.
3. Take *specific, data-driven actions* to retain them.

ChurnSense AI addresses all three gaps in a single integrated platform.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Data Management** | CSV upload, validation, quality analysis, preprocessing |
| **ML Pipeline** | Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost |
| **Model Management** | Versioning, comparison, metrics, confusion matrix |
| **Predictions** | Individual & bulk prediction, risk categorization |
| **Explainability** | SHAP-based feature attribution per prediction |
| **Recommendations** | Original rule-based retention recommendation engine |
| **Analytics** | Executive dashboard, churn trends, segment analysis |
| **Customer 360** | Full customer profile with prediction, explanation, history |
| **Reports** | Exportable PDF/JSON reports |
| **Auth** | JWT-based authentication with role-based access |

---

## 🏗️ Architecture

```
User
 ↓
Next.js 14 Frontend (TypeScript + Tailwind CSS + shadcn/ui)
 ↓
FastAPI REST API (Python 3.11+)
 ↓
 ┌──────────────────────────────────────┐
 │  Auth Service                        │
 │  Customer Service                    │
 │  Dataset Service                     │
 │  Analytics Service                   │
 │  Prediction Service                  │
 │  Model Training Service              │
 │  Explainability Service (SHAP)       │
 │  Recommendation Engine               │
 │  Report Service                      │
 └──────────────────────────────────────┘
 ↓
PostgreSQL (Supabase)
 ↓
ML Model Repository (Joblib)
```

---

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** — App Router, SSR/SSG
- **TypeScript** — Full type safety
- **Tailwind CSS** — Utility-first styling
- **shadcn/ui** — Accessible component primitives
- **Recharts** — Charts and visualizations
- **TanStack Query** — Server state management
- **Zustand** — Client state management
- **React Hook Form + Zod** — Form validation

### Backend
- **Python 3.11+** — Core language
- **FastAPI** — REST API framework
- **Pydantic v2** — Schema validation
- **SQLAlchemy 2.x** — ORM
- **Alembic** — Database migrations
- **python-jose** — JWT tokens
- **passlib** — Password hashing

### Machine Learning
- **scikit-learn** — Models, pipelines, metrics
- **XGBoost** — Gradient boosting
- **SHAP** — Model explainability
- **Pandas + NumPy** — Data processing
- **Joblib** — Model persistence
- **imbalanced-learn** — Class imbalance handling

### Database
- **PostgreSQL 15** via **Supabase**

### Deployment
- Frontend → **Vercel**
- Backend → **Render / Railway**
- Database → **Supabase**

---

## 📁 Project Structure

```
churnsense-ai/
├── frontend/           # Next.js 14 App Router full-stack web UI
├── backend/            # FastAPI asynchronous REST API
├── ml/                 # Standalone ML training, benchmarks, & synthetic data
│   ├── data/           # Synthetic demo data (safe to distribute)
│   ├── training/       # Standalone train.py pipeline
│   └── models/         # Model artifact documentation
├── database/           # PostgreSQL schema.sql, seed.sql, & migrations
├── docs/               # Comprehensive project documentation
│   ├── architecture/   # Architecture & system design
│   ├── api/            # REST API reference
│   ├── user-guide/     # Platform operational guide
│   ├── copyright/      # Formal copyright & originality documentation
│   └── diagrams/       # Flowcharts and ER diagrams
├── scripts/            # Dataset generators & utility scripts
├── .env.example        # Sanitized environment template
├── ATTRIBUTIONS.md     # Third-party open-source attribution matrix
├── LICENSE             # MIT License
└── docker-compose.yml  # Local stack containerization
```

---

## ⚡ Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15 (or Supabase account)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Swarajkarle/churnsense-ai.git
cd churnsense-ai
```

### 2. Environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Database setup
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.core.seed  # optional demo data
```

### 4. Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

---

## 🔑 Environment Variables

See [`.env.example`](.env.example) for all required variables.

Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon key |
| `NEXT_PUBLIC_API_URL` | Backend API base URL |

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test
```

---

## 📖 Documentation

- [API Documentation](docs/api/README.md)
- [Architecture](docs/architecture/README.md)
- [User Guide](docs/user-guide/README.md)
- [Copyright Documentation](docs/copyright/README.md)
- [Third-Party Attributions](ATTRIBUTIONS.md)

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
npx vercel --prod
```

### Backend (Render/Railway)
See [Deployment Guide](docs/architecture/deployment.md).

---

## ©️ Copyright & Originality

The **software implementation** of ChurnSense AI — including the application architecture, source code, UI/UX design, feature engineering pipeline, explainability integration, recommendation engine logic, database design, API structure, and documentation — constitutes an original creative work developed by the authors.

The general concept of customer churn prediction is not claimed as proprietary. Open-source libraries are used as dependencies under their respective licenses (see [ATTRIBUTIONS.md](ATTRIBUTIONS.md)).

The software implementation, source code, documentation, UI elements, and original components created by the authors are intended to constitute the copyrightable portions of the work, subject to applicable law and the determination of the Copyright Office.

---

## 👤 Author

**Swaraj Karle**
3rd-Year Computer Engineering Student
Project developed: 2025–2026

---

## 📄 License

[MIT License](LICENSE) — See LICENSE file for details.
