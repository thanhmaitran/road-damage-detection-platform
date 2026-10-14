# Road Damage Detection Platform
Full-stack computer vision: PyTorch detector trained on RDD2022, FastAPI backend, React + TypeScript dashboard.

> **Status:** code complete for all phases; dataset download, training and evaluation have to be run on your machine. No metrics are claimed until you produce them (see `docs/MODEL_CARD.md`).

## Features
Detection (upload → boxes, confidence filter, class toggles) · Analytics (history, class/confidence charts) · Model Insights (benchmark from saved evaluation) · Upload validation · Docker Compose · CI.

## Run order (what to do after cloning)
1. `python scripts/download_rdd2022.py` (or download manually from Figshare) and **check the license**.
2. `python scripts/build_dataset_inventory.py` -> `python scripts/audit_report.py` -> `python -m ml.src.data.split_manifest`
3. `python ml/scripts/smoke_test.py` verifies train/eval code on synthetic data (needs torch).
4. Train and evaluate on a GPU: easiest is `notebooks/run_on_gpu.ipynb` (Colab/Kaggle). Local: see `ml/README.md`.
5. Copy `best.pt` to `artifacts/checkpoints/` and `metrics.json` to `artifacts/evaluation/`, then start backend + frontend.

## Quick start
```bash
# 1. data + model  (see ml/README.md and data/README.md)
# 2. backend
python -m venv .venv && source .venv/bin/activate      # Windows: .\.venv\Scripts\Activate.ps1
pip install -e "backend[dev,ml]"
cd backend && uvicorn app.main:app --reload             # http://127.0.0.1:8000/docs
# 3. frontend
cd frontend && cp .env.example .env.local && npm install && npm run dev
```
Without `artifacts/checkpoints/best.pt` the backend runs but `/detections` returns 503 by design.

## Docker
`docker compose config` then `docker compose up --build` (checkpoint mounted from `./artifacts`; set `POSTGRES_PASSWORD`).

## Docs
`docs/DATA_CARD.md` · `docs/MODEL_CARD.md` · `docs/API.md` · `docs/ARCHITECTURE.md` · `docs/TESTING.md`

## Limitations
Predictions are not engineering assessments; analytics reflect only uploaded images; dataset license must be verified before redistribution.

## Acknowledgements
RDD2022 / CRDDC'2022: Arya, Maeda, Sekimoto et al. (Figshare).
