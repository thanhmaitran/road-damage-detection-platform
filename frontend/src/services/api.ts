import type { ClassesResponse, DetectionPage, DetectionResult, ModelInfo, ModelMetrics, Summary } from "../types/detection";

const BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}/api/v1${path}`, init);
  } catch {
    throw new ApiError("Cannot reach the backend. Is it running?", 0);
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try { const b = await res.json(); if (typeof b.detail === "string") detail = b.detail; } catch { /* ignore */ }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; model_ready: boolean }>("/health"),
  model: () => request<ModelInfo>("/model"),
  metrics: () => request<ModelMetrics>("/model/metrics"),
  detect(file: File) {
    const fd = new FormData();
    fd.append("file", file);
    return request<DetectionResult>("/detections", { method: "POST", body: fd });
  },
  history: (page = 1, pageSize = 20) => request<DetectionPage>(`/detections?page=${page}&page_size=${pageSize}`),
  summary: () => request<Summary>("/analytics/summary"),
  classes: () => request<ClassesResponse>("/analytics/classes"),
};
