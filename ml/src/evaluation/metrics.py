"""Detection metrics via torchmetrics (COCO-style matching by class, IoU and confidence)."""


def detection_metrics(preds, gts, class_metrics=True):
    from torchmetrics.detection.mean_ap import MeanAveragePrecision
    m = MeanAveragePrecision(box_format="xyxy", iou_type="bbox", class_metrics=class_metrics)
    m.update(preds, gts)
    r = m.compute()
    out = {"map": float(r["map"]), "map50": float(r["map_50"]), "map75": float(r["map_75"]),
           "mar_100": float(r["mar_100"])}
    if class_metrics and r["map_per_class"].numel() > 1:
        out["map_per_class"] = [float(x) for x in r["map_per_class"]]
        out["classes"] = [int(x) for x in r["classes"]]
    return out
