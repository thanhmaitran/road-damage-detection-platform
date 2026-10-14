from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Box(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class DetectionItem(BaseModel):
    class_id: int
    class_code: str
    class_name: str
    confidence: float
    box: Box


class DetectionResult(BaseModel):
    id: str
    created_at: datetime
    model_version: str
    image_width: int
    image_height: int
    inference_ms: float
    status: str = "success"
    detections: list[DetectionItem]


class DetectionPage(BaseModel):
    items: list[DetectionResult]
    total: int
    page: int
    page_size: int


class ModelInfo(BaseModel):
    version: str
    ready: bool
    classes: dict[str, str]
    checkpoint_epoch: Optional[int] = None
