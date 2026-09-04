from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Stock(Base):
    """One row per NSE/BSE-listed company we track."""
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # e.g. RELIANCE.NS
    exchange: Mapped[str] = mapped_column(String(4))                          # NSE | BSE
    name: Mapped[str] = mapped_column(String(120))
    sector: Mapped[str | None] = mapped_column(String(80), nullable=True)

    prices: Mapped[list["PriceBar"]] = relationship(back_populates="stock")
    financials: Mapped[list["QuarterlyFinancial"]] = relationship(back_populates="stock")


class PriceBar(Base):
    """Daily OHLCV — the base data both the technical and price-pillar engines read from."""
    __tablename__ = "price_bars"
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uix_stock_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)

    stock: Mapped["Stock"] = relationship(back_populates="prices")


class QuarterlyFinancial(Base):
    """One row per reported quarter — feeds growth, quality, and fundamentals engines."""
    __tablename__ = "quarterly_financials"
    __table_args__ = (UniqueConstraint("stock_id", "quarter_end", name="uix_stock_quarter"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    quarter_end: Mapped[date] = mapped_column(Date, index=True)

    revenue: Mapped[float] = mapped_column(Float)
    ebitda: Mapped[float] = mapped_column(Float)
    net_profit: Mapped[float] = mapped_column(Float)
    eps: Mapped[float] = mapped_column(Float)

    total_debt: Mapped[float] = mapped_column(Float)
    total_equity: Mapped[float] = mapped_column(Float)
    interest_expense: Mapped[float] = mapped_column(Float)
    cfo: Mapped[float] = mapped_column(Float)          # cash flow from operations
    roce_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    promoter_holding_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    dividend_payout_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    stock: Mapped["Stock"] = relationship(back_populates="financials")


class QGLPScoreSnapshot(Base):
    """Cached engine output — recomputing QGLP on every page view is wasteful."""
    __tablename__ = "qglp_score_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quality_score: Mapped[float] = mapped_column(Float)
    growth_score: Mapped[float] = mapped_column(Float)
    longevity_score: Mapped[float] = mapped_column(Float)
    price_score: Mapped[float] = mapped_column(Float)
    composite_score: Mapped[float] = mapped_column(Float)


class SimulatedTrade(Base):
    """A hypothetical 'what if I had bought this' call the user logs in the simulator."""
    __tablename__ = "simulated_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)

    action: Mapped[str] = mapped_column(String(4))       # BUY | SELL
    quantity: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    entry_date: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(String(240), nullable=True)  # e.g. "QGLP score 78"

    stock: Mapped["Stock"] = relationship()
