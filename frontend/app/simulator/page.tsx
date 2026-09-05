"use client";

import { useEffect, useState } from "react";
import { api, type SimulatedTrade } from "@/lib/api";

const DEMO_USER_ID = "demo-user"; // swap for real auth once you add it

export default function SimulatorPage() {
  const [trades, setTrades] = useState<SimulatedTrade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    ticker: "",
    action: "BUY",
    quantity: "",
    entry_price: "",
    entry_date: new Date().toISOString().slice(0, 10),
    note: "",
  });

  async function loadTrades() {
    setLoading(true);
    const data = await api.getTrades(DEMO_USER_ID);
    setTrades(data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    loadTrades();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!form.ticker || !form.quantity || !form.entry_price) {
      setError("TICKER, QUANTITY, AND ENTRY PRICE ARE REQUIRED.");
      return;
    }

    try {
      await api.logTrade({
        user_id: DEMO_USER_ID,
        ticker: form.ticker.toUpperCase(),
        action: form.action,
        quantity: parseFloat(form.quantity),
        entry_price: parseFloat(form.entry_price),
        entry_date: form.entry_date,
        note: form.note || undefined,
      });
      setForm({ ...form, ticker: "", quantity: "", entry_price: "", note: "" });
      await loadTrades();
    } catch {
      setError("COULDN'T LOG THAT TRADE — IS THE TICKER TRACKED IN THE BACKEND YET?");
    }
  }

  const totalReturn =
    trades.length > 0
      ? trades.reduce((sum, t) => sum + (t.unrealized_return_pct ?? 0), 0) / trades.length
      : null;

  const inputClass =
    "rounded border border-panelBorder bg-black/40 px-3 py-2 text-sm text-matrix placeholder:text-matrixDim focus:border-matrix focus:outline-none focus:shadow-glow";

  return (
    <div>
      <h1 className="mb-1 text-xl tracking-wider glow-text">VIRTUAL SIMULATOR</h1>
      <p className="mb-6 text-sm text-matrixDim">
        Log the calls you would have made and track what they&apos;d be worth today. No real money involved.
      </p>

      <form onSubmit={handleSubmit} className="crt-panel mb-8 grid gap-3 rounded-lg p-5 sm:grid-cols-6">
        <input
          className={`col-span-2 ${inputClass}`}
          placeholder="TICKER (e.g. RELIANCE)"
          value={form.ticker}
          onChange={(e) => setForm({ ...form, ticker: e.target.value })}
        />
        <select
          className={inputClass}
          value={form.action}
          onChange={(e) => setForm({ ...form, action: e.target.value })}
        >
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input
          className={inputClass}
          placeholder="QUANTITY"
          type="number"
          value={form.quantity}
          onChange={(e) => setForm({ ...form, quantity: e.target.value })}
        />
        <input
          className={inputClass}
          placeholder="ENTRY PRICE ₹"
          type="number"
          value={form.entry_price}
          onChange={(e) => setForm({ ...form, entry_price: e.target.value })}
        />
        <input
          className={inputClass}
          type="date"
          value={form.entry_date}
          onChange={(e) => setForm({ ...form, entry_date: e.target.value })}
        />
        <input
          className={`col-span-6 sm:col-span-4 ${inputClass}`}
          placeholder="NOTE (optional — e.g. QGLP score 78)"
          value={form.note}
          onChange={(e) => setForm({ ...form, note: e.target.value })}
        />
        <button
          type="submit"
          className="col-span-6 rounded border border-matrix bg-matrixFaint px-4 py-2 text-sm font-bold text-matrix shadow-glow hover:bg-matrix hover:text-black sm:col-span-2"
        >
          LOG CALL
        </button>
        {error && <p className="col-span-6 text-sm text-bearish glow-text-red">{error}</p>}
      </form>

      {loading ? (
        <p className="text-sm text-matrixDim">LOADING TRADES…</p>
      ) : trades.length === 0 ? (
        <p className="text-sm text-matrixDim">NO CALLS LOGGED YET.</p>
      ) : (
        <div className="crt-panel overflow-hidden rounded-lg">
          {totalReturn !== null && (
            <div className="border-b border-panelBorder px-5 py-3 text-sm">
              AVG UNREALIZED RETURN:{" "}
              <span className={totalReturn >= 0 ? "text-bullish glow-text" : "text-bearish glow-text-red"}>
                {totalReturn.toFixed(2)}%
              </span>
            </div>
          )}
          <table className="w-full text-sm">
            <thead className="bg-black/30 text-left text-matrixDim">
              <tr>
                <th className="px-4 py-2 font-normal">TICKER</th>
                <th className="px-4 py-2 font-normal">ACTION</th>
                <th className="px-4 py-2 font-normal">QTY</th>
                <th className="px-4 py-2 font-normal">ENTRY</th>
                <th className="px-4 py-2 font-normal">NOW</th>
                <th className="px-4 py-2 font-normal">RETURN</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((t) => (
                <tr key={t.id} className="border-t border-panelBorder">
                  <td className="px-4 py-2">{t.ticker}</td>
                  <td className="px-4 py-2">{t.action}</td>
                  <td className="px-4 py-2">{t.quantity}</td>
                  <td className="px-4 py-2">₹{t.entry_price.toFixed(2)}</td>
                  <td className="px-4 py-2">{t.current_price ? `₹${t.current_price.toFixed(2)}` : "—"}</td>
                  <td
                    className={`px-4 py-2 ${
                      t.unrealized_return_pct !== null
                        ? t.unrealized_return_pct >= 0
                          ? "text-bullish glow-text"
                          : "text-bearish glow-text-red"
                        : "text-matrixDim"
                    }`}
                  >
                    {t.unrealized_return_pct !== null ? `${t.unrealized_return_pct.toFixed(2)}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
