import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class DetectionRow(Base):
    __tablename__ = "detections"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    model_version: Mapped[str] = mapped_column(String(64))
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    inference_ms: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default="success")
    items: Mapped[list["ItemRow"]] = relationship(back_populates="detection", cascade="all, delete-orphan", lazy="selectin")


class ItemRow(Base):
    __tablename__ = "detection_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    detection_id: Mapped[str] = mapped_column(ForeignKey("detections.id"), index=True)
    class_id: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float)
    xmin: Mapped[float] = mapped_column(Float)
    ymin: Mapped[float] = mapped_column(Float)
    xmax: Mapped[float] = mapped_column(Float)
    ymax: Mapped[float] = mapped_column(Float)
    detection: Mapped[DetectionRow] = relationship(back_populates="items")


def make_session_factory(url: str):
    kw = {}
    if url.startswith("sqlite"):
        kw["connect_args"] = {"check_same_thread": False}
        if url in ("sqlite://", "sqlite:///:memory:") or ":memory:" in url:
            kw["poolclass"] = StaticPool
    engine = create_engine(url, **kw)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


class DetectionRepository:
    """Only metadata is stored. Uploaded images are never written to disk."""

    def __init__(self, session):
        self.s = session

    def add(self, version, w, h, ms, dets) -> DetectionRow:
        row = DetectionRow(model_version=version, image_width=w, image_height=h, inference_ms=ms,
                           items=[ItemRow(class_id=d.class_id, confidence=d.confidence, xmin=d.box[0],
                                          ymin=d.box[1], xmax=d.box[2], ymax=d.box[3]) for d in dets])
        self.s.add(row)
        self.s.commit()
        return row

    def get(self, id_):
        return self.s.get(DetectionRow, id_)

    def list(self, page, page_size):
        total = self.s.scalar(select(func.count()).select_from(DetectionRow))
        q = select(DetectionRow).order_by(DetectionRow.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.s.scalars(q)), total

    def summary(self):
        n = self.s.scalar(select(func.count()).select_from(DetectionRow)) or 0
        items = self.s.scalar(select(func.count()).select_from(ItemRow)) or 0
        avg = self.s.scalar(select(func.avg(DetectionRow.inference_ms)))
        return {"total_images": n, "total_detections": items, "avg_inference_ms": avg,
                "images_without_detections": self.s.scalar(
                    select(func.count()).select_from(DetectionRow).where(~DetectionRow.items.any())) or 0}

    def by_class(self):
        q = select(ItemRow.class_id, func.count(), func.avg(ItemRow.confidence)).group_by(ItemRow.class_id)
        return [(c, n, a) for c, n, a in self.s.execute(q)]

    def confidences(self):
        return list(self.s.scalars(select(ItemRow.confidence)))

    def daily_counts(self):
        day = func.date(DetectionRow.created_at)
        return [(str(d), n) for d, n in self.s.execute(select(day, func.count()).group_by(day).order_by(day))]
