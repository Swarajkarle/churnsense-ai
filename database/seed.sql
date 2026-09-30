-- =============================================================================
-- ChurnSense AI — Initial Database Seed
-- Default demo organization and administrative user for development.
-- Default credentials:
-- Email: admin@churnsense.ai
-- Password: Password123!
-- =============================================================================

-- Default Organization
INSERT INTO organizations (id, name, slug, industry, created_at, updated_at)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'ChurnSense Demo Corp',
    'churnsense-demo',
    'Telecommunications & SaaS',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (slug) DO NOTHING;

-- Default Admin User (Password: Password123!)
INSERT INTO users (id, email, hashed_password, full_name, role, is_active, organization_id, created_at, updated_at)
VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'admin@churnsense.ai',
    '$2b$12$1.IvwiSCEgGowdrAwWyDjOUPXXcOPE4MN1e9S70c8WyvOyvPo6ROu',
    'Demo Administrator',
    'admin',
    TRUE,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;

-- Sample Seed Customers
INSERT INTO customers (id, organization_id, external_id, name, email, tenure, contract_type, monthly_charges, total_charges, payment_method, services, churn_label, created_at, updated_at)
VALUES 
(
    'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'CUST-001',
    'Sarah Jenkins',
    'sarah.j@example.com',
    34,
    'One year',
    65.50,
    2227.00,
    'Credit card (automatic)',
    '["PhoneService", "InternetService", "TechSupport"]'::json,
    FALSE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'CUST-002',
    'Marcus Vance',
    'm.vance@example.com',
    4,
    'Month-to-month',
    89.20,
    356.80,
    'Electronic check',
    '["PhoneService", "InternetService", "StreamingTV"]'::json,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;
