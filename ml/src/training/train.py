"""Fine-tune the baseline detector. Usage (repo root):
    python -m ml.src.training.train --config ml/configs/baseline.json
"""
import argparse
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def collate(b):
    return tuple(zip(*b))


def main():
    import numpy as np
    import torch
    from torch.utils.data import DataLoader
    from ml.src.data.transforms import eval_transforms, train_transforms
    from ml.src.data.voc_dataset import VOCDataset
    from ml.src.evaluation.evaluate import evaluate_model
    from ml.src.models.detector import build_detector
    from ml.src.training.checkpoint import save_checkpoint

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "ml/configs/baseline.json"))
    ap.add_argument("--data-root", default=str(ROOT / "data/raw/RDD2022"))
    ap.add_argument("--classes", default=str(ROOT / "ml/configs/classes.json"))
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())

    random.seed(cfg["seed"]); np.random.seed(cfg["seed"]); torch.manual_seed(cfg["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    manifest = ROOT / cfg["manifest"]
    train_ds = VOCDataset(manifest, "train", a.data_root, a.classes, train_transforms(), cfg.get("max_train_images"))
    val_ds = VOCDataset(manifest, "val", a.data_root, a.classes, eval_transforms(), cfg.get("max_val_images"))
    train_dl = DataLoader(train_ds, batch_size=cfg["batch_size"], shuffle=True,
                          num_workers=cfg["num_workers"], collate_fn=collate)

    model = build_detector(len(train_ds.classes), cfg["pretrained"], cfg["min_size"], cfg["max_size"]).to(device)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=cfg["learning_rate"])
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=max(1, cfg["epochs"] // 2), gamma=0.1)

    ckpt_dir = ROOT / cfg["checkpoint_dir"]
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    history, best = [], -1.0
    for epoch in range(1, cfg["epochs"] + 1):
        model.train()
        t0, total = time.time(), 0.0
        for imgs, targets in train_dl:
            imgs = [i.to(device) for i in imgs]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            loss = sum(model(imgs, targets).values())
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item()
        sched.step()
        res = evaluate_model(model, val_ds, device)
        row = {"epoch": epoch, "train_loss": total / max(1, len(train_dl)),
               "val_map50": res["map50"], "val_map": res["map"], "seconds": time.time() - t0}
        history.append(row)
        print(row)
        save_checkpoint(ckpt_dir / f"epoch_{epoch}.pt", model, cfg, train_ds.classes, epoch, res["map50"])
        if res["map50"] > best:  # model selection uses VALIDATION only, never test
            best = res["map50"]
            save_checkpoint(ckpt_dir / "best.pt", model, cfg, train_ds.classes, epoch, best)
    (ckpt_dir / "training_history.json").write_text(json.dumps(history, indent=2))


if __name__ == "__main__":
    main()
