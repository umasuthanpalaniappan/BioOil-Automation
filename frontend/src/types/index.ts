export interface FeedstockInput {
  Cel: number;
  Hem: number;
  Lig: number;
  VM: number;
  Ash: number;
  FC: number;
  "C%": number;
  "H%": number;
  "O%": number;
  "N%": number;
  Size: number;
  HR: number;
  PT: number;
  Temp?: number | null;
}

export interface ConstraintFlag {
  field: string;
  message: string;
  severity: "warning" | "error";
}

export interface DriftFlag {
  field: string;
  value: number;
  training_min: number;
  training_max: number;
  message: string;
}

export interface SecondaryPredictions {
  "H/C"?: number | null;
  Cal_value?: number | null;
  Oil_yield?: number | null;
}

export interface FullPredictionResponse {
  target: string;
  prediction: number;
  confidence_interval_95?: [number, number] | null;
  model_used: string;
  physics_flags: ConstraintFlag[];
  drift_flags: DriftFlag[];
  secondary?: SecondaryPredictions;
}

export interface ModelComparisonResponse {
  feedstock: FeedstockInput;
  predictions: Record<string, number>;
  confidence_intervals: Record<string, [number, number] | null>;
}

export interface ExplanationItem {
  feature: string;
  value: number;
  shap_value: number;
  plain_language: string;
}

export interface ExplainResponse {
  prediction: number;
  base_value: number;
  top_features: ExplanationItem[];
  summary: string;
}

export interface ModelInfo {
  name: string;
  target: string;
  cv_r2?: number | null;
  test_r2?: number | null;
  test_rmse?: number | null;
  test_mae?: number | null;
}

export const DEFAULT_FEEDSTOCK: FeedstockInput = {
  Cel: 38,
  Hem: 27,
  Lig: 24,
  VM: 74,
  Ash: 4,
  FC: 16,
  "C%": 49,
  "H%": 6,
  "O%": 42,
  "N%": 1,
  Size: 0.75,
  HR: 20,
  PT: 500,
  Temp: 40,
};
