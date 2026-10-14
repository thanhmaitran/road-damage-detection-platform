import type { DetectionResult } from "../../types/detection";
import { CLASS_COLORS } from "../../services/boxes";

/** SVG overlay uses viewBox = original image size, so boxes stay exact at any display size. */
export default function DetectionCanvas({ src, result, minConfidence, hidden }: {
  src: string; result: DetectionResult; minConfidence: number; hidden: Set<string>;
}) {
  const W = result.image_width, H = result.image_height;
  const sw = Math.max(2, Math.round(Math.max(W, H) / 300));
  return (
    <div className="stage">
      <img src={src} alt="Analysed road" />
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
        {result.detections.filter((d) => d.confidence >= minConfidence && !hidden.has(d.class_code)).map((d, i) => {
          const c = CLASS_COLORS[d.class_code] ?? "#fff";
          return (
            <g key={i}>
              <rect x={d.box.xmin} y={d.box.ymin} width={d.box.xmax - d.box.xmin} height={d.box.ymax - d.box.ymin}
                fill="none" stroke={c} strokeWidth={sw} />
              <text x={d.box.xmin + sw} y={Math.max(sw * 6, d.box.ymin - sw)} fill={c} fontSize={sw * 6}>
                {d.class_code} {(d.confidence * 100).toFixed(0)}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
