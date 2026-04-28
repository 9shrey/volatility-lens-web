import type { MetadataRoute } from "next";
import { listTickers } from "@/lib/artifacts/client";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.VLENS_SITE_URL ?? "https://volatility-lens.vercel.app";
  let tickers: string[] = [];
  try {
    const idx = await listTickers();
    tickers = idx.tickers.map((t) => t.symbol);
  } catch {
    /* ignore */
  }
  return [
    { url: `${base}/`, changeFrequency: "daily", priority: 1 },
    { url: `${base}/methodology`, changeFrequency: "monthly" },
    { url: `${base}/about`, changeFrequency: "monthly" },
    ...tickers.map((s) => ({
      url: `${base}/ticker/${s}`,
      changeFrequency: "daily" as const,
      priority: 0.8,
    })),
  ];
}
