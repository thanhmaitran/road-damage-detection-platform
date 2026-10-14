"""Reproducible train/val/test manifest built ONLY from labeled, valid images.

Split is done per country group with a fixed seed. Caveat: RDD2022 provides no
sequence/source ids, so near-duplicate frames may cross splits; document this in MODEL_CARD.
Usage: python -m ml.src.data.split_manifest --seed 42
"""
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def make_manifest(inv: pd.DataFrame, seed=42, val=0.15, test=0.15) -> pd.DataFrame:
    ok = inv[(inv["status"] == "ok") & (inv["annotation_path"].fillna("") != "")
             & (inv["n_invalid_boxes"] == 0) & (inv["n_out_of_bounds"] == 0)
             & (inv["n_boxes"] > 0)].copy()
    parts = []
    for _, g in ok.groupby("group"):
        g = g.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        n = len(g)
        n_test, n_val = int(n * test), int(n * val)
        g["split"] = "train"
        g.loc[: n_test - 1, "split"] = "test"
        g.loc[n_test: n_test + n_val - 1, "split"] = "val"
        parts.append(g)
    out = pd.concat(parts, ignore_index=True)
    return out[["image_path", "annotation_path", "group", "split"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", type=Path, default=ROOT / "data/interim/dataset_inventory.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "data/splits/manifest.csv")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    m = make_manifest(pd.read_csv(a.inventory), seed=a.seed)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    m.to_csv(a.out, index=False)
    print(m.groupby(["group", "split"]).size().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
