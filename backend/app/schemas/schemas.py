"""
ChurnSense AI — Pydantic v2 Schemas

Request/response models for all API endpoints.
These are separate from SQLAlchemy ORM models to maintain clean separation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Common ────────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    organization_name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    organization_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)


# ── Dataset ───────────────────────────────────────────────────────────────────

class DatasetColumnSchema(BaseModel):
    column_name: str
    data_type: str
    is_target: bool
    null_count: Optional[int]
    unique_count: Optional[int]
    mean: Optional[float]
    std: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    top_values: Optional[List[Dict[str, Any]]]

    model_config = {"from_attributes": True}


class DatasetResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    file_size_bytes: Optional[int]
    row_count: Optional[int]
    column_count: Optional[int]
    target_column: Optional[str]
    status: str
    quality_score: Optional[float]
    validation_report: Optional[Dict[str, Any]]
    version: int
    created_at: datetime
    columns: List[DatasetColumnSchema] = []

    model_config = {"from_attributes": True}


class DatasetValidationResult(BaseModel):
    is_valid: bool
    quality_score: float
    row_count: int
    column_count: int
    missing_values_total: int
    duplicate_rows: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    boolean_columns: List[str]
    issues: List[Dict[str, Any]]
    warnings: List[str]
    column_profiles: List[DatasetColumnSchema]


class PreprocessingConfigRequest(BaseModel):
    target_column: str
    test_split: float = Field(0.2, ge=0.1, le=0.5)
    handle_missing: str = "mean_median"  # mean_median | drop | constant
    encode_categorical: str = "onehot"  # onehot | label | ordinal
    scale_numeric: str = "standard"  # standard | minmax | none
    handle_outliers: bool = True
    handle_imbalance: str = "none"  # none | smote | class_weight


# ── ML Models ─────────────────────────────────────────────────────────────────

class TrainingRequest(BaseModel):
    dataset_id: str
    target_column: str
    algorithms: List[str] = Field(
        default=["logistic_regression", "random_forest", "gradient_boosting"]
    )
    test_split: float = Field(0.2, ge=0.1, le=0.5)
    random_state: int = 42
    preprocessing_config: Optional[PreprocessingConfigRequest] = None
    notes: Optional[str] = None


class ModelMetricSchema(BaseModel):
    split: str
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    roc_auc: Optional[float]
    confusion_matrix: Optional[List[List[int]]]
    feature_importances: Optional[Dict[str, float]]

    model_config = {"from_attributes": True}


class MLModelResponse(BaseModel):
    id: str
    name: str
    algorithm: str
    version: str
    status: str
    is_active: bool
    feature_names: Optional[List[str]]
    hyperparameters: Optional[Dict[str, Any]]
    test_split: Optional[float]
    notes: Optional[str]
    created_at: datetime
    metrics: List[ModelMetricSchema] = []

    model_config = {"from_attributes": True}


class ModelActivateRequest(BaseModel):
    model_id: str


# ── Predictions ───────────────────────────────────────────────────────────────

class IndividualPredictionRequest(BaseModel):
    customer_id: Optional[str] = None
    features: Dict[str, Any]
    model_id: Optional[str] = None  # uses active model if None
    threshold: float = Field(0.5, ge=0.0, le=1.0)


class PredictionFactorSchema(BaseModel):
    feature: str
    value: Any
    shap_value: float
    direction: str  # positive | negative (relative to churn)
    description: str


class PredictionExplanationSchema(BaseModel):
    top_risk_factors: List[PredictionFactorSchema]
    top_protective_factors: List[PredictionFactorSchema]
    base_value: Optional[float]
    explanation_method: str

    model_config = {"from_attributes": True}


class RecommendationSchema(BaseModel):
    id: str
    category: str
    title: str
    description: str
    rationale: Optional[str]
    priority: int

    model_config = {"from_attributes": True}


class PredictionResponse(BaseModel):
    id: str
    customer_id: Optional[str]
    model_id: Optional[str]
    churn_probability: float
    churn_prediction: bool
    risk_level: str
    prediction_threshold: float
    created_at: datetime
    explanation: Optional[PredictionExplanationSchema]
    recommendations: List[RecommendationSchema] = []

    model_config = {"from_attributes": True}


# ── Analytics ─────────────────────────────────────────────────────────────────

class OverviewAnalyticsResponse(BaseModel):
    total_customers: int
    customers_at_risk: int
    predicted_churners: int
    average_churn_probability: float
    retention_opportunity_count: int
    active_model_accuracy: Optional[float]
    active_model_precision: Optional[float]
    active_model_recall: Optional[float]
    active_model_f1: Optional[float]
    active_model_roc_auc: Optional[float]
    active_model_name: Optional[str]


class ChurnTrendPoint(BaseModel):
    period: str
    churn_rate: float
    total: int
    churned: int


class SegmentAnalyticsResponse(BaseModel):
    by_contract: List[Dict[str, Any]]
    by_tenure_group: List[Dict[str, Any]]
    by_payment_method: List[Dict[str, Any]]
    risk_distribution: List[Dict[str, Any]]


# ── Customers ─────────────────────────────────────────────────────────────────

class CustomerResponse(BaseModel):
    id: str
    external_id: Optional[str]
    name: Optional[str]
    email: Optional[str]
    tenure: Optional[int]
    contract_type: Optional[str]
    monthly_charges: Optional[float]
    total_charges: Optional[float]
    payment_method: Optional[str]
    services: Optional[List[str]]
    churn_label: Optional[bool]
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerDetailResponse(CustomerResponse):
    latest_prediction: Optional[PredictionResponse]
    prediction_history: List[PredictionResponse] = []


# ── Reports ───────────────────────────────────────────────────────────────────

class ReportGenerateRequest(BaseModel):
    title: str = "ChurnSense AI Report"
    report_type: str = "overview"
    model_id: Optional[str] = None
    dataset_id: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    title: str
    report_type: str
    content: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = {"from_attributes": True}
