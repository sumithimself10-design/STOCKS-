"""
Everything that talks to an external, unreliable source lives here — never
inside an engine or a router. This is the only file that should ever import
yfinance or nsepython, so when NSE breaks a function again (see nsepython's
open GitHub issues on get_beta / dividend_timeline), you fix it in one place.
"""
import logging
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    Thin wrapper with two responsibilities: normalize ticker suffixes for
    NSE (.NS) / BSE (.BO), and shield the rest of the app from partial or
    broken upstream responses instead of letting a KeyError bubble up.
    """

    def normalize_ticker(self, symbol: str, exchange: str) -> str:
        symbol = symbol.upper().strip()
        if symbol.endswith((".NS", ".BO")):
            return symbol
        suffix = ".NS" if exchange.upper() == "NSE" else ".BO"
        return f"{symbol}{suffix}"

    def get_price_history(self, ticker: str, lookback_days: int = 400) -> pd.DataFrame:
        """Returns a DataFrame with columns [close, volume], oldest -> newest.
        400-day default lookback so a 200-day SMA always has a full window."""
        try:
            start = date.today() - timedelta(days=lookback_days)
            data = yf.download(ticker, start=start, progress=False, auto_adjust=True)
            if data.empty:
                logger.warning("No price data returned for %s", ticker)
                return pd.DataFrame(columns=["close", "volume"])
            out = data[["Close", "Volume"]].rename(columns={"Close": "close", "Volume": "volume"})
            return out.reset_index(drop=True)
        except Exception:
            logger.exception("Price fetch failed for %s", ticker)
            return pd.DataFrame(columns=["close", "volume"])

    def get_trailing_eps_and_pe(self, ticker: str) -> tuple[float | None, float | None]:
        try:
            info = yf.Ticker(ticker).info
            return info.get("trailingEps"), info.get("trailingPE")
        except Exception:
            logger.exception("Fundamentals fetch failed for %s", ticker)
            return None, None

    def get_quarterly_financials(self, ticker: str) -> pd.DataFrame:
        """
        yfinance quarterly statements as a fallback source. For production,
        cross-check this against NSE's own results/corporate-announcements
        endpoint — yfinance's Indian-company coverage is inconsistent on
        line items like CFO and promoter holding.
        """
        try:
            tk = yf.Ticker(ticker)
            income = tk.quarterly_financials.T
            cashflow = tk.quarterly_cashflow.T
            balance = tk.quarterly_balance_sheet.T
            merged = income.join(cashflow, how="outer", lsuffix="_inc").join(
                balance, how="outer", rsuffix="_bal"
            )
            return merged
        except Exception:
            logger.exception("Quarterly financials fetch failed for %s", ticker)
            return pd.DataFrame()


# Module-level singleton — stateless, safe to share across requests
data_fetcher = DataFetcher()
