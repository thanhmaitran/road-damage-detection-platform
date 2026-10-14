import { describe, expect, it } from "vitest";
import { scaleBox } from "./boxes";

describe("scaleBox", () => {
  it("scales per axis", () => {
    const r = scaleBox({ xmin: 100, ymin: 50, xmax: 300, ymax: 150 }, 1000, 500, 500, 250);
    expect(r).toEqual({ x: 50, y: 25, w: 100, h: 50 });
  });
  it("applies offsets", () => {
    expect(scaleBox({ xmin: 0, ymin: 0, xmax: 10, ymax: 10 }, 100, 100, 50, 50, 7, 3)).toEqual({ x: 7, y: 3, w: 5, h: 5 });
  });
});
