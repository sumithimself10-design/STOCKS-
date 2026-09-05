import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinAI Pro India",
  description: "QGLP-driven analysis for NSE & BSE listed stocks",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-panelBorder bg-panel/60 backdrop-blur">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-lg tracking-widest glow-text">
              FIN<span className="text-matrixDim">.</span>AI <span className="text-matrixDim">// INDIA</span>
            </Link>
            <nav className="flex gap-6 text-sm text-matrixDim">
              <Link href="/" className="hover:text-matrix hover:glow-text">SCREENER</Link>
              <Link href="/simulator" className="hover:text-matrix hover:glow-text">SIMULATOR</Link>
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>

        <footer className="mx-auto max-w-5xl px-4 py-8 text-xs text-matrixDim">
          <span className="text-amber">//</span> FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY. NOT INVESTMENT ADVICE.
          QGLP scores and technical signals are decision-support tools, not
          predictions — verify against official filings before acting.
        </footer>
      </body>
    </html>
  );
}
