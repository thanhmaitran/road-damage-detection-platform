import importlib.util
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("inv", ROOT / "scripts/build_dataset_inventory.py")
inv = importlib.util.module_from_spec(spec); spec.loader.exec_module(inv)
from ml.src.data.split_manifest import make_manifest  # noqa: E402
from ml.src.data.validation import box_is_valid  # noqa: E402

XML = "<annotation><size><width>100</width><height>80</height></size><object><name>D40</name><bndbox><xmin>10</xmin><ymin>10</ymin><xmax>{x}</xmax><ymax>50</ymax></bndbox></object></annotation>"


def make(root, n=10, bad=()):
    for i in range(n):
        d = root / "Japan/train"
        (d / "images").mkdir(parents=True, exist_ok=True)
        (d / "annotations/xmls").mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (100, 80)).save(d / f"images/a{i}.jpg")
        (d / f"annotations/xmls/a{i}.xml").write_text(XML.format(x=999 if i in bad else 60))


def test_inventory_pairs_separate_dirs_and_flags_oob(tmp_path):
    make(tmp_path, 4, bad={1})
    df = inv.build(tmp_path)
    assert len(df) == 4 and (df.annotation_path != "").all()
    assert int((df.n_out_of_bounds > 0).sum()) == 1


def test_corrupt_image_is_reported(tmp_path):
    make(tmp_path, 1)
    (tmp_path / "Japan/train/images/bad.jpg").write_bytes(b"junk")
    assert "image_corrupt" in set(inv.build(tmp_path).status)


def test_split_excludes_bad_and_is_reproducible(tmp_path):
    make(tmp_path, 20, bad={3})
    df = inv.build(tmp_path)
    m1, m2 = make_manifest(df, seed=7), make_manifest(df, seed=7)
    assert m1.equals(m2) and len(m1) == 19
    assert set(m1.split) == {"train", "val", "test"}


def test_box_validity():
    assert box_is_valid((0, 0, 10, 10), 10, 10)
    assert not box_is_valid((5, 5, 5, 9), 10, 10)
    assert not box_is_valid((0, 0, 11, 10), 10, 10)
