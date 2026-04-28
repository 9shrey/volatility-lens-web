import { NextResponse } from "next/server";
import { listTickers } from "@/lib/artifacts/client";

export const runtime = "edge";
export const revalidate = 86400;

export async function GET() {
  try {
    const idx = await listTickers();
    return NextResponse.json({
      tickers: idx.tickers.map((t) => t.symbol),
      as_of: idx.as_of,
      manifest_version: idx.manifest_version,
    });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 502 });
  }
}
