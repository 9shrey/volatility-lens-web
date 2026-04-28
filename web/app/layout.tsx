import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

export const metadata: Metadata = {
  title: "Volatility & Regime Lens",
  description:
    "Equity implied-volatility surfaces, skew/term-structure dynamics, and statistical regime classifications.",
  openGraph: {
    title: "Volatility & Regime Lens",
    description:
      "Interactive volatility surfaces and regime classifications, backed by a deterministic research pipeline.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col font-sans">
        <Header />
        <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
