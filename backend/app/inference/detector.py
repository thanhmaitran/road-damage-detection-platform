"""Loads the checkpoint ONCE and runs inference. Never returns fabricated detections."""
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image


@dataclass
class RawDetection:
    class_id: int
    confidence: float
    box: tuple  # xmin, ymin, xmax, ymax in original image pixels


class Detector(Protocol):
    ready: bool
    version: str
    classes: dict  # code -> name

    def predict(self, image: Image.Image, score_threshold: float) -> tuple[list[RawDetection], float]: ...


class TorchDetector:
    def __init__(self, checkpoint: Path, version: str, classes_file: Path):
        self.version, self.ready, self.epoch = version, False, None
        self.classes = json.loads(Path(classes_file).read_text(encoding="utf-8"))
        self._model = None
        self._ckpt = Path(checkpoint)

    def load(self):
        if not self._ckpt.exists():
            return  # stays not-ready -> API answers 503
        import sys
        import torch
        sys.path.insert(0, str(self._ckpt.resolve().parents[2]))  # repo root, for ml.* imports
        from ml.src.training.checkpoint import load_checkpoint
        self._torch = torch
        self._model, ck = load_checkpoint(str(self._ckpt), "cpu")
        self.epoch = ck.get("epoch")
        self.classes = ck["classes"]
        self.ready = True

    def predict(self, image, score_threshold):
        import torchvision.transforms.functional as F
        t = time.perf_counter()
        with self._torch.no_grad():
            out = self._model([F.to_tensor(image.convert("RGB"))])[0]
        ms = (time.perf_counter() - t) * 1000
        res = [RawDetection(int(l), float(s), tuple(float(x) for x in b))
               for b, l, s in zip(out["boxes"], out["labels"], out["scores"]) if s >= score_threshold]
        return res, ms
