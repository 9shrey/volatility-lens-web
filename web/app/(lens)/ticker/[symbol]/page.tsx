import { notFound } from "next/navigation";
import { fetchSnapshot, listTickers } from "@/lib/artifacts/client";
import { SkewChart } from "@/components/charts/SkewChart";
import { TermStructure } from "@/components/charts/TermStructure";
import { RegimeRibbon } from "@/components/charts/RegimeRibbon";
import { SurfaceHeatmap } from "@/components/charts/SurfaceHeatmap";
import { ProvenanceBadge } from "@/components/layout/ProvenanceBadge";

export const revalidate = 3600;

export async function generateStaticParams() {
  try {
    const idx = await listTickers();
    return idx.tickers.map((t) => ({ symbol: t.symbol }));
  } catch {
    return [];
  }
}

type Params = { params: { symbol: string } };

export default async function TickerPage({ params }: Params) {
  const symbol = params.symbol.toUpperCase();
  let surface, skew, term, regime;
  try {
    [surface, skew, term, regime] = await Promise.all([
      fetchSnapshot(symbol, "latest", "surface"),
      fetchSnapshot(symbol, "latest", "skew"),
      fetchSnapshot(symbol, "latest", "term"),
      fetchSnapshot(symbol, "latest", "regime"),
    ]);
  } catch {
    notFound();
  }
  if (
    !surface ||
    surface.view !== "surface" ||
    !skew ||
    skew.view !== "skew" ||
    !term ||
    term.view !== "term" ||
    !regime ||
    regime.view !== "regime"
  ) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">{symbol}</h1>
        <ProvenanceBadge symbol={symbol} asOf={surface.data.as_of} />
      </div>

      <section className="rounded border border-[color:var(--border)] p-3">
        <h2 className="font-medium mb-2">Implied volatility surface</h2>
        <SurfaceHeatmap data={surface.data} isLoading={false} />
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded border border-[color:var(--border)] p-3">
          <h2 className="font-medium mb-2">Skew (25Δ RR)</h2>
          <SkewChart data={skew.data} isLoading={false} />
        </section>
        <section className="rounded border border-[color:var(--border)] p-3">
          <h2 className="font-medium mb-2">ATM term structure</h2>
          <TermStructure data={term.data} isLoading={false} />
        </section>
      </div>

      <section className="rounded border border-[color:var(--border)] p-3">
        <h2 className="font-medium mb-2">Regime ribbon ({regime.data.model})</h2>
        <RegimeRibbon data={regime.data} isLoading={false} />
      </section>

      <section className="text-sm">
        <a
          className="underline"
          href={`/api/snapshot?symbol=${symbol}&date=${surface.data.as_of}&view=surface`}
        >
          Get data (JSON) ↓
        </a>
      </section>
    </div>
  );
}
