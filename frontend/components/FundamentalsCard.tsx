"use client";

import { Bar, CartesianGrid, Line, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Fundamentals } from "@/lib/api";

export default function FundamentalsCard({ data }: { data: Fundamentals }) {
  const chartData = data.quarterly_labels.map((label, i) => ({
    quarter: label.slice(0, 7),
    revenue: data.quarterly_revenue[i],
    netProfit: data.quarterly_net_profit[i],
  }));

  return (
    <div className="crt-panel rounded-lg p-5">
      <h2 className="mb-3 text-sm tracking-widest text-matrixDim">FUNDAMENTALS</h2>
      <dl className="mb-5 grid grid-cols-2 gap-y-2 text-sm">
        <dt className="text-matrixDim">PE RATIO</dt>
        <dd className="text-right">{data.pe_ratio ?? "—"}</dd>
        <dt className="text-matrixDim">5YR MEDIAN PE</dt>
        <dd className="text-right">{data.pe_5yr_median ?? "—"}</dd>
        <dt className="text-matrixDim">DEBT / EQUITY</dt>
        <dd className="text-right">{data.debt_to_equity ?? "—"}</dd>
        <dt className="text-matrixDim">INTEREST COVERAGE</dt>
        <dd className="text-right">{data.interest_coverage ?? "—"}x</dd>
      </dl>

      {chartData.length > 0 ? (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#123021" />
              <XAxis dataKey="quarter" fontSize={11} stroke="#1c7a4a" />
              <YAxis fontSize={11} stroke="#1c7a4a" />
              <Tooltip
                contentStyle={{ background: "#0a0f0c", border: "1px solid #123021", color: "#39ff88" }}
                labelStyle={{ color: "#39ff88" }}
              />
              <Bar dataKey="revenue" fill="#1c7a4a" name="Revenue" radius={[3, 3, 0, 0]} />
              <Line type="monotone" dataKey="netProfit" stroke="#39ff88" strokeWidth={2} name="Net profit" dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="text-sm text-matrixDim">NO QUARTERLY HISTORY AVAILABLE YET.</p>
      )}
    </div>
  );
}
