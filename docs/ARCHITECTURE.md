# Architecture

RDD2022 → inventory/audit → split manifest → training (PyTorch) → checkpoint + evaluation JSON → FastAPI (loads checkpoint once) → React frontend (renders only backend output).

- `ml/` is independent of the web app; the backend imports only the checkpoint loader.
- Detection history (SQLite locally, PostgreSQL in Docker) is separate from benchmark results (`metrics.json`), so usage statistics are never mistaken for model quality.
- If no checkpoint exists the API answers 503 rather than returning fabricated detections.
