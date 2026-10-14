import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ClassStat } from "../../types/detection";

export default function ClassDistributionChart({ data }: { data: ClassStat[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#25324d" />
        <XAxis dataKey="class_name" stroke="#9fb0c8" /><YAxis allowDecimals={false} stroke="#9fb0c8" />
        <Tooltip /><Bar dataKey="count" fill="#4fc3f7" /></BarChart>
    </ResponsiveContainer>
  );
}
