import Link from "next/link";
import { env } from "@/lib/env";
import { listTickers, fetchSnapshot } from "@/lib/artifacts/client";
import { SkewChart } from "@/components/charts/SkewChart";
import { RegimeRibbon } from "@/components/charts/RegimeRibbon";
import { ProvenanceBadge } from "@/components/layout/ProvenanceBadge";

export const revalidate = 3600;

export default async function HomePage() {
  const e = env();
  const symbol = e.VLENS_DEFAULT_TICKER;
  let asOf = "—";
  let skew: Awaited<ReturnType<typeof fetchSnapshot>> | null = null;
  let regime: Awaited<ReturnType<typeof fetchSnapshot>> | null = null;

  try {
    const idx = await listTickers();
    asOf = idx.as_of;
    skew = await fetchSnapshot(symbol, "latest", "skew");
    regime = await fetchSnapshot(symbol, "latest", "regime");
  } catch {
    // graceful: render shell even when bundle is unreachable in dev
  }

  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Volatility & Regime Lens</h1>
        <p className="text-[color:var(--muted)] max-w-2xl">
          Daily implied-volatility surfaces, skew metrics, and statistical regime classifications.
          Powered by a deterministic Python pipeline that publishes signed, versioned artifacts.
        </p>
        <div className="flex gap-3 text-sm">
          <Link className="underline" href={`/ticker/${symbol}`}>Open {symbol} lens →</Link>
          <Link className="underline" href="/methodology">Methodology</Link>
        </div>
      </section>

      <ProvenanceBadge symbol={symbol} asOf={asOf} />

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded border border-[color:var(--border)] p-3">
          <h2 className="font-medium mb-2">Skew (25Δ RR · 30d)</h2>
          {skew?.view === "skew" ? (
            <SkewChart data={skew.data} isLoading={false} />
          ) : (
            <p className="text-sm text-[color:var(--muted)]">No bundle available.</p>
          )}
        </div>
        <div className="rounded border border-[color:var(--border)] p-3">
          <h2 className="font-medium mb-2">Regime ribbon</h2>
          {regime?.view === "regime" ? (
            <RegimeRibbon data={regime.data} isLoading={false} />
          ) : (
            <p className="text-sm text-[color:var(--muted)]">No bundle available.</p>
          )}
        </div>
      </section>
    </div>
  );
}
