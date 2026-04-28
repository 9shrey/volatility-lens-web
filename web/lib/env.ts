import { z } from "zod";

const EnvSchema = z.object({
  VLENS_BLOB_BASE_URL: z.string().url().optional(),
  VLENS_BUNDLE_VERSION: z.string().optional(),
  VLENS_PIPELINE_SECRET: z.string().min(8).optional(),
  VLENS_DEFAULT_TICKER: z.string().min(1).default("SPY"),
  VLENS_LOCAL_BUNDLE_PATH: z.string().optional(),
});

export type Env = z.infer<typeof EnvSchema>;

let cached: Env | null = null;

export function env(): Env {
  if (cached) return cached;
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    throw new Error("Invalid environment: " + parsed.error.toString());
  }
  cached = parsed.data;
  return cached;
}

export function bundleBaseUrl(): string {
  const e = env();
  if (e.VLENS_BLOB_BASE_URL && e.VLENS_BUNDLE_VERSION) {
    return `${e.VLENS_BLOB_BASE_URL.replace(/\/$/, "")}/${e.VLENS_BUNDLE_VERSION}`;
  }
  // Local fallback for `next dev`: served from /public/_smoke_bundle/
  return "/_smoke_bundle";
}
