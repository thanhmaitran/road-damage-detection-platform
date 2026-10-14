import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function ConfidenceChart({ values }: { values: number[] }) {
  const bins = Array.from({ length: 10 }, (_, i) => ({ range: `${i * 10}-${i * 10 + 10}%`, count: 0 }));
  values.forEach((v) => { bins[Math.min(9, Math.floor(v * 10))].count++; });
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={bins}><CartesianGrid strokeDasharray="3 3" stroke="#25324d" />
        <XAxis dataKey="range" stroke="#9fb0c8" /><YAxis allowDecimals={false} stroke="#9fb0c8" />
        <Tooltip /><Bar dataKey="count" fill="#ffd54f" /></BarChart>
    </ResponsiveContainer>
  );
}
