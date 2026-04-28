export function Footer() {
  return (
    <footer className="border-t border-[color:var(--border)] mt-8">
      <div className="max-w-6xl mx-auto w-full px-4 py-4 text-xs text-[color:var(--muted)] flex justify-between">
        <span>Source: synthetic demo data. Not investment advice.</span>
        <a
          href="https://github.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:underline"
        >
          Source
        </a>
      </div>
    </footer>
  );
}
