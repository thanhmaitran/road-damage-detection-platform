"""python ml/scripts/predict_image.py path/to/img.jpg [--checkpoint ...] [--score 0.5]"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import torch  # noqa: E402
import torchvision.transforms.functional as F  # noqa: E402
from PIL import Image  # noqa: E402
from ml.src.training.checkpoint import load_checkpoint  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("image")
ap.add_argument("--checkpoint", default=str(ROOT / "artifacts/checkpoints/best.pt"))
ap.add_argument("--score", type=float, default=0.5)
a = ap.parse_args()
model, ck = load_checkpoint(a.checkpoint)
names = list(ck["classes"].values())
with torch.no_grad():
    out = model([F.to_tensor(Image.open(a.image).convert("RGB"))])[0]
for b, l, s in zip(out["boxes"], out["labels"], out["scores"]):
    if s >= a.score:
        print(names[int(l) - 1], f"{float(s):.2f}", [round(float(x)) for x in b])
