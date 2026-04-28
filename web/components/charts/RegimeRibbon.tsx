"use client";

import type { RegimeSnapshot } from "@/lib/artifacts/schemas";

const COLORS: Record<string, string> = {
  calm: "#1f77b4",
  normal: "#7f7f7f",
  stress: "#d62728",
};
const PATTERNS: Record<string, string> = {
  calm: "",
  normal: "/",
  stress: "x",
};

export function RegimeRibbon({
  data,
  isLoading,
}: {
  data: RegimeSnapshot;
  isLoading: boolean;
}) {
  if (isLoading) {
    return <div className="h-12 animate-pulse bg-[color:var(--border)] rounded" />;
  }
  const total = data.states.length || 1;
  return (
    <div className="space-y-2" data-testid="regime-ribbon">
      <div
        className="flex h-8 w-full overflow-hidden rounded border border-[color:var(--border)]"
        role="img"
        aria-label={`Regime ribbon over ${total} days`}
      >
        {data.states.map((row, i) => {
          const label = data.state_labels[String(row.state)] ?? `state_${row.state}`;
          const color = COLORS[label] ?? "#999";
          return (
            <span
              key={i}
              title={`${row.date} · ${label}`}
              aria-label={`${row.date} ${label}`}
              data-pattern={PATTERNS[label]}
              style={{ background: color, flex: `1 1 ${100 / total}%` }}
            />
          );
        })}
      </div>
      <div className="flex gap-3 text-xs text-[color:var(--muted)]">
        {Object.entries(data.state_labels).map(([k, v]) => (
          <span key={k} className="inline-flex items-center gap-1">
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ background: COLORS[v] ?? "#999" }}
            />
            {v}
          </span>
        ))}
      </div>
    </div>
  );
}
