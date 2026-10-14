import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.inference.detector import TorchDetector
from app.repositories.db import DetectionRepository, DetectionRow, make_session_factory
from app.schemas.detection import Box, DetectionItem, DetectionPage, DetectionResult, ModelInfo
from app.services.upload import read_image


def to_result(row: DetectionRow, classes: dict) -> DetectionResult:
    codes = list(classes)
    items = []
    for it in row.items:
        i = it.class_id - 1
        items.append(DetectionItem(
            class_id=it.class_id, class_code=codes[i] if 0 <= i < len(codes) else "unknown",
            class_name=classes.get(codes[i], "unknown") if 0 <= i < len(codes) else "unknown",
            confidence=it.confidence, box=Box(xmin=it.xmin, ymin=it.ymin, xmax=it.xmax, ymax=it.ymax)))
    return DetectionResult(id=row.id, created_at=row.created_at, model_version=row.model_version,
                           image_width=row.image_width, image_height=row.image_height,
                           inference_ms=row.inference_ms, status=row.status, detections=items)


def create_app(settings: Settings | None = None, detector=None, session_factory=None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.sessions = session_factory or make_session_factory(settings.database_url)
        if detector is not None:
            app.state.detector = detector
        else:
            d = TorchDetector(settings.model_checkpoint, settings.model_version, settings.classes_file)
            try:
                d.load()  # loaded once at startup, not per request
            except Exception:  # noqa: BLE001 - keep API up; /health reports model state
                d.ready = False
            app.state.detector = d
        yield

    app = FastAPI(title="Road Damage Detection API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False,
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @app.exception_handler(Exception)
    async def unhandled(_: Request, __: Exception):  # no stack traces / paths leak to clients
        return JSONResponse({"detail": "Internal server error"}, status_code=500)

    def repo(request: Request):
        with request.app.state.sessions() as s:
            yield DetectionRepository(s)

    @app.get("/api/v1/health")
    def health(request: Request):
        return {"status": "ok", "model_ready": bool(request.app.state.detector.ready)}

    @app.get("/api/v1/model", response_model=ModelInfo)
    def model_info(request: Request):
        d = request.app.state.detector
        return ModelInfo(version=d.version, ready=d.ready, classes=d.classes,
                         checkpoint_epoch=getattr(d, "epoch", None))

    @app.get("/api/v1/model/metrics")
    def model_metrics():
        p: Path = settings.eval_metrics_file
        if not p.exists():
            raise HTTPException(404, "No evaluation results found. Run ml.src.evaluation.evaluate first.")
        return json.loads(p.read_text())

    @app.post("/api/v1/detections", response_model=DetectionResult, status_code=201)
    async def create_detection(request: Request, file: UploadFile = File(...), r: DetectionRepository = Depends(repo)):
        d = request.app.state.detector
        if not d.ready:
            raise HTTPException(503, "Model is not available. Train or provide a checkpoint first.")
        img = await read_image(file, settings.max_upload_bytes, settings.max_image_pixels)
        dets, ms = d.predict(img, settings.score_threshold)
        from types import SimpleNamespace
        row = r.add(d.version, img.width, img.height, ms,
                    [SimpleNamespace(class_id=x.class_id, confidence=x.confidence, box=x.box) for x in dets])
        return to_result(row, d.classes)

    @app.get("/api/v1/detections", response_model=DetectionPage)
    def list_detections(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        r: DetectionRepository = Depends(repo)):
        rows, total = r.list(page, page_size)
        c = request.app.state.detector.classes
        return DetectionPage(items=[to_result(x, c) for x in rows], total=total, page=page, page_size=page_size)

    @app.get("/api/v1/detections/{det_id}", response_model=DetectionResult)
    def get_detection(det_id: str, request: Request, r: DetectionRepository = Depends(repo)):
        row = r.get(det_id)
        if row is None:
            raise HTTPException(404, "Detection not found")
        return to_result(row, request.app.state.detector.classes)

    @app.get("/api/v1/analytics/summary")
    def analytics_summary(r: DetectionRepository = Depends(repo)):
        return {**r.summary(), "daily": [{"date": d, "count": n} for d, n in r.daily_counts()],
                "scope_note": "Statistics cover only images analysed through this website."}

    @app.get("/api/v1/analytics/classes")
    def analytics_classes(request: Request, r: DetectionRepository = Depends(repo)):
        codes = list(request.app.state.detector.classes)
        names = request.app.state.detector.classes
        out = []
        for cid, n, avg in r.by_class():
            code = codes[cid - 1] if 0 <= cid - 1 < len(codes) else "unknown"
            out.append({"class_id": cid, "class_code": code, "class_name": names.get(code, "unknown"),
                        "count": n, "avg_confidence": avg})
        return {"classes": out, "confidences": r.confidences()}

    return app


app = create_app()
