import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <>
      <h2>Road Damage Detection Platform</h2>
      <p className="muted">Detects longitudinal cracks, transverse cracks, alligator cracks and potholes in road images. Model trained on RDD2022.</p>
      <div className="cards">
        <Link className="card" to="/detect"><div className="v">Detection</div><div className="l">Upload an image, get boxes from the real model.</div></Link>
        <Link className="card" to="/analytics"><div className="v">Analytics</div><div className="l">Statistics of images analysed here.</div></Link>
        <Link className="card" to="/model"><div className="v">Model Insights</div><div className="l">Benchmark on a labelled split.</div></Link>
      </div>
      <div className="msg info">Results are model predictions, not engineering assessments. See the Model Card for limitations.</div>
    </>
  );
}
