# Testing
- `pytest` at repo root: data pipeline (inventory pairing, bad boxes, corrupt images, reproducible split).
- `cd backend && pytest`: API (valid upload, corrupt/oversized/wrong-format files, 503 without model, history, analytics). Uses a test double detector so no torch/checkpoint is needed.
- `cd frontend && npm test`: box scaling math.
- Not covered yet: real-checkpoint integration test, browser end-to-end test.
