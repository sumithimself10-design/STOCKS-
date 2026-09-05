import type { QGLPBreakdown } from "@/lib/api";

function Bar({ label, value }: { label: string; value: number }) {
  const color = value >= 65 ? "bg-matrix shadow-glow" : value >= 40 ? "bg-amber" : "bg-bearish shadow-glowRed";
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-matrixDim">{label.toUpperCase()}</span>
        <span className="font-bold">{value.toFixed(0)}</span>
      </div>
      <div className="h-2 w-full rounded bg-matrixFaint">
        <div className={`h-2 rounded ${color}`} style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}

export default function ScoreCard({ data }: { data: QGLPBreakdown }) {
  return (
    <div className="crt-panel rounded-lg p-5">
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="text-sm tracking-widest text-matrixDim">QGLP SCORE</h2>
        <span className="text-3xl font-bold glow-text">
          {data.composite_score.toFixed(0)}
          <span className="text-sm text-matrixDim">/100</span>
        </span>
      </div>
      <div className="space-y-3">
        <Bar label="Quality" value={data.quality_score} />
        <Bar label="Growth" value={data.growth_score} />
        <Bar label="Longevity" value={data.longevity_score} />
        <Bar label="Price" value={data.price_score} />
      </div>
      {data.notes.length > 0 && (
        <ul className="mt-4 space-y-1 border-t border-panelBorder pt-3 text-xs text-matrixDim">
          {data.notes.map((n, i) => (
            <li key={i}>&gt; {n}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
