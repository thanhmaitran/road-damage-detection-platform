"""Draw ground-truth boxes on N images -> docs/figures/gt_samples/. Do this BEFORE training."""
import argparse
import sys
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ml.src.data.voc_dataset import class_ids, load_classes, parse_voc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=12)
ap.add_argument("--split", default="train")
ap.add_argument("--data-root", default=str(ROOT / "data/raw/RDD2022"))
a = ap.parse_args()
ids = class_ids(load_classes(ROOT / "ml/configs/classes.json"))
inv = {v: k for k, v in ids.items()}
df = pd.read_csv(ROOT / "data/splits/manifest.csv")
df = df[df.split == a.split]
df = df.sample(min(a.n, len(df)), random_state=0)
out = ROOT / "docs/figures/gt_samples"
out.mkdir(parents=True, exist_ok=True)
for _, r in df.iterrows():
    img = Image.open(Path(a.data_root) / r.image_path).convert("RGB")
    d = ImageDraw.Draw(img)
    boxes, labels = parse_voc(Path(a.data_root) / r.annotation_path, ids)
    for b, l in zip(boxes, labels):
        d.rectangle(b, outline="red", width=4)
        d.text((b[0] + 4, b[1] + 4), inv[l], fill="yellow")
    img.save(out / f"{Path(r.image_path).stem}.jpg")
print("saved to", out)
