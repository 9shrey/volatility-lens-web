export default function AboutPage() {
  return (
    <article className="prose dark:prose-invert max-w-none space-y-3">
      <h1>About</h1>
      <p>
        Volatility & Regime Lens is a public, interactive web product backed by a
        deterministic Python research pipeline. The pipeline nightly publishes versioned,
        signed JSON artifacts; the website consumes them statically via Vercel’s edge.
      </p>
      <p>
        Not investment advice. Source data is synthetic by default.
      </p>
    </article>
  );
}
