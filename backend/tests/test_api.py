from tests.conftest import FakeDetector, png_bytes


def up(client, data, name="x.png", ctype="image/png"):
    return client.post("/api/v1/detections", files={"file": (name, data, ctype)})


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_detect_and_history(client):
    r = up(client, png_bytes())
    assert r.status_code == 201
    body = r.json()
    assert body["image_width"] == 64 and body["detections"][0]["class_name"] == "pothole"
    assert client.get(f"/api/v1/detections/{body['id']}").json()["id"] == body["id"]
    page = client.get("/api/v1/detections").json()
    assert page["total"] == 1


def test_no_detections_is_valid(make_client):
    with make_client(FakeDetector(dets=[])) as c:
        r = up(c, png_bytes())
        assert r.status_code == 201 and r.json()["detections"] == []
        assert c.get("/api/v1/analytics/summary").json()["images_without_detections"] == 1


def test_rejects_non_image(client):
    assert up(client, b"not an image", "a.png").status_code == 400


def test_rejects_wrong_format_even_with_image_mime(client):
    assert up(client, png_bytes(fmt="GIF"), "a.png", "image/png").status_code == 415


def test_rejects_too_large(make_client):
    with make_client(max_upload_bytes=10) as c:
        assert up(c, png_bytes((200, 200))).status_code == 413


def test_rejects_huge_dimensions(make_client):
    with make_client(max_image_pixels=100) as c:
        assert up(c, png_bytes((64, 48))).status_code == 413


def test_model_not_ready_returns_503(make_client):
    d = FakeDetector(); d.ready = False
    with make_client(d) as c:
        assert up(c, png_bytes()).status_code == 503


def test_unknown_id_404(client):
    assert client.get("/api/v1/detections/nope").status_code == 404


def test_analytics_classes(client):
    up(client, png_bytes())
    out = client.get("/api/v1/analytics/classes").json()
    assert out["classes"][0]["class_code"] == "D40" and out["classes"][0]["count"] == 1


def test_metrics_404_when_missing(client):
    assert client.get("/api/v1/model/metrics").status_code == 404
