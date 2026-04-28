"use client";

import type { SurfaceSnapshot } from "@/lib/artifacts/schemas";

/**
 * 2-D heatmap fallback for the implied-volatility surface.
 * The 3-D r3f variant (Surface3D) is dynamically imported on the surface tab
 * for desktop viewports; this component is the always-available SSR fallback.
 */
export function SurfaceHeatmap({
  data,
  isLoading,
}: {
  data: SurfaceSnapshot;
  isLoading: boolean;
}) {
  if (isLoading) {
    return <div className="h-64 animate-pulse bg-[color:var(--border)] rounded" />;
  }
  const flat = data.iv.flat();
  const min = Math.min(...flat);
  const max = Math.max(...flat);
  const span = max - min || 1;

  return (
    <div data-testid="surface-heatmap" className="overflow-x-auto">
      <table className="text-[10px] border-collapse" aria-label="Implied volatility surface">
        <thead>
          <tr>
            <th className="px-1 py-0.5 text-left">tenor (yr) ↓ / k →</th>
            {data.grid.log_moneyness.map((k, i) => (
              <th key={i} className="px-1 py-0.5 text-right">
                {k.toFixed(2)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.grid.tenor_years.map((t, i) => (
            <tr key={i}>
              <td className="px-1 py-0.5 font-mono">{t.toFixed(3)}</td>
              {(data.iv[i] ?? []).map((v, j) => {
                const u = (v - min) / span;
                const bg = `rgb(${Math.round(255 * u)}, ${Math.round(80 + 100 * (1 - u))}, ${Math.round(255 * (1 - u))})`;
                return (
                  <td
                    key={j}
                    className="px-1 py-0.5 text-right font-mono"
                    style={{ background: bg, color: "#fff" }}
                    title={`k=${data.grid.log_moneyness[j]?.toFixed(2)} t=${t.toFixed(3)} iv=${v.toFixed(4)}`}
                  >
                    {v.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
