import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _p(v: str) -> Path:
    p = Path(v)
    return p if p.is_absolute() else REPO_ROOT / p


@dataclass(frozen=True)
class Settings:
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./rdd.db"))
    model_checkpoint: Path = field(default_factory=lambda: _p(os.getenv("MODEL_CHECKPOINT", "artifacts/checkpoints/best.pt")))
    model_version: str = field(default_factory=lambda: os.getenv("MODEL_VERSION", "baseline-001"))
    classes_file: Path = field(default_factory=lambda: _p(os.getenv("CLASSES_FILE", "ml/configs/classes.json")))
    eval_metrics_file: Path = field(default_factory=lambda: _p(os.getenv("EVAL_METRICS_FILE", "artifacts/evaluation/metrics.json")))
    max_upload_bytes: int = field(default_factory=lambda: int(float(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024))
    max_image_pixels: int = field(default_factory=lambda: int(os.getenv("MAX_IMAGE_PIXELS", "25000000")))
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","))
    score_threshold: float = 0.25


def get_settings() -> Settings:
    return Settings()
