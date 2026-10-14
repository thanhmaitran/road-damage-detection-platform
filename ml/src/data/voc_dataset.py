import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
from PIL import Image


def load_classes(path) -> dict:
    """{code: readable_name}. Label ids start at 1 (0 = background)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def class_ids(classes: dict) -> dict:
    return {code: i + 1 for i, code in enumerate(classes)}


def parse_voc(xml_path: Path, code_to_id: dict):
    root = ET.parse(xml_path).getroot()
    boxes, labels = [], []
    for obj in root.findall("object"):
        code = (obj.findtext("name") or "").strip()
        if code not in code_to_id:
            continue  # unmapped classes are skipped; the audit should surface them
        b = obj.find("bndbox")
        boxes.append([float(b.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")])
        labels.append(code_to_id[code])
    return boxes, labels


class VOCDataset:
    """Torch-style dataset over a split manifest -> (image, target)."""

    def __init__(self, manifest, split, data_root, classes_file, transforms=None, max_images=None):
        df = pd.read_csv(manifest)
        df = df[df["split"] == split].reset_index(drop=True)
        if max_images:
            df = df.iloc[:max_images]
        self.df, self.root, self.transforms = df, Path(data_root), transforms
        self.classes = load_classes(classes_file)
        self.code_to_id = class_ids(self.classes)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        import torch
        r = self.df.iloc[i]
        img = Image.open(self.root / r["image_path"]).convert("RGB")
        boxes, labels = parse_voc(self.root / r["annotation_path"], self.code_to_id)
        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor(i),
        }
        if self.transforms:
            img, target = self.transforms(img, target)
        return img, target
