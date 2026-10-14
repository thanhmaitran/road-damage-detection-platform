import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import Settings
from app.inference.detector import RawDetection
from app.main import create_app
from app.repositories.db import make_session_factory


class FakeDetector:
    """TEST DOUBLE ONLY: lets API tests run without torch/checkpoint. Never used by the real app."""
    ready, version = True, "test-0"
    classes = {"D00": "longitudinal_crack", "D10": "transverse_crack", "D20": "alligator_crack", "D40": "pothole"}

    def __init__(self, dets=None):
        self.dets = [RawDetection(4, 0.9, (10, 10, 50, 40))] if dets is None else dets

    def predict(self, image, thr):
        return self.dets, 1.5


def png_bytes(size=(64, 48), fmt="PNG"):
    b = io.BytesIO()
    Image.new("RGB", size, "gray").save(b, fmt)
    return b.getvalue()


@pytest.fixture
def make_client():
    def _make(detector=None, **over):
        s = Settings(database_url="sqlite://", **over)
        app = create_app(s, detector or FakeDetector(), make_session_factory("sqlite://"))
        return TestClient(app)
    return _make


@pytest.fixture
def client(make_client):
    with make_client() as c:
        yield c
