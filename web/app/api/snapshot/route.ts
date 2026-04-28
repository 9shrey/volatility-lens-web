import { NextResponse } from "next/server";
import { fetchSnapshot } from "@/lib/artifacts/client";
import { SnapshotViewSchema } from "@/lib/url-state";

export const runtime = "edge";
export const revalidate = 86400;

export async function GET(req: Request) {
  const url = new URL(req.url);
  const symbol = (url.searchParams.get("symbol") ?? "").toUpperCase();
  const date = url.searchParams.get("date") ?? "latest";
  const view = SnapshotViewSchema.safeParse(url.searchParams.get("view") ?? "surface");
  if (!symbol) return NextResponse.json({ error: "missing symbol" }, { status: 400 });
  if (!view.success) return NextResponse.json({ error: "invalid view" }, { status: 400 });
  try {
    const result = await fetchSnapshot(symbol, date, view.data);
    const body = JSON.stringify(result.data);
    return new NextResponse(body, {
      headers: {
        "content-type": "application/json",
        "cache-control": "public, s-maxage=86400, stale-while-revalidate=604800",
      },
    });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 502 });
  }
}
