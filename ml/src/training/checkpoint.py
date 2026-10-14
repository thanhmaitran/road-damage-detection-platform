from pathlib import Path


def save_checkpoint(path, model, config, classes, epoch, val_map=None, extra=None):
    import torch
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict(), "config": config, "classes": classes,
                "epoch": epoch, "val_map50": val_map, "extra": extra or {}}, path)


def load_checkpoint(path, device="cpu"):
    import torch
    from ml.src.models.detector import build_detector
    ck = torch.load(path, map_location=device, weights_only=False)
    cfg = ck["config"]
    model = build_detector(len(ck["classes"]), pretrained=False,
                           min_size=cfg.get("min_size", 640), max_size=cfg.get("max_size", 1066))
    model.load_state_dict(ck["model_state"])
    return model.to(device).eval(), ck
