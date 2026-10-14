"""Run inference over a split and compute metrics. Standalone:
    python -m ml.src.evaluation.evaluate --checkpoint artifacts/checkpoints/best.pt --split val
Use --split test ONLY for the final report.
"""
import argparse
import json
import platform
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def predict_split(model, ds, device, score_thr=0.05):
    import torch
    model.eval()
    preds, gts, lat = [], [], []
    with torch.no_grad():
        for i in range(len(ds)):
            img, tgt = ds[i]
            if device == "cuda":
                torch.cuda.synchronize()
            t = time.perf_counter()
            out = model([img.to(device)])[0]
            if device == "cuda":
                torch.cuda.synchronize()
            lat.append((time.perf_counter() - t) * 1000)
            keep = out["scores"] >= score_thr
            preds.append({k: out[k][keep].cpu() for k in ("boxes", "scores", "labels")})
            gts.append({"boxes": tgt["boxes"], "labels": tgt["labels"]})
    return preds, gts, lat


def evaluate_model(model, ds, device):
    from ml.src.evaluation.metrics import detection_metrics
    preds, gts, _ = predict_split(model, ds, device)
    return detection_metrics(preds, gts)


def main():
    import torch
    import torchvision
    from ml.src.data.transforms import eval_transforms
    from ml.src.data.voc_dataset import VOCDataset
    from ml.src.evaluation.metrics import detection_metrics
    from ml.src.training.checkpoint import load_checkpoint

    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(ROOT / "artifacts/checkpoints/best.pt"))
    ap.add_argument("--manifest", default=str(ROOT / "data/splits/manifest.csv"))
    ap.add_argument("--data-root", default=str(ROOT / "data/raw/RDD2022"))
    ap.add_argument("--classes", default=str(ROOT / "ml/configs/classes.json"))
    ap.add_argument("--split", default="val", choices=["val", "test"])
    ap.add_argument("--max-images", type=int, default=None)
    ap.add_argument("--model-version", default="baseline-001")
    ap.add_argument("--out", default=str(ROOT / "artifacts/evaluation/metrics.json"))
    a = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, ck = load_checkpoint(a.checkpoint, device)
    ds = VOCDataset(a.manifest, a.split, a.data_root, a.classes, eval_transforms(), a.max_images)
    with torch.no_grad():
        if len(ds):  # warm-up: latency should exclude first-call overhead
            model([ds[0][0].to(device)])
    preds, gts, lat = predict_split(model, ds, device)
    m = detection_metrics(preds, gts)
    names = list(ds.classes.values())
    if "map_per_class" in m:
        m["per_class"] = {names[c - 1]: v for c, v in zip(m.pop("classes"), m.pop("map_per_class"))}
    result = {
        "model_version": a.model_version, "split": a.split, "n_images": len(ds),
        "evaluated_at": time.strftime("%Y-%m-%d"), "score_threshold": 0.05,
        "metrics": m,
        "latency_ms": {"mean": sum(lat) / max(1, len(lat)), "device": device, "warmup": 1,
                       "note": "per-image forward pass, batch size 1, excludes image decoding"},
        "env": {"python": platform.python_version(), "torch": torch.__version__,
                "torchvision": torchvision.__version__},
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
