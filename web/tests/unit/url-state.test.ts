import { describe, expect, it } from "vitest";
import { parseUrlState, buildUrl } from "@/lib/url-state";

describe("url-state", () => {
  it("falls back to defaults", () => {
    const s = parseUrlState(new URLSearchParams(""));
    expect(s.symbol).toBe("SPY");
    expect(s.view).toBe("surface");
    expect(s.model).toBe("hmm3");
    expect(s.theme).toBe("auto");
  });

  it("uppercases symbol and parses known values", () => {
    const s = parseUrlState(new URLSearchParams("symbol=qqq&view=skew&model=hmm2&theme=dark"));
    expect(s.symbol).toBe("QQQ");
    expect(s.view).toBe("skew");
    expect(s.model).toBe("hmm2");
    expect(s.theme).toBe("dark");
  });

  it("rejects unknown view → surface fallback", () => {
    const s = parseUrlState(new URLSearchParams("view=garbage"));
    expect(s.view).toBe("surface");
  });

  it("buildUrl roundtrips", () => {
    const u = buildUrl("/ticker/SPY", { view: "skew", model: "hmm3" });
    expect(u).toContain("view=skew");
    expect(u).toContain("model=hmm3");
  });
});
