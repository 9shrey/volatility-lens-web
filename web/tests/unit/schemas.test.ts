import { describe, expect, it } from "vitest";
import {
  ManifestSchema,
  RegimeSnapshotSchema,
  SurfaceSnapshotSchema,
} from "@/lib/artifacts/schemas";

describe("zod artifact schemas", () => {
  it("accepts a minimal SurfaceSnapshot", () => {
    const ok = SurfaceSnapshotSchema.safeParse({
      symbol: "SPY",
      as_of: "2024-12-31",
      grid: { log_moneyness: [-0.1, 0.0, 0.1], tenor_years: [0.25] },
      iv: [[0.2, 0.18, 0.21]],
      svi_params: {
        "0.250000": { a: 0.02, b: 0.1, rho: -0.3, m: 0.0, sigma: 0.2 },
      },
      quality: {
        rmse_vs_market: 0.001,
        n_quotes: 3,
        interpolated_cells: 0,
        butterfly_violations: 0,
        calendar_violations: 0,
      },
    });
    expect(ok.success).toBe(true);
  });

  it("rejects invalid SVI rho", () => {
    const r = SurfaceSnapshotSchema.safeParse({
      symbol: "SPY",
      as_of: "2024-12-31",
      grid: { log_moneyness: [0], tenor_years: [0.25] },
      iv: [[0.2]],
      svi_params: { "0.25": { a: 0, b: 0.1, rho: 1.5, m: 0, sigma: 0.2 } },
      quality: {
        rmse_vs_market: 0,
        n_quotes: 1,
        interpolated_cells: 0,
        butterfly_violations: 0,
        calendar_violations: 0,
      },
    });
    expect(r.success).toBe(false);
  });

  it("regime snapshot rejects unknown model", () => {
    const r = RegimeSnapshotSchema.safeParse({
      symbol: "SPY",
      model: "magic_lstm",
      fit_window: ["2024-01-01", "2024-12-31"],
      states: [],
      state_labels: {},
      seed: 1,
    });
    expect(r.success).toBe(false);
  });

  it("manifest requires schema_version", () => {
    expect(ManifestSchema.safeParse({}).success).toBe(false);
  });
});
