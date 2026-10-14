import { useRef } from "react";

const MAX_MB = 10;
const OK = ["image/jpeg", "image/png"];

/** Client-side checks are only UX; the backend re-validates everything. */
export default function ImageUploader({ onSelect, disabled }: { onSelect: (f: File | null, error?: string) => void; disabled?: boolean }) {
  const ref = useRef<HTMLInputElement>(null);
  return (
    <input
      ref={ref} type="file" accept="image/jpeg,image/png" disabled={disabled} aria-label="Choose an image"
      onChange={(e) => {
        const f = e.target.files?.[0] ?? null;
        if (!f) return onSelect(null);
        if (!OK.includes(f.type)) return onSelect(null, "Only JPEG and PNG images are supported.");
        if (f.size > MAX_MB * 1024 * 1024) return onSelect(null, `File is larger than ${MAX_MB} MB.`);
        onSelect(f);
      }}
    />
  );
}
