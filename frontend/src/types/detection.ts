export interface Box { xmin: number; ymin: number; xmax: number; ymax: number }
export interface DetectionItem {
  class_id: number; class_code: string; class_name: string; confidence: number; box: Box;
}
export interface DetectionResult {
  id: string; created_at: string; model_version: string; image_width: number; image_height: number;
  inference_ms: number; status: string; detections: DetectionItem[];
}
export interface DetectionPage { items: DetectionResult[]; total: number; page: number; page_size: number }
export interface ModelInfo { version: string; ready: boolean; classes: Record<string, string>; checkpoint_epoch?: number }
export interface Summary {
  total_images: number; total_detections: number; avg_inference_ms: number | null;
  images_without_detections: number; daily: { date: string; count: number }[]; scope_note: string;
}
export interface ClassStat { class_id: number; class_code: string; class_name: string; count: number; avg_confidence: number }
export interface ClassesResponse { classes: ClassStat[]; confidences: number[] }
export interface ModelMetrics {
  model_version: string; split: string; n_images: number; evaluated_at: string; score_threshold: number;
  metrics: { map: number; map50: number; map75: number; mar_100: number; per_class?: Record<string, number> };
  latency_ms: { mean: number; device: string; warmup: number; note: string };
  env: Record<string, string>;
}
