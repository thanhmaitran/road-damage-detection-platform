import type { DetectionItem } from "../../types/detection";

export default function DetectionTable({ items }: { items: DetectionItem[] }) {
  if (!items.length) return <div className="msg info">No road damage detected above the selected threshold.</div>;
  return (
    <table>
      <thead><tr><th>Class</th><th>Confidence</th><th>Box (px)</th></tr></thead>
      <tbody>
        {items.map((d, i) => (
          <tr key={i}>
            <td>{d.class_name} <span className="muted">({d.class_code})</span></td>
            <td>{(d.confidence * 100).toFixed(1)}%</td>
            <td>{[d.box.xmin, d.box.ymin, d.box.xmax, d.box.ymax].map(Math.round).join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
