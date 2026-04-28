/**
 * Hand-curated zod mirrors of the pydantic schemas in
 * `pipeline/src/vlens/data/schemas.py`.
 *
 * Run `pnpm gen:schemas` to regenerate `schemas.generated.ts` from the
 * exported JSON Schema; this file pins the public types we actually consume.
 */
import { z } from "zod";

export const SVIParamsSchema = z.object({
  a: z.number(),
  b: z.number().nonnegative(),
  rho: z.number().min(-0.999).max(0.999),
  m: z.number(),
  sigma: z.number().positive(),
});

export const GridSpecSchema = z.object({
  log_moneyness: z.array(z.number()),
  tenor_years: z.array(z.number()),
});

export const SurfaceQualitySchema = z.object({
  rmse_vs_market: z.number().nonnegative(),
  n_quotes: z.number().int().nonnegative(),
  interpolated_cells: z.number().int().nonnegative(),
  butterfly_violations: z.number().int().nonnegative(),
  calendar_violations: z.number().int().nonnegative(),
});

export const SurfaceSnapshotSchema = z.object({
  symbol: z.string(),
  as_of: z.string(),
  grid: GridSpecSchema,
  iv: z.array(z.array(z.number())),
  svi_params: z.record(z.string(), SVIParamsSchema),
  quality: SurfaceQualitySchema,
});

export const SkewMetricSchema = z.object({
  date: z.string(),
  rr_25d: z.number(),
  bf_25d: z.number(),
  atm_iv_30d: z.number(),
  term_slope_30_90: z.number(),
});

export const TermPointSchema = z.object({
  date: z.string(),
  tenor_days: z.number().int(),
  atm_iv: z.number(),
});

export const RegimeStateRowSchema = z.object({
  date: z.string(),
  state: z.number().int().nonnegative(),
  posterior: z.array(z.number()),
});

export const RegimeSnapshotSchema = z.object({
  symbol: z.string(),
  model: z.enum(["hmm_gaussian_k2", "hmm_gaussian_k3", "changepoint_pelt"]),
  fit_window: z.tuple([z.string(), z.string()]),
  states: z.array(RegimeStateRowSchema),
  state_labels: z.record(z.string(), z.string()),
  seed: z.number().int(),
});

export const TickerIndexEntrySchema = z.object({
  symbol: z.string(),
  latest_date: z.string(),
  n_dates: z.number().int(),
});

export const TickerIndexSchema = z.object({
  tickers: z.array(TickerIndexEntrySchema),
  as_of: z.string(),
  manifest_version: z.string(),
});

export const ManifestSchema = z.object({
  schema_version: z.string(),
  pipeline_git_sha: z.string(),
  produced_at: z.string(),
  inputs_hash: z.string(),
  bundle_id: z.string(),
  signature: z.string(),
});

export const SUPPORTED_SCHEMA_VERSION = "1.0";

export type SVIParams = z.infer<typeof SVIParamsSchema>;
export type SurfaceSnapshot = z.infer<typeof SurfaceSnapshotSchema>;
export type SkewMetric = z.infer<typeof SkewMetricSchema>;
export type TermPoint = z.infer<typeof TermPointSchema>;
export type RegimeSnapshot = z.infer<typeof RegimeSnapshotSchema>;
export type TickerIndex = z.infer<typeof TickerIndexSchema>;
export type Manifest = z.infer<typeof ManifestSchema>;
export type SnapshotView = "surface" | "skew" | "term" | "regime";
