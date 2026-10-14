# Data

Source: RDD2022 (CRDDC'2022), https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
(4 files on Figshare; 47,420 images from Japan, India, Czech Republic, Norway, United States, China; 4 damage classes.)

## How to reproduce
1. Download the archives from Figshare **manually in your browser** and put them in `data/raw/`.
2. Extract into `data/raw/RDD2022/` (do not edit or rename files).
3. `python scripts/build_dataset_inventory.py`  -> `data/interim/dataset_inventory.csv`
4. `python scripts/audit_report.py`              -> `docs/DATA_AUDIT.md`
5. `python -m ml.src.data.split_manifest --seed 42` -> `data/splits/manifest.csv`

Only labelled images are used for train/val/test. The official test images ship without labels and are never used for metrics.
