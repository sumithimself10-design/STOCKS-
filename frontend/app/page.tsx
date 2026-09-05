import Link from "next/link";
import { api } from "@/lib/api";

export default async function HomePage() {
  const stocks = (await api.listStocks()) ?? [];

  return (
    <div>
      <h1 className="mb-1 text-xl tracking-wider glow-text">NSE // BSE SCREENER</h1>
      <p className="mb-6 text-sm text-matrixDim">
        QGLP score · technical signal · fundamentals — tracked Indian equities only.
      </p>

      {stocks.length === 0 ? (
        <div className="crt-panel rounded-lg border-dashed p-6 text-sm text-matrixDim">
          NO STOCKS TRACKED YET. RUN{" "}
          <code className="rounded bg-matrixFaint px-1 text-matrix">
            python -m app.scripts.seed_stocks
          </code>{" "}
          ON THE BACKEND TO POPULATE THE UNIVERSE.
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {stocks.map((s) => (
            <Link
              key={s.ticker}
              href={`/stock/${s.ticker}`}
              className="crt-panel group rounded-lg p-4 transition hover:border-matrix hover:shadow-glow"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold tracking-wide group-hover:glow-text">
                  {s.ticker.replace(/\.(NS|BO)$/, "")}
                </span>
                <span className="text-xs text-matrixDim">{s.exchange}</span>
              </div>
              <p className="mt-1 text-sm text-matrixDim">{s.name}</p>
              {s.sector && <p className="mt-1 text-xs text-matrixDim/70">{s.sector}</p>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
