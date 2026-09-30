"""
ChurnSense AI — SQLAlchemy ORM Models (Database Schema)

Defines all database tables with UUIDs, timestamps, foreign keys,
indexes, and constraints for a normalized PostgreSQL schema.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


# ── Users ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="analyst")  # admin | analyst | viewer
    is_active = Column(Boolean, nullable=False, default=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="users")
    datasets = relationship("Dataset", back_populates="uploaded_by_user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="created_by_user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


# ── Organizations ────────────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    users = relationship("User", back_populates="organization")
    customers = relationship("Customer", back_populates="organization", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="organization", cascade="all, delete-orphan")
    models = relationship("MLModel", back_populates="organization", cascade="all, delete-orphan")


# ── Datasets ─────────────────────────────────────────────────────────────────

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    target_column = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="uploaded")
    # Status: uploaded | validating | validated | preprocessing | ready | error
    quality_score = Column(Float, nullable=True)
    validation_report = Column(JSON, nullable=True)
    preprocessing_config = Column(JSON, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="datasets")
    uploaded_by_user = relationship("User", back_populates="datasets")
    columns = relationship("DatasetColumn", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin")
    training_runs = relationship("TrainingRun", back_populates="dataset", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_datasets_org_status", "organization_id", "status"),
    )


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    dataset_id = Column(UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(50), nullable=False)  # numeric | categorical | boolean | datetime | text
    is_target = Column(Boolean, nullable=False, default=False)
    null_count = Column(Integer, nullable=True)
    unique_count = Column(Integer, nullable=True)
    mean = Column(Float, nullable=True)
    std = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    top_values = Column(JSON, nullable=True)  # [{value, count}]
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    dataset = relationship("Dataset", back_populates="columns")

    __table_args__ = (
        UniqueConstraint("dataset_id", "column_name", name="uq_dataset_column"),
    )


# ── Customers ────────────────────────────────────────────────────────────────

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(255), nullable=True)  # ID from source system
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    tenure = Column(Integer, nullable=True)
    contract_type = Column(String(100), nullable=True)
    monthly_charges = Column(Float, nullable=True)
    total_charges = Column(Float, nullable=True)
    payment_method = Column(String(100), nullable=True)
    services = Column(JSON, nullable=True)  # list of service names
    churn_label = Column(Boolean, nullable=True)  # known ground truth if available
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="customers")
    features = relationship("CustomerFeature", back_populates="customer", cascade="all, delete-orphan", lazy="selectin")
    predictions = relationship("Prediction", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_customers_org", "organization_id"),
        Index("ix_customers_ext_id", "organization_id", "external_id"),
    )


class CustomerFeature(Base):
    __tablename__ = "customer_features"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(255), nullable=False)
    feature_value = Column(String(1024), nullable=True)
    feature_type = Column(String(50), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    customer = relationship("Customer", back_populates="features")

    __table_args__ = (
        Index("ix_customer_features_customer", "customer_id"),
    )


# ── ML Models ────────────────────────────────────────────────────────────────

class MLModel(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    algorithm = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False, default="1.0.0")
    status = Column(String(50), nullable=False, default="training")
    # Status: training | trained | deployed | archived | failed
    is_active = Column(Boolean, nullable=False, default=False)
    artifact_path = Column(String(512), nullable=True)
    preprocessing_artifact_path = Column(String(512), nullable=True)
    feature_names = Column(JSON, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    training_dataset_id = Column(UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    training_dataset_version = Column(Integer, nullable=True)
    test_split = Column(Float, nullable=True)
    random_state = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    organization = relationship("Organization", back_populates="models")
    metrics = relationship("ModelMetric", back_populates="model", cascade="all, delete-orphan", lazy="selectin")
    training_run = relationship("TrainingRun", back_populates="model", uselist=False)
    predictions = relationship("Prediction", back_populates="model")

    __table_args__ = (
        Index("ix_models_org_active", "organization_id", "is_active"),
    )


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    model_id = Column(UUID(as_uuid=False), ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    split = Column(String(20), nullable=False)  # train | test | validation
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    confusion_matrix = Column(JSON, nullable=True)  # [[TN,FP],[FN,TP]]
    feature_importances = Column(JSON, nullable=True)  # {feature: importance}
    computed_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    model = relationship("MLModel", back_populates="metrics")


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    model_id = Column(UUID(as_uuid=False), ForeignKey("models.id", ondelete="CASCADE"), nullable=True)
    dataset_id = Column(UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="queued")
    # Status: queued | running | completed | failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    model = relationship("MLModel", back_populates="training_run")
    dataset = relationship("Dataset", back_populates="training_runs")


# ── Predictions ───────────────────────────────────────────────────────────────

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    model_id = Column(UUID(as_uuid=False), ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    churn_probability = Column(Float, nullable=False)
    churn_prediction = Column(Boolean, nullable=False)
    risk_level = Column(String(50), nullable=False)  # low | medium | high | critical
    prediction_threshold = Column(Float, nullable=False, default=0.5)
    input_features = Column(JSON, nullable=True)
    mode = Column(String(20), nullable=False, default="individual")  # individual | bulk
    batch_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    customer = relationship("Customer", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")
    created_by_user = relationship("User", back_populates="predictions")
    explanation = relationship("PredictionExplanation", back_populates="prediction", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    recommendations = relationship("Recommendation", back_populates="prediction", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_predictions_customer", "customer_id"),
        Index("ix_predictions_created_at", "created_at"),
        Index("ix_predictions_batch", "batch_id"),
    )


class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    prediction_id = Column(UUID(as_uuid=False), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, unique=True)
    shap_values = Column(JSON, nullable=True)  # {feature: shap_value}
    top_risk_factors = Column(JSON, nullable=True)  # [{feature, value, impact, direction}]
    top_protective_factors = Column(JSON, nullable=True)  # [{feature, value, impact, direction}]
    base_value = Column(Float, nullable=True)
    explanation_method = Column(String(50), nullable=False, default="shap")
    computed_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    prediction = relationship("Prediction", back_populates="explanation")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    prediction_id = Column(UUID(as_uuid=False), ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    # Categories: contract_upgrade | loyalty_incentive | pricing_review |
    #             personalized_support | service_resolution | success_outreach
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)  # Why this recommendation was generated
    priority = Column(Integer, nullable=False, default=1)  # 1 = highest
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    prediction = relationship("Prediction", back_populates="recommendations")

    __table_args__ = (
        Index("ix_recommendations_prediction", "prediction_id"),
    )


# ── Reports ───────────────────────────────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)  # overview | segment | model | customer
    model_id = Column(UUID(as_uuid=False), ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    dataset_id = Column(UUID(as_uuid=False), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True)
    content = Column(JSON, nullable=True)
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        Index("ix_reports_org", "organization_id"),
    )


# ── Audit Logs ────────────────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user", "user_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
