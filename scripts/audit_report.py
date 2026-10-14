"""Summarise inventory CSV into docs/DATA_AUDIT.md (numbers come from your data)."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
inv = pd.read_csv(ROOT / "data/interim/dataset_inventory.csv").fillna("")
lab = inv[inv["annotation_path"] != ""]
cls = lab["classes"].str.split(";").explode()
lines = ["# Data audit (auto-generated)", "",
         f"- Images found: {len(inv)}", f"- Images with annotation: {len(lab)}", "",
         "## Status", inv["status"].value_counts().to_markdown(), "",
         "## Images per group", inv.groupby("group").size().to_markdown(), "",
         "## Labeled images per class", cls[cls != ""].value_counts().to_markdown(), "",
         "## Anomalies",
         f"- size_mismatch: {int(lab['size_mismatch'].sum())}",
         f"- images with out-of-bounds boxes: {int((lab['n_out_of_bounds'] > 0).sum())}",
         f"- invalid boxes: {int(lab['n_invalid_boxes'].sum())}"]
out = ROOT / "docs/DATA_AUDIT.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out)
