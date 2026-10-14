import { useEffect, useState } from "react";
import ClassDistributionChart from "../components/charts/ClassDistributionChart";
import ConfidenceChart from "../components/charts/ConfidenceChart";
import { api } from "../services/api";
import type { ClassesResponse, DetectionPage, Summary } from "../types/detection";

export default function AnalyticsPage() {
  const [sum, setSum] = useState<Summary | null>(null);
  const [cls, setCls] = useState<ClassesResponse | null>(null);
  const [hist, setHist] = useState<DetectionPage | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");

  useEffect(() => { Promise.all([api.summary(), api.classes()]).then(([s, c]) => { setSum(s); setCls(c); }).catch((e) => setError(e.message)); }, []);
  useEffect(() => { api.history(page, 10).then(setHist).catch((e) => setError(e.message)); }, [page]);

  if (error) return <div className="msg error" role="alert">{error}</div>;
  if (!sum || !cls) return <p>Loading…</p>;
  if (sum.total_images === 0) return <div className="msg info">No analyses yet. Upload an image on the Detection page.</div>;

  return (
    <>
      <h2>Analytics</h2>
      <p className="muted">{sum.scope_note} These numbers describe website usage, not model quality and not road conditions.</p>
      <div className="cards">
        <div className="card"><div className="v">{sum.total_images}</div><div className="l">Images analysed</div></div>
        <div className="card"><div className="v">{sum.total_detections}</div><div className="l">Detections</div></div>
        <div className="card"><div className="v">{sum.images_without_detections}</div><div className="l">Images with no detections</div></div>
        <div className="card"><div className="v">{sum.avg_inference_ms?.toFixed(0) ?? "–"} ms</div><div className="l">Mean inference time</div></div>
      </div>
      <div className="row">
        <div className="card grow"><h3>Detections per class</h3><ClassDistributionChart data={cls.classes} /></div>
        <div className="card grow"><h3>Confidence distribution</h3><ConfidenceChart values={cls.confidences} /></div>
      </div>
      <h3>History</h3>
      {hist && (<>
        <table><thead><tr><th>When</th><th>Model</th><th>Size</th><th>Detections</th><th>ms</th></tr></thead>
          <tbody>{hist.items.map((r) => (<tr key={r.id}><td>{new Date(r.created_at).toLocaleString()}</td><td>{r.model_version}</td><td>{r.image_width}×{r.image_height}</td><td>{r.detections.length}</td><td>{r.inference_ms.toFixed(0)}</td></tr>))}</tbody></table>
        <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>{" "}
        <button className="btn" disabled={page * hist.page_size >= hist.total} onClick={() => setPage(page + 1)}>Next</button>
        <span className="muted"> Page {page} · {hist.total} total</span>
      </>)}
    </>
  );
}
