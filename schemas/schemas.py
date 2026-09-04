from datetime import date

from pydantic import BaseModel, Field


class PriceBarOut(BaseModel):
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    class Config:
        from_attributes = True


class QGLPBreakdown(BaseModel):
    """Every pillar is returned separately — never collapse this into one
    number without showing the parts, that's how you end up with a black box."""
    quality_score: float = Field(ge=0, le=100)
    growth_score: float = Field(ge=0, le=100)
    longevity_score: float = Field(ge=0, le=100)
    price_score: float = Field(ge=0, le=100)
    composite_score: float = Field(ge=0, le=100)
    notes: list[str] = Field(default_factory=list)  # e.g. "Longevity: only 4 yrs of data available"


class TechnicalSignalOut(BaseModel):
    ticker: str
    close: float
    sma_200: float | None
    price_vs_sma200_pct: float | None
    volume_confirmed: bool
    signal: str          # "bullish" | "bearish" | "neutral"
    rsi_14: float | None = None


class FundamentalsOut(BaseModel):
    ticker: str
    pe_ratio: float | None
    pe_5yr_median: float | None
    debt_to_equity: float | None
    interest_coverage: float | None
    quarterly_revenue: list[float]
    quarterly_net_profit: list[float]
    quarterly_labels: list[str]


class SimulatedTradeIn(BaseModel):
    user_id: str
    ticker: str
    action: str  # BUY | SELL
    quantity: float
    entry_price: float
    entry_date: date
    note: str | None = None


class SimulatedTradeOut(SimulatedTradeIn):
    id: int
    current_price: float | None = None
    unrealized_return_pct: float | None = None
