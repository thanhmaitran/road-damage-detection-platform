"""Verify the whole ML pipeline end-to-end on a tiny SYNTHETIC dataset (no pretrained download).
This only proves the code runs; the resulting numbers mean nothing.
    python ml/scripts/smoke_test.py
"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def build(root: Path, n=24):
    random.seed(0)
    rows = ["image_path,annotation_path,group,split"]
    (root / "G/train/images").mkdir(parents=True)
    (root / "G/train/annotations/xmls").mkdir(parents=True)
    for i in range(n):
        im = Image.new("RGB", (160, 120), "gray")
        x0, y0 = random.randint(10, 60), random.randint(10, 40)
        ImageDraw.Draw(im).rectangle([x0, y0, x0 + 50, y0 + 40], fill="black")
        im.save(root / f"G/train/images/i{i}.jpg")
        (root / f"G/train/annotations/xmls/i{i}.xml").write_text(
            f"<annotation><size><width>160</width><height>120</height></size><object><name>D40</name>"
            f"<bndbox><xmin>{x0}</xmin><ymin>{y0}</ymin><xmax>{x0 + 50}</xmax><ymax>{y0 + 40}</ymax></bndbox></object></annotation>")
        split = "train" if i < 16 else ("val" if i < 20 else "test")
        rows.append(f"G/train/images/i{i}.jpg,G/train/annotations/xmls/i{i}.xml,G,{split}")
    (root / "manifest.csv").write_text("\n".join(rows))


def main():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        build(d)
        cfg = json.loads((ROOT / "ml/configs/baseline.json").read_text())
        cfg.update(epochs=2, pretrained=False, min_size=120, max_size=160, manifest=str(d / "manifest.csv"),
                   checkpoint_dir=str(d / "ckpt"), max_train_images=16, max_val_images=4)
        (d / "cfg.json").write_text(json.dumps(cfg))
        env_py = [sys.executable, "-m"]
        run = lambda *a: subprocess.run(env_py + list(a), cwd=ROOT, check=True)  # noqa: E731
        run("ml.src.training.train", "--config", str(d / "cfg.json"), "--data-root", str(d))
        run("ml.src.evaluation.evaluate", "--checkpoint", str(d / "ckpt/best.pt"), "--manifest", str(d / "manifest.csv"),
            "--data-root", str(d), "--split", "val", "--out", str(d / "m.json"))
        run("ml.src.evaluation.error_analysis", "--checkpoint", str(d / "ckpt/best.pt"), "--manifest", str(d / "manifest.csv"),
            "--data-root", str(d), "--out", str(d / "e.json"))
        assert (d / "m.json").exists() and (d / "e.json").exists()
        print("SMOKE TEST OK: train -> checkpoint -> evaluate -> error analysis all ran.")


if __name__ == "__main__":
    main()
