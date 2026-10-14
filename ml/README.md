# ML pipeline
Run from the repository root with the venv active (`pip install torch torchvision torchmetrics pycocotools pandas pillow`).

```
python scripts/build_dataset_inventory.py
python scripts/audit_report.py
python -m ml.src.data.split_manifest --seed 42
python ml/scripts/visualize_annotations.py          # LOOK at the images before training
python -m ml.src.training.train --config ml/configs/baseline.json
python -m ml.src.evaluation.evaluate --split val
python -m ml.src.evaluation.error_analysis --split val
python -m ml.src.evaluation.evaluate --split test   # once, at the very end
```
Start with the small `max_train_images` in `baseline.json` to check the pipeline; raise it (or set null) for a real run. CPU training is very slow; use a GPU for full runs.

Configs: `baseline.json` (500 images, pipeline check), `full.json` (all training images, 10 epochs, needs GPU). Synthetic end-to-end check: `python ml/scripts/smoke_test.py`.
