"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { SkewMetric } from "@/lib/artifacts/schemas";

export function SkewChart({
  data,
  isLoading,
}: {
  data: SkewMetric[];
  isLoading: boolean;
  asOf?: string;
}) {
  if (isLoading) {
    return <div className="h-48 animate-pulse bg-[color:var(--border)] rounded" />;
  }
  return (
    <div data-testid="skew-chart" className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" tick={{ fontSize: 10 }} minTickGap={32} />
          <YAxis tick={{ fontSize: 10 }} width={40} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="rr_25d"
            stroke="#1f77b4"
            dot={false}
            strokeWidth={1.5}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
