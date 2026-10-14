# Data Card — RDD2022

| Field | Value |
|---|---|
| Source | Figshare record 21431547 (CRDDC'2022, IEEE BigData Cup) |
| Content | 47,420 road images, 6 countries, >55,000 annotated damage instances (per the Figshare page) |
| Classes | D00 longitudinal crack, D10 transverse crack, D20 alligator crack, D40 pothole |
| Annotation format | Pascal VOC XML (train); test images unlabeled |
| License | **TO VERIFY.** The Figshare page text fetched when this repo was generated did not display a license. Check the license field on the live page and the official RoadDamageDetector repo before publishing or redistributing any images. Do not commit images to this repo. |

## Verified by you (fill in after running the audit)
- [ ] Archive structure matches `scripts/build_dataset_inventory.py` assumptions (images/xml pairing by stem).
- [ ] Class codes in XML match `ml/configs/classes.json` (see docs/DATA_AUDIT.md).
- [ ] Counts of corrupt images / bad boxes / size mismatches: _from DATA_AUDIT.md_

## Splits
Per-country random split, seed 42, 70/15/15, from labelled & valid images only. Limitation: no source/sequence ids are provided, so near-duplicate frames may land in different splits and inflate scores.

## Known limitations
Geographic and camera bias (6 countries, dashcam/smartphone style imagery); class imbalance; label noise in crack boundaries.
