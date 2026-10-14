"""Phase 1: build an inventory of images + Pascal VOC annotations.

Handles both layouts: annotation next to image, or separate
`images/` and `annotations/xmls/` folders (RDD2022 uses the latter).
Pairing is done by file stem, never by guessing from names.

Usage: python scripts/build_dataset_inventory.py [--root data/raw/RDD2022]
"""
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
IMG_EXT = {".jpg", ".jpeg", ".png"}


def read_annotation(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    size = root.find("size")
    w = int(float(size.findtext("width", "0"))) if size is not None else 0
    h = int(float(size.findtext("height", "0"))) if size is not None else 0
    boxes, invalid = [], 0
    for obj in root.findall("object"):
        label = (obj.findtext("name") or "unknown").strip()
        b = obj.find("bndbox")
        try:
            coords = [float(b.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")]
        except (AttributeError, TypeError, ValueError):
            invalid += 1
            continue
        boxes.append((label, *coords))
    return {"xml_w": w, "xml_h": h, "boxes": boxes, "invalid_boxes": invalid}


def group_of(path: Path, root: Path) -> str:
    rel = path.relative_to(root).parts
    return rel[0] if len(rel) > 1 else "unknown"


def build(root: Path) -> pd.DataFrame:
    images = [p for p in root.rglob("*") if p.suffix.lower() in IMG_EXT]
    xmls = {}
    for p in root.rglob("*.xml"):
        xmls.setdefault(p.stem, []).append(p)
    rows = []
    for img in sorted(images):
        row = {"image_path": str(img.relative_to(root)), "group": group_of(img, root),
               "annotation_path": "", "status": "ok", "width": 0, "height": 0,
               "n_boxes": 0, "n_invalid_boxes": 0, "n_out_of_bounds": 0,
               "size_mismatch": False, "classes": ""}
        try:
            with Image.open(img) as im:
                row["width"], row["height"] = im.size
        except (UnidentifiedImageError, OSError):
            row["status"] = "image_corrupt"
            rows.append(row)
            continue
        cands = [x for x in xmls.get(img.stem, []) if x.parent.parent == img.parent.parent]
        cands = cands or xmls.get(img.stem, [])
        if not cands:
            row["status"] = "no_annotation"  # normal for the unlabeled test set
            rows.append(row)
            continue
        xml = cands[0]
        row["annotation_path"] = str(xml.relative_to(root))
        try:
            ann = read_annotation(xml)
        except ET.ParseError:
            row["status"] = "annotation_corrupt"
            rows.append(row)
            continue
        W, H = row["width"], row["height"]
        row["n_boxes"] = len(ann["boxes"])
        row["n_invalid_boxes"] = ann["invalid_boxes"]
        row["size_mismatch"] = (ann["xml_w"], ann["xml_h"]) != (W, H)
        # 0 <= xmin < xmax <= W and 0 <= ymin < ymax <= H
        row["n_out_of_bounds"] = sum(
            not (0 <= x0 < x1 <= W and 0 <= y0 < y1 <= H) for _, x0, y0, x1, y1 in ann["boxes"])
        row["classes"] = ";".join(sorted({b[0] for b in ann["boxes"]}))
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT / "data/raw/RDD2022")
    ap.add_argument("--out", type=Path, default=ROOT / "data/interim/dataset_inventory.csv")
    a = ap.parse_args()
    df = build(a.root)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(f"{len(df)} images -> {a.out}")
    if len(df):
        print(df["status"].value_counts().to_string())
        print(df.groupby("group").size().to_string())


if __name__ == "__main__":
    main()
