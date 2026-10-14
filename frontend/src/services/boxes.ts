import type { Box } from "../types/detection";

/** Map a box in original-image pixels to displayed pixels (uniform scale, image fits the frame). */
export function scaleBox(b: Box, imgW: number, imgH: number, dispW: number, dispH: number, offX = 0, offY = 0) {
  const sx = dispW / imgW, sy = dispH / imgH;
  return { x: offX + b.xmin * sx, y: offY + b.ymin * sy, w: (b.xmax - b.xmin) * sx, h: (b.ymax - b.ymin) * sy };
}

export const CLASS_COLORS: Record<string, string> = {
  D00: "#4fc3f7", D10: "#ffd54f", D20: "#ba68c8", D40: "#ff7043",
};
