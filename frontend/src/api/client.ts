import axios from "axios";
import type {
  ExplainResponse,
  FeedstockInput,
  FullPredictionResponse,
  ModelComparisonResponse,
  ModelInfo,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE_URL });

export async function predict(feedstock: FeedstockInput, model_name = "best") {
  const { data } = await api.post<FullPredictionResponse>("/predict", {
    feedstock,
    model_name,
  });
  return data;
}

export async function compareModels(feedstock: FeedstockInput) {
  const { data } = await api.post<ModelComparisonResponse>("/compare-models", {
    feedstock,
  });
  return data;
}

export async function explain(feedstock: FeedstockInput, model_name = "best") {
  const { data } = await api.post<ExplainResponse>("/explain", {
    feedstock,
    model_name,
  });
  return data;
}

export async function listModels() {
  const { data } = await api.get<{ models: ModelInfo[] }>("/models");
  return data.models;
}

export async function featureRanges() {
  const { data } = await api.get<Record<string, { min: number; max: number }>>(
    "/feature-ranges"
  );
  return data;
}

export async function batchPredict(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/batch-predict", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export function batchPredictDownloadUrl() {
  return `${API_BASE_URL}/batch-predict/download`;
}

export async function exportPdf(feedstock: FeedstockInput, model_name = "best") {
  const response = await api.post(
    "/export/pdf",
    { feedstock, model_name },
    { responseType: "blob" }
  );
  return response.data as Blob;
}
