import { useEffect, useState } from "react";
import { api, ApiError } from "../services/api";
import type { ModelMetrics } from "../types/detection";

export default function ModelInsightsPage() {
  const [m, setM] = useState<ModelMetrics | null>(null);
  const [error, setError] = useState("");
  const [missing, setMissing] = useState(false);
  useEffect(() => { api.metrics().then(setM).catch((e: ApiError) => (e.status === 404 ? setMissing(true) : setError(e.message))); }, []);

  if (error) return <div className="msg error" role="alert">{error}</div>;
  if (missing) return <div className="msg info">No benchmark results yet. Run the evaluation script (see ml/README.md).</div>;
  if (!m) return <p>Loading…</p>;
  const f = (x: number) => x.toFixed(3);
  return (
    <>
      <h2>Model Insights</h2>
      <p className="muted">Benchmark of <b>{m.model_version}</b> on the <b>{m.split}</b> split ({m.n_images} labelled images), evaluated {m.evaluated_at}. Score threshold {m.score_threshold}. mAP follows COCO-style matching.</p>
      <div className="cards">
        <div className="card"><div className="v">{f(m.metrics.map50)}</div><div className="l">mAP@0.5</div></div>
        <div className="card"><div className="v">{f(m.metrics.map)}</div><div className="l">mAP@0.5:0.95</div></div>
        <div className="card"><div className="v">{f(m.metrics.mar_100)}</div><div className="l">Recall (AR@100)</div></div>
        <div className="card"><div className="v">{m.latency_ms.mean.toFixed(0)} ms</div><div className="l">Latency ({m.latency_ms.device})</div></div>
      </div>
      {m.metrics.per_class && (<table><thead><tr><th>Class</th><th>mAP@0.5:0.95</th></tr></thead>
        <tbody>{Object.entries(m.metrics.per_class).map(([k, v]) => <tr key={k}><td>{k}</td><td>{f(v)}</td></tr>)}</tbody></table>)}
      <p className="muted">Latency: {m.latency_ms.note}; warm-up runs: {m.latency_ms.warmup}. Env: {Object.entries(m.env).map(([k, v]) => `${k} ${v}`).join(", ")}.</p>
    </>
  );
}
