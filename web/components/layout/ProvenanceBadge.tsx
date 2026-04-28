export function ProvenanceBadge({ symbol, asOf }: { symbol: string; asOf: string }) {
  return (
    <div
      data-testid="provenance-badge"
      className="text-xs text-[color:var(--muted)] inline-flex gap-2 border border-[color:var(--border)] rounded px-2 py-1"
    >
      <span>symbol: {symbol}</span>
      <span>·</span>
      <span>as_of: {asOf}</span>
      <span>·</span>
      <span>source: synthetic</span>
    </div>
  );
}
