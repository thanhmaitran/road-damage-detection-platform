# API (prefix `/api/v1`)

| Method | Path | Notes |
|---|---|---|
| GET | /health | `{status, model_ready}` |
| GET | /model | version, class map, readiness |
| GET | /model/metrics | contents of `artifacts/evaluation/metrics.json`; 404 if not evaluated |
| POST | /detections | multipart field `file` (JPEG/PNG). 201 result; 400 invalid image; 413 too large; 415 wrong format; 503 model not loaded |
| GET | /detections?page=&page_size= | history, newest first |
| GET | /detections/{id} | one analysis; 404 if unknown |
| GET | /analytics/summary | totals, daily counts, mean inference ms |
| GET | /analytics/classes | per-class counts and confidences |

Interactive docs at `/docs` when the backend runs. Uploaded images are validated in memory and never stored; only metadata and boxes are saved.
