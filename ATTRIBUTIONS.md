# Third-Party Attributions

This file lists all significant third-party libraries, frameworks, datasets, fonts,
icons, and other resources used in ChurnSense AI, along with their licenses.

Ownership of these libraries and resources is NOT claimed. They are used as
dependencies under the terms of their respective licenses.

---

## Backend Libraries

| Library | Version | License | Purpose |
|---|---|---|---|
| FastAPI | 0.111.x | MIT | REST API framework |
| Pydantic | 2.x | MIT | Data validation & serialization |
| SQLAlchemy | 2.x | MIT | ORM |
| Alembic | 1.x | MIT | Database migrations |
| python-jose | 3.x | MIT | JWT token handling |
| passlib | 1.x | BSD | Password hashing |
| bcrypt | 4.x | Apache 2.0 | Password hashing backend |
| uvicorn | 0.x | BSD | ASGI server |
| python-multipart | 0.x | Apache 2.0 | File upload handling |
| httpx | 0.x | BSD | HTTP client (testing) |
| pytest | 7.x | MIT | Test framework |
| pytest-asyncio | 0.x | Apache 2.0 | Async test support |

## Machine Learning Libraries

| Library | Version | License | Purpose |
|---|---|---|---|
| scikit-learn | 1.x | BSD-3-Clause | ML models, pipelines, metrics |
| XGBoost | 2.x | Apache 2.0 | Gradient boosting model |
| SHAP | 0.x | MIT | Model explainability |
| Pandas | 2.x | BSD-3-Clause | Data manipulation |
| NumPy | 1.x | BSD-3-Clause | Numerical operations |
| Joblib | 1.x | BSD-3-Clause | Model serialization |
| imbalanced-learn | 0.x | MIT | Class imbalance handling |
| Matplotlib | 3.x | PSF/BSD | Plotting (non-UI) |
| Seaborn | 0.x | BSD-3-Clause | Statistical visualization (notebooks) |
| SciPy | 1.x | BSD-3-Clause | Statistical functions |

## Frontend Libraries

| Library | Version | License | Purpose |
|---|---|---|---|
| Next.js | 14.x | MIT | React framework |
| React | 18.x | MIT | UI library |
| TypeScript | 5.x | Apache 2.0 | Type safety |
| Tailwind CSS | 3.x | MIT | Utility-first CSS |
| shadcn/ui | Latest | MIT | Accessible component primitives |
| Radix UI | Latest | MIT | Headless component primitives (via shadcn) |
| Recharts | 2.x | MIT | Charting library |
| TanStack Query | 5.x | MIT | Server state management |
| Zustand | 4.x | MIT | Client state management |
| React Hook Form | 7.x | MIT | Form management |
| Zod | 3.x | MIT | Schema validation |
| Axios | 1.x | MIT | HTTP client |
| Lucide React | Latest | ISC | Icon library |
| date-fns | 3.x | MIT | Date utilities |
| clsx | 2.x | MIT | Class merging utility |
| tailwind-merge | 2.x | MIT | Tailwind class merging |

## Fonts

| Font | License | Source |
|---|---|---|
| Inter | SIL Open Font License 1.1 | Google Fonts |
| JetBrains Mono | SIL Open Font License 1.1 | Google Fonts |

## Icons

| Icon Set | License | Source |
|---|---|---|
| Lucide | ISC License | https://lucide.dev |

## Demo Dataset

The synthetic demo dataset included in `ml/data/synthetic/` was **generated
programmatically** using a custom Python script (`scripts/generate_demo_data.py`).
It does not reproduce any real customer data and is not derived from any
proprietary dataset.

If users choose to use the IBM Telco Customer Churn dataset (available on Kaggle),
they should review the dataset's license terms independently. ChurnSense AI
does not bundle or distribute that dataset.

---

## Notes

- All libraries above are used as dependencies under their respective licenses.
- Ownership of any of these libraries is not claimed.
- The original creative work in ChurnSense AI consists of the application
  architecture, source code, UI/UX design, feature engineering pipeline,
  explainability integration, recommendation engine, database schema, API
  design, and documentation, all created by the project authors.
