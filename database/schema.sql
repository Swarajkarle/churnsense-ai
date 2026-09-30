-- =============================================================================
-- ChurnSense AI — PostgreSQL Database Schema
-- Normalized 14-table schema supporting multi-tenant churn intelligence.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_organizations_slug ON organizations (slug);

-- 2. Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'analyst' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    organization_id UUID REFERENCES organizations (id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- 3. Customers
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    external_id VARCHAR(255),
    name VARCHAR(255),
    email VARCHAR(255),
    tenure INTEGER,
    contract_type VARCHAR(100),
    monthly_charges FLOAT,
    total_charges FLOAT,
    payment_method VARCHAR(100),
    services JSON,
    churn_label BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_customers_org ON customers (organization_id);
CREATE INDEX IF NOT EXISTS ix_customers_ext ON customers (external_id);

-- 4. Customer Features
CREATE TABLE IF NOT EXISTS customer_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    feature_name VARCHAR(255) NOT NULL,
    feature_value VARCHAR(1024),
    feature_type VARCHAR(50),
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_cust_features_id ON customer_features (customer_id);

-- 5. Datasets
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users (id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes INTEGER,
    row_count INTEGER,
    column_count INTEGER,
    target_column VARCHAR(100),
    status VARCHAR(50) DEFAULT 'uploaded' NOT NULL,
    quality_score FLOAT,
    validation_report JSON,
    preprocessing_config JSON,
    version INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 6. Dataset Columns
CREATE TABLE IF NOT EXISTS dataset_columns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES datasets (id) ON DELETE CASCADE,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    is_target BOOLEAN DEFAULT FALSE NOT NULL,
    null_count INTEGER,
    unique_count INTEGER,
    mean FLOAT,
    std FLOAT,
    min_value FLOAT,
    max_value FLOAT,
    top_values JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_dataset_column UNIQUE (dataset_id, column_name)
);

-- 7. Models
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'trained' NOT NULL,
    is_active BOOLEAN DEFAULT FALSE NOT NULL,
    artifact_path VARCHAR(512),
    preprocessing_artifact_path VARCHAR(512),
    feature_names JSON,
    hyperparameters JSON,
    training_dataset_id UUID REFERENCES datasets (id) ON DELETE SET NULL,
    training_dataset_version INTEGER,
    test_split FLOAT,
    random_state INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 8. Model Metrics
CREATE TABLE IF NOT EXISTS model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models (id) ON DELETE CASCADE,
    split VARCHAR(20) DEFAULT 'test' NOT NULL,
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    confusion_matrix JSON,
    feature_importances JSON,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 9. Predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers (id) ON DELETE SET NULL,
    model_id UUID REFERENCES models (id) ON DELETE SET NULL,
    created_by UUID REFERENCES users (id) ON DELETE SET NULL,
    churn_probability FLOAT NOT NULL,
    churn_prediction BOOLEAN NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    prediction_threshold FLOAT DEFAULT 0.5 NOT NULL,
    input_features JSON,
    mode VARCHAR(20) DEFAULT 'individual' NOT NULL,
    batch_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_predictions_model ON predictions (model_id);
CREATE INDEX IF NOT EXISTS ix_predictions_risk ON predictions (risk_level);

-- 10. Prediction Explanations
CREATE TABLE IF NOT EXISTS prediction_explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL UNIQUE REFERENCES predictions (id) ON DELETE CASCADE,
    shap_values JSON,
    top_risk_factors JSON,
    top_protective_factors JSON,
    base_value FLOAT,
    explanation_method VARCHAR(50) NOT NULL,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 11. Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES predictions (id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT,
    priority INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 12. Training Runs
CREATE TABLE IF NOT EXISTS training_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models (id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets (id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds FLOAT,
    error_message TEXT,
    log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 13. Reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    created_by UUID REFERENCES users (id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    model_id UUID REFERENCES models (id) ON DELETE SET NULL,
    dataset_id UUID REFERENCES datasets (id) ON DELETE SET NULL,
    content JSON,
    file_path VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 14. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users (id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
