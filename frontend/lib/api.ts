const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export type StockSummary = {
  ticker: string;
  name: string;
  exchange: string;
  sector: string | null;
};

export type QGLPBreakdown = {
  quality_score: number;
  growth_score: number;
  longevity_score: number;
  price_score: number;
  composite_score: number;
  notes: string[];
};

export type TechnicalSignal = {
  ticker: string;
  close: number;
  sma_200: number | null;
  price_vs_sma200_pct: number | null;
  volume_confirmed: boolean;
  signal: "bullish" | "bearish" | "neutral";
  rsi_14: number | null;
};

export type Fundamentals = {
  ticker: string;
  pe_ratio: number | null;
  pe_5yr_median: number | null;
  debt_to_equity: number | null;
  interest_coverage: number | null;
  quarterly_revenue: number[];
  quarterly_net_profit: number[];
  quarterly_labels: string[];
};

export type NewsItem = {
  title: string;
  source: string;
  url: string;
  published_at: string;
};

export type SimulatedTrade = {
  id: number;
  user_id: string;
  ticker: string;
  action: string;
  quantity: number;
  entry_price: number;
  entry_date: string;
  note: string | null;
  current_price: number | null;
  unrealized_return_pct: number | null;
};

export const api = {
  listStocks: (q = "") => getJson<StockSummary[]>(`/api/v1/stocks/search?q=${encodeURIComponent(q)}`),
  getQglp: (ticker: string) => getJson<QGLPBreakdown>(`/api/v1/qglp/${ticker}`),
  getTechnical: (ticker: string) => getJson<TechnicalSignal>(`/api/v1/technical/${ticker}`),
  getFundamentals: (ticker: string) => getJson<Fundamentals>(`/api/v1/fundamentals/${ticker}`),
  getNews: (companyName: string) => getJson<NewsItem[]>(`/api/v1/news/${encodeURIComponent(companyName)}`),
  getTrades: (userId: string) => getJson<SimulatedTrade[]>(`/api/v1/simulator/trades/${userId}`),
  logTrade: async (trade: {
    user_id: string;
    ticker: string;
    action: string;
    quantity: number;
    entry_price: number;
    entry_date: string;
    note?: string;
  }) => {
    const res = await fetch(`${API_BASE}/api/v1/simulator/trades`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(process.env.NEXT_PUBLIC_SIMULATOR_API_KEY
          ? { "X-API-Key": process.env.NEXT_PUBLIC_SIMULATOR_API_KEY }
          : {}),
      },
      body: JSON.stringify(trade),
    });
    if (!res.ok) throw new Error("Failed to log trade");
    return res.json();
  },
};
