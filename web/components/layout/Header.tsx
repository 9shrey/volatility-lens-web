import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-[color:var(--border)]">
      <div className="max-w-6xl mx-auto w-full px-4 py-3 flex items-center justify-between">
        <Link href="/" className="font-semibold tracking-tight">
          Volatility&nbsp;Lens
        </Link>
        <nav className="text-sm flex gap-4">
          <Link href="/methodology" className="hover:underline">
            Methodology
          </Link>
          <Link href="/about" className="hover:underline">
            About
          </Link>
        </nav>
      </div>
    </header>
  );
}
