"""Download RDD2022 from Figshare (article 21431547) via the public Figshare API, verify MD5, extract.

    python scripts/download_rdd2022.py [--dest data/raw] [--no-extract]

Check the dataset license on the Figshare page BEFORE using or redistributing the data.
"""
import argparse
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

ARTICLE = 21431547
API = f"https://api.figshare.com/v2/articles/{ARTICLE}"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=Path(__file__).resolve().parents[1] / "data/raw")
    ap.add_argument("--no-extract", action="store_true")
    a = ap.parse_args()
    a.dest.mkdir(parents=True, exist_ok=True)
    meta = json.load(urllib.request.urlopen(API))
    lic = meta.get("license", {})
    print("License reported by Figshare:", lic.get("name"), lic.get("url"))
    (a.dest / "figshare_metadata.json").write_text(json.dumps(meta, indent=2))
    for f in meta["files"]:
        out = a.dest / f["name"]
        if out.exists() and md5(out) == f.get("computed_md5"):
            print("ok (already downloaded):", f["name"])
        else:
            print(f"downloading {f['name']} ({f['size'] / 1e9:.2f} GB) ...")
            urllib.request.urlretrieve(f["download_url"], out)
            if f.get("computed_md5") and md5(out) != f["computed_md5"]:
                raise SystemExit(f"MD5 mismatch for {f['name']}")
        if not a.no_extract and out.suffix == ".zip":
            target = a.dest / "RDD2022"
            print("extracting to", target)
            with zipfile.ZipFile(out) as z:
                z.extractall(target)
    print("done. Now run scripts/build_dataset_inventory.py (check the folder layout first).")


if __name__ == "__main__":
    main()
