"""Match predictions to GT (IoU>=0.5) and export FP/FN/confusion stats.
    python -m ml.src.evaluation.error_analysis --split val --max-images 200
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def analyse(preds, gts, iou_thr=0.5, score_thr=0.5):
    import torch
    from torchvision.ops import box_iou
    fp = fn = 0
    confusion, per_image = Counter(), []
    for i, (p, g) in enumerate(zip(preds, gts)):
        keep = p["scores"] >= score_thr
        pb, pl = p["boxes"][keep], p["labels"][keep]
        gb = g["boxes"]
        iou = box_iou(pb, gb) if len(pb) and len(gb) else torch.zeros(len(pb), len(gb))
        used, img_fp = set(), 0
        for pi in range(len(pb)):
            if iou.shape[1] == 0:
                img_fp += 1
                continue
            gi = int(iou[pi].argmax())
            if iou[pi, gi] >= iou_thr and gi not in used:
                used.add(gi)
                if pl[pi] != g["labels"][gi]:
                    confusion[(int(g["labels"][gi]), int(pl[pi]))] += 1
                    img_fp += 1
            else:
                img_fp += 1
        img_fn = len(gb) - len(used)
        fp, fn = fp + img_fp, fn + img_fn
        per_image.append({"idx": i, "fp": img_fp, "fn": img_fn, "n_pred": len(pb)})
    worst = sorted(per_image, key=lambda r: r["fp"] + r["fn"], reverse=True)[:20]
    return {"false_positives": fp, "false_negatives": fn,
            "confusions_gt_pred": {f"{a}->{b}": n for (a, b), n in confusion.items()},
            "worst_images": worst, "iou_threshold": iou_thr, "score_threshold": score_thr}


def main():
    import torch
    from ml.src.data.transforms import eval_transforms
    from ml.src.data.voc_dataset import VOCDataset
    from ml.src.evaluation.evaluate import predict_split
    from ml.src.training.checkpoint import load_checkpoint
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(ROOT / "artifacts/checkpoints/best.pt"))
    ap.add_argument("--manifest", default=str(ROOT / "data/splits/manifest.csv"))
    ap.add_argument("--data-root", default=str(ROOT / "data/raw/RDD2022"))
    ap.add_argument("--classes", default=str(ROOT / "ml/configs/classes.json"))
    ap.add_argument("--split", default="val")
    ap.add_argument("--max-images", type=int, default=200)
    ap.add_argument("--out", default=str(ROOT / "artifacts/evaluation/error_analysis.json"))
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_checkpoint(a.checkpoint, device)
    ds = VOCDataset(a.manifest, a.split, a.data_root, a.classes, eval_transforms(), a.max_images)
    preds, gts, _ = predict_split(model, ds, device)
    res = analyse(preds, gts)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
