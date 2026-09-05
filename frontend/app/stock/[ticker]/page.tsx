import Link from "next/link";
import { api } from "@/lib/api";
import ScoreCard from "@/components/ScoreCard";
import SignalBadge from "@/components/SignalBadge";
import FundamentalsCard from "@/components/FundamentalsCard";
import NewsList from "@/components/NewsList";

export default async function StockPage({ params }: { params: { ticker: string } }) {
  const ticker = decodeURIComponent(params.ticker);
  const companyName = ticker.replace(/\.(NS|BO)$/, "");

  const [qglp, technical, fundamentals, news] = await Promise.all([
    api.getQglp(companyName),
    api.getTechnical(companyName),
    api.getFundamentals(companyName),
    api.getNews(companyName),
  ]);

  return (
    <div>
      <Link href="/" className="mb-4 inline-block text-sm text-matrixDim hover:text-matrix hover:glow-text">
        &lt; BACK TO SCREENER
      </Link>
      <h1 className="mb-6 text-xl tracking-wider glow-text">{companyName}</h1>

      <div className="grid gap-4 sm:grid-cols-2">
        {qglp ? <ScoreCard data={qglp} /> : <FailedCard label="QGLP score" />}
        {technical ? <SignalBadge data={technical} /> : <FailedCard label="Technical signal" />}
        {fundamentals ? <FundamentalsCard data={fundamentals} /> : <FailedCard label="Fundamentals" />}
        <NewsList items={news ?? []} />
      </div>
    </div>
  );
}

function FailedCard({ label }: { label: string }) {
  return (
    <div className="crt-panel rounded-lg border-dashed p-5 text-sm text-matrixDim">
      &gt; COULDN&apos;T LOAD {label.toUpperCase()} — the backend may still be fetching data for this ticker, or it hit a rate limit. Try again shortly.
    </div>
  );
}
