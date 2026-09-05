import type { TechnicalSignal } from "@/lib/api";

const STYLES: Record<TechnicalSignal["signal"], string> = {
  bullish: "bg-matrixFaint text-matrix border-matrix shadow-glow glow-text",
  bearish: "bg-[#2a0e0b] text-bearish border-bearish shadow-glowRed glow-text-red",
  neutral: "bg-matrixFaint text-matrixDim border-panelBorder",
};

export default function SignalBadge({ data }: { data: TechnicalSignal }) {
  return (
    <div className="crt-panel rounded-lg p-5">
      <h2 className="mb-3 text-sm tracking-widest text-matrixDim">TECHNICAL SIGNAL</h2>
      <span className={`inline-block rounded border px-3 py-1 text-sm font-bold uppercase ${STYLES[data.signal]}`}>
        {data.signal}
      </span>
      <dl className="mt-4 grid grid-cols-2 gap-y-2 text-sm">
        <dt className="text-matrixDim">CLOSE</dt>
        <dd className="text-right">₹{data.close.toFixed(2)}</dd>
        <dt className="text-matrixDim">200-DAY SMA</dt>
        <dd className="text-right">{data.sma_200 ? `₹${data.sma_200.toFixed(2)}` : "—"}</dd>
        <dt className="text-matrixDim">VS. SMA</dt>
        <dd className="text-right">
          {data.price_vs_sma200_pct !== null ? `${data.price_vs_sma200_pct.toFixed(2)}%` : "—"}
        </dd>
        <dt className="text-matrixDim">VOLUME CONFIRMED</dt>
        <dd className="text-right">{data.volume_confirmed ? "YES" : "NO"}</dd>
        <dt className="text-matrixDim">RSI (14)</dt>
        <dd className="text-right">{data.rsi_14 ?? "—"}</dd>
      </dl>
      <p className="mt-3 text-xs text-matrixDim/70">
        &gt; PRIMARY SIGNAL: PRICE VS. 200-DAY SMA, CONFIRMED BY VOLUME. RSI SHOWN AS SECONDARY CONTEXT ONLY.
      </p>
    </div>
  );
}
