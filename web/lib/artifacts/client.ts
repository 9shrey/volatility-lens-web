import {
  ManifestSchema,
  RegimeSnapshotSchema,
  SUPPORTED_SCHEMA_VERSION,
  SkewMetricSchema,
  SurfaceSnapshotSchema,
  TermPointSchema,
  TickerIndexSchema,
  type Manifest,
  type RegimeSnapshot,
  type SkewMetric,
  type SnapshotView,
  type SurfaceSnapshot,
  type TermPoint,
  type TickerIndex,
} from "./schemas";
import { z } from "zod";
import { bundleBaseUrl } from "../env";

export class ArtifactError extends Error {}

async function getJSON<T>(url: string, schema: z.ZodType<T>, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { next: { revalidate: 3600 }, signal });
  if (!res.ok) {
    throw new ArtifactError(`Fetch ${url} failed: ${res.status}`);
  }
  const json = await res.json();
  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    throw new ArtifactError(`Schema validation failed for ${url}: ${parsed.error.message}`);
  }
  return parsed.data;
}

export async function fetchManifest(signal?: AbortSignal): Promise<Manifest> {
  const m = await getJSON(`${bundleBaseUrl()}/manifest.json`, ManifestSchema, signal);
  if (m.schema_version !== SUPPORTED_SCHEMA_VERSION) {
    throw new ArtifactError(
      `Unsupported bundle schema_version=${m.schema_version}; expected ${SUPPORTED_SCHEMA_VERSION}`,
    );
  }
  return m;
}

export async function listTickers(signal?: AbortSignal): Promise<TickerIndex> {
  return getJSON(`${bundleBaseUrl()}/index.json`, TickerIndexSchema, signal);
}

async function resolveDate(symbol: string, date: string, signal?: AbortSignal): Promise<string> {
  if (date !== "latest") return date;
  const pointer = await getJSON(
    `${bundleBaseUrl()}/tickers/${symbol}/latest.json`,
    z.object({ path: z.string() }),
    signal,
  );
  return pointer.path;
}

export type SnapshotResult =
  | { view: "surface"; data: SurfaceSnapshot }
  | { view: "skew"; data: SkewMetric[] }
  | { view: "term"; data: TermPoint[] }
  | { view: "regime"; data: RegimeSnapshot };

export async function fetchSnapshot(
  symbol: string,
  date: string,
  view: SnapshotView,
  opts: { signal?: AbortSignal } = {},
): Promise<SnapshotResult> {
  const resolved = await resolveDate(symbol, date, opts.signal);
  const base = `${bundleBaseUrl()}/tickers/${symbol}/${resolved}`;
  switch (view) {
    case "surface":
      return { view, data: await getJSON(`${base}/surface.json`, SurfaceSnapshotSchema, opts.signal) };
    case "skew":
      return { view, data: await getJSON(`${base}/skew.json`, z.array(SkewMetricSchema), opts.signal) };
    case "term":
      return { view, data: await getJSON(`${base}/term.json`, z.array(TermPointSchema), opts.signal) };
    case "regime":
      return { view, data: await getJSON(`${base}/regime.json`, RegimeSnapshotSchema, opts.signal) };
  }
}
