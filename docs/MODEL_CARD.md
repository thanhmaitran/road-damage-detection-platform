# Model Card — baseline-001

- **Architecture:** torchvision Faster R-CNN ResNet50-FPN, COCO-pretrained, new 4-class head.
- **Intended use:** research/portfolio demonstration of road damage detection on road images.
- **Not intended for:** safety-critical decisions, maintenance prioritisation, or counting damage across a road network.
- **Training data:** train split from `data/splits/manifest.csv` (RDD2022), config in `ml/configs/baseline.json`.
- **Selection:** best epoch by validation mAP@0.5; test split touched once for the final report.

## Results
_Not yet measured._ Run `python -m ml.src.evaluation.evaluate --split val` (and `--split test` once at the end), then paste the numbers from `artifacts/evaluation/metrics.json` here with the date, split size and hardware.

## Error analysis
_Run `python -m ml.src.evaluation.error_analysis` and summarise false positives, misses, class confusions._

## Limitations
Fill in after evaluation. Expected areas to check: small/thin cracks, shadows and road markings as false positives, domain shift between countries, near-duplicate leakage across splits.
