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
import type { TermPoint } from "@/lib/artifacts/schemas";

export function TermStructure({
  data,
  isLoading,
}: {
  data: TermPoint[];
  isLoading: boolean;
}) {
  if (isLoading) {
    return <div className="h-48 animate-pulse bg-[color:var(--border)] rounded" />;
  }
  // Pivot: take the latest date's term structure
  const latest = data[data.length - 1]?.date;
  const slice = latest ? data.filter((d) => d.date === latest) : data;
  return (
    <div data-testid="term-chart" className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={slice} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="tenor_days" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} width={40} />
          <Tooltip />
          <Line dataKey="atm_iv" stroke="#7f7f7f" dot strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
