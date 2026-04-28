import { z } from "zod";

export const SnapshotViewSchema = z.enum(["surface", "skew", "term", "regime"]);
export const RegimeModelSchema = z.enum(["hmm2", "hmm3", "cp"]);
export const ThemeSchema = z.enum(["auto", "light", "dark"]);

export type ParsedUrlState = {
  symbol: string;
  date: string;
  view: z.infer<typeof SnapshotViewSchema>;
  model: z.infer<typeof RegimeModelSchema>;
  theme: z.infer<typeof ThemeSchema>;
};

export function parseUrlState(
  search: URLSearchParams,
  defaults: Partial<ParsedUrlState> = {},
): ParsedUrlState {
  const symbol = (search.get("symbol") ?? defaults.symbol ?? "SPY").toUpperCase();
  const date = search.get("date") ?? defaults.date ?? "latest";
  const view = SnapshotViewSchema.safeParse(search.get("view") ?? defaults.view ?? "surface");
  const model = RegimeModelSchema.safeParse(search.get("model") ?? defaults.model ?? "hmm3");
  const theme = ThemeSchema.safeParse(search.get("theme") ?? defaults.theme ?? "auto");
  return {
    symbol,
    date,
    view: view.success ? view.data : "surface",
    model: model.success ? model.data : "hmm3",
    theme: theme.success ? theme.data : "auto",
  };
}

export function buildUrl(path: string, state: Partial<ParsedUrlState>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(state)) if (v) sp.set(k, String(v));
  const qs = sp.toString();
  return qs ? `${path}?${qs}` : path;
}
