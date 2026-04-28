export default function MethodologyPage() {
  return (
    <article className="prose dark:prose-invert max-w-none">
      <h1>Methodology</h1>
      <h2>SVI surface fit</h2>
      <p>
        Each tenor slice is fit with the raw SVI parameterization{" "}
        <code>w(k) = a + b·(ρ·(k − m) + √((k − m)² + σ²))</code>. We enforce the necessary
        no-arbitrage condition <code>a + b·σ·√(1 − ρ²) ≥ 0</code> at fit time and report
        butterfly + calendar violations after the fit rather than silently correcting them.
      </p>
      <h2>Skew metrics</h2>
      <p>
        Risk-reversal and butterfly are computed at the 25-delta strike, derived numerically
        from the fitted SVI surface under Black-Scholes (r = 0). The term slope is the
        90-day ATM IV minus the 30-day ATM IV.
      </p>
      <h2>Regime model</h2>
      <p>
        A Gaussian HMM (K ∈ {"{2, 3}"}) is fit on rolling realized vol, IV − RV, 25Δ RR,
        and term slope. State labels are deterministic by the unconditional mean of feature
        zero (realized vol) so that <code>0 → calm</code>, <code>1 → normal</code>, and{" "}
        <code>2 → stress</code> are stable across re-fits.
      </p>
      <h2>No look-ahead</h2>
      <p>
        Pipeline modules accept an explicit <code>cutoff</code>; using any data with{" "}
        <code>as_of &gt; cutoff</code> is a runtime error. A property test asserts that
        shifting input series by k bars shifts every derived series by exactly k bars.
      </p>
      <h2>Source data</h2>
      <p>
        The default deployment runs on a <strong>synthetic</strong> SVI-based generator so the
        site is reproducible without paid data. Real-data adapters are pluggable but disabled in
        CI.
      </p>
    </article>
  );
}
