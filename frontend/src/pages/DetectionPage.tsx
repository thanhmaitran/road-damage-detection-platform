import { useEffect, useState } from "react";
import ImageUploader from "../components/detection/ImageUploader";
import DetectionCanvas from "../components/detection/DetectionCanvas";
import DetectionTable from "../components/detection/DetectionTable";
import { api } from "../services/api";
import type { DetectionResult } from "../types/detection";

export default function DetectionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState<string>("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [minConf, setMinConf] = useState(0.5);
  const [hidden, setHidden] = useState<Set<string>>(new Set());

  useEffect(() => { if (!file) { setUrl(""); return; } const u = URL.createObjectURL(file); setUrl(u); return () => URL.revokeObjectURL(u); }, [file]);

  async function run() {
    if (!file) return;
    setLoading(true); setError(""); setResult(null);
    try { setResult(await api.detect(file)); } catch (e) { setError((e as Error).message); } finally { setLoading(false); }
  }
  const visible = result?.detections.filter((d) => d.confidence >= minConf && !hidden.has(d.class_code)) ?? [];
  const codes = Array.from(new Set(result?.detections.map((d) => d.class_code) ?? []));

  return (
    <>
      <h2>Detection</h2>
      <ImageUploader disabled={loading} onSelect={(f, err) => { setFile(f); setResult(null); setError(err ?? ""); }} />
      <button className="btn" style={{ marginLeft: 12 }} disabled={!file || loading} onClick={run}>{loading ? "Analysing…" : "Analyse"}</button>
      {error && <div className="msg error" role="alert">{error}</div>}
      {result && url && (
        <div className="row" style={{ marginTop: 16 }}>
          <div className="grow"><DetectionCanvas src={url} result={result} minConfidence={minConf} hidden={hidden} /></div>
          <div className="grow">
            <p className="muted">Model {result.model_version} · {result.inference_ms.toFixed(0)} ms · {result.image_width}×{result.image_height}</p>
            <label>Confidence ≥ {(minConf * 100).toFixed(0)}% <input type="range" min={0} max={1} step={0.05} value={minConf} onChange={(e) => setMinConf(+e.target.value)} /></label>
            <div>{codes.map((c) => (
              <label key={c} style={{ marginRight: 12 }}>
                <input type="checkbox" checked={!hidden.has(c)} onChange={() => setHidden((h) => { const n = new Set(h); n.has(c) ? n.delete(c) : n.add(c); return n; })} /> {c}
              </label>))}</div>
            <DetectionTable items={visible} />
          </div>
        </div>
      )}
    </>
  );
}
