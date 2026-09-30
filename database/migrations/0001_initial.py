"""
ChurnSense AI — Initial Database Migration

Creates all tables defined in the ORM models.
Run with: alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, default="analyst"),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Datasets
    op.create_table(
        "datasets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("column_count", sa.Integer, nullable=True),
        sa.Column("target_column", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="uploaded"),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("validation_report", sa.JSON, nullable=True),
        sa.Column("preprocessing_config", sa.JSON, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Dataset Columns
    op.create_table(
        "dataset_columns",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(255), nullable=False),
        sa.Column("data_type", sa.String(50), nullable=False),
        sa.Column("is_target", sa.Boolean, nullable=False, default=False),
        sa.Column("null_count", sa.Integer, nullable=True),
        sa.Column("unique_count", sa.Integer, nullable=True),
        sa.Column("mean", sa.Float, nullable=True),
        sa.Column("std", sa.Float, nullable=True),
        sa.Column("min_value", sa.Float, nullable=True),
        sa.Column("max_value", sa.Float, nullable=True),
        sa.Column("top_values", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Customers
    op.create_table(
        "customers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("tenure", sa.Integer, nullable=True),
        sa.Column("contract_type", sa.String(100), nullable=True),
        sa.Column("monthly_charges", sa.Float, nullable=True),
        sa.Column("total_charges", sa.Float, nullable=True),
        sa.Column("payment_method", sa.String(100), nullable=True),
        sa.Column("services", sa.JSON, nullable=True),
        sa.Column("churn_label", sa.Boolean, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_customers_org", "customers", ["organization_id"])

    # Customer Features
    op.create_table(
        "customer_features",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_name", sa.String(255), nullable=False),
        sa.Column("feature_value", sa.String(1024), nullable=True),
        sa.Column("feature_type", sa.String(50), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Models
    op.create_table(
        "models",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("algorithm", sa.String(100), nullable=False),
        sa.Column("version", sa.String(50), nullable=False, default="1.0.0"),
        sa.Column("status", sa.String(50), nullable=False, default="training"),
        sa.Column("is_active", sa.Boolean, nullable=False, default=False),
        sa.Column("artifact_path", sa.String(512), nullable=True),
        sa.Column("preprocessing_artifact_path", sa.String(512), nullable=True),
        sa.Column("feature_names", sa.JSON, nullable=True),
        sa.Column("hyperparameters", sa.JSON, nullable=True),
        sa.Column("training_dataset_id", sa.String(36), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("training_dataset_version", sa.Integer, nullable=True),
        sa.Column("test_split", sa.Float, nullable=True),
        sa.Column("random_state", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Model Metrics
    op.create_table(
        "model_metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("model_id", sa.String(36), sa.ForeignKey("models.id", ondelete="CASCADE"), nullable=False),
        sa.Column("split", sa.String(20), nullable=False),
        sa.Column("accuracy", sa.Float, nullable=True),
        sa.Column("precision", sa.Float, nullable=True),
        sa.Column("recall", sa.Float, nullable=True),
        sa.Column("f1_score", sa.Float, nullable=True),
        sa.Column("roc_auc", sa.Float, nullable=True),
        sa.Column("confusion_matrix", sa.JSON, nullable=True),
        sa.Column("feature_importances", sa.JSON, nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Training Runs
    op.create_table(
        "training_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("model_id", sa.String(36), sa.ForeignKey("models.id", ondelete="CASCADE"), nullable=True),
        sa.Column("dataset_id", sa.String(36), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("log", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Predictions
    op.create_table(
        "predictions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("customer_id", sa.String(36), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("model_id", sa.String(36), sa.ForeignKey("models.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("churn_probability", sa.Float, nullable=False),
        sa.Column("churn_prediction", sa.Boolean, nullable=False),
        sa.Column("risk_level", sa.String(50), nullable=False),
        sa.Column("prediction_threshold", sa.Float, nullable=False, default=0.5),
        sa.Column("input_features", sa.JSON, nullable=True),
        sa.Column("mode", sa.String(20), nullable=False, default="individual"),
        sa.Column("batch_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_predictions_customer", "predictions", ["customer_id"])
    op.create_index("ix_predictions_created_at", "predictions", ["created_at"])

    # Prediction Explanations
    op.create_table(
        "prediction_explanations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("prediction_id", sa.String(36), sa.ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("shap_values", sa.JSON, nullable=True),
        sa.Column("top_risk_factors", sa.JSON, nullable=True),
        sa.Column("top_protective_factors", sa.JSON, nullable=True),
        sa.Column("base_value", sa.Float, nullable=True),
        sa.Column("explanation_method", sa.String(50), nullable=False, default="shap"),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("prediction_id", sa.String(36), sa.ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("rationale", sa.Text, nullable=True),
        sa.Column("priority", sa.Integer, nullable=False, default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Reports
    op.create_table(
        "reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("model_id", sa.String(36), sa.ForeignKey("models.id", ondelete="SET NULL"), nullable=True),
        sa.Column("dataset_id", sa.String(36), sa.ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("content", sa.JSON, nullable=True),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_user", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reports")
    op.drop_table("recommendations")
    op.drop_table("prediction_explanations")
    op.drop_table("predictions")
    op.drop_table("training_runs")
    op.drop_table("model_metrics")
    op.drop_table("models")
    op.drop_table("customer_features")
    op.drop_table("customers")
    op.drop_table("dataset_columns")
    op.drop_table("datasets")
    op.drop_table("users")
    op.drop_table("organizations")
