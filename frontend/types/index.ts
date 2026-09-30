/**
 * ChurnSense AI — TypeScript Type Definitions
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: "admin" | "analyst" | "viewer";
  is_active: boolean;
  organization_id: string | null;
  created_at: string;
}

export interface Dataset {
  id: string;
  name: string;
  description?: string;
  file_size_bytes?: number;
  row_count?: number;
  column_count?: number;
  target_column?: string;
  status: "uploaded" | "validating" | "validated" | "preprocessing" | "ready" | "error";
  quality_score?: number;
  validation_report?: ValidationReport;
  version: number;
  created_at: string;
  columns: DatasetColumn[];
}

export interface DatasetColumn {
  column_name: string;
  data_type: "numeric" | "categorical" | "boolean" | "datetime" | "text";
  is_target: boolean;
  null_count?: number;
  unique_count?: number;
  mean?: number;
  std?: number;
  min_value?: number;
  max_value?: number;
  top_values?: Array<{ value: string; count: number }>;
}

export interface ValidationReport {
  is_valid: boolean;
  quality_score: number;
  row_count: number;
  column_count: number;
  missing_values_total: number;
  duplicate_rows: number;
  numeric_columns: string[];
  categorical_columns: string[];
  boolean_columns: string[];
  issues: ValidationIssue[];
  warnings: string[];
  column_profiles: DatasetColumn[];
}

export interface ValidationIssue {
  severity: "error" | "warning";
  message: string;
  column?: string;
  missing_count?: number;
  missing_pct?: number;
}

export interface MLModel {
  id: string;
  name: string;
  algorithm: string;
  version: string;
  status: "training" | "trained" | "deployed" | "archived" | "failed";
  is_active: boolean;
  feature_names?: string[];
  hyperparameters?: Record<string, any>;
  test_split?: number;
  notes?: string;
  created_at: string;
  metrics: ModelMetric[];
}

export interface ModelMetric {
  split: "train" | "test" | "validation";
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  roc_auc?: number;
  confusion_matrix?: number[][];
  feature_importances?: Record<string, number>;
}

export interface Prediction {
  id: string;
  customer_id?: string;
  model_id?: string;
  churn_probability: number;
  churn_prediction: boolean;
  risk_level: "low" | "medium" | "high" | "critical";
  prediction_threshold: number;
  mode?: string;
  created_at: string;
  explanation?: PredictionExplanation;
  recommendations: Recommendation[];
}

export interface PredictionFactor {
  feature: string;
  value: any;
  shap_value: number;
  direction: "positive" | "negative";
  description: string;
}

export interface PredictionExplanation {
  top_risk_factors: PredictionFactor[];
  top_protective_factors: PredictionFactor[];
  base_value?: number;
  explanation_method: string;
}

export interface Recommendation {
  id: string;
  category: string;
  title: string;
  description: string;
  rationale?: string;
  priority: number;
}

export interface Customer {
  id: string;
  external_id?: string;
  name?: string;
  email?: string;
  tenure?: number;
  contract_type?: string;
  monthly_charges?: number;
  total_charges?: number;
  payment_method?: string;
  services?: string[];
  churn_label?: boolean;
  created_at: string;
  latest_prediction?: Prediction;
  prediction_history?: Prediction[];
}

export interface OverviewAnalytics {
  total_customers: number;
  customers_at_risk: number;
  predicted_churners: number;
  average_churn_probability: number;
  retention_opportunity_count: number;
  active_model_accuracy?: number;
  active_model_precision?: number;
  active_model_recall?: number;
  active_model_f1?: number;
  active_model_roc_auc?: number;
  active_model_name?: string;
}

export interface ChurnTrendPoint {
  period: string;
  churn_rate: number;
  total: number;
  churned: number;
}

export interface SegmentAnalytics {
  by_contract: Array<{ contract_type: string; total: number; churned: number; churn_rate: number }>;
  by_tenure_group: Array<{ tenure_group: string; total: number; churn_rate: number }>;
  by_payment_method: Array<{ payment_method: string; total: number; churned: number; churn_rate: number }>;
  risk_distribution: Array<{ risk_level: string; count: number }>;
}

export interface Report {
  id: string;
  title: string;
  report_type: string;
  content?: Record<string, any>;
  created_at: string;
}
