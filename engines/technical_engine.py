"""
Technical engine — primary signal is price vs. 200-day SMA confirmed by
volume, which is the trend filter with the broadest consensus behind it.
RSI is computed as secondary context, never the primary call.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class TechnicalSignal:
    close: float
    sma_200: float | None
    price_vs_sma200_pct: float | None
    volume_confirmed: bool
    signal: str  # "bullish" | "bearish" | "neutral"
    rsi_14: float | None = None


class TechnicalEngine:
    def __init__(self, sma_window: int = 200, volume_lookback: int = 20, rsi_window: int = 14):
        self.sma_window = sma_window
        self.volume_lookback = volume_lookback
        self.rsi_window = rsi_window

    def compute(self, price_df: pd.DataFrame) -> TechnicalSignal:
        """
        price_df: DataFrame with columns ['close', 'volume'], sorted oldest -> newest.
        """
        if len(price_df) < self.sma_window:
            close = float(price_df["close"].iloc[-1])
            return TechnicalSignal(
                close=close, sma_200=None, price_vs_sma200_pct=None,
                volume_confirmed=False, signal="neutral",
                rsi_14=self._rsi(price_df["close"]),
            )

        sma_200 = price_df["close"].rolling(self.sma_window).mean().iloc[-1]
        close = float(price_df["close"].iloc[-1])
        pct_vs_sma = ((close - sma_200) / sma_200) * 100

        avg_volume = price_df["volume"].tail(self.volume_lookback).mean()
        latest_volume = price_df["volume"].iloc[-1]
        volume_confirmed = latest_volume > avg_volume * 1.2  # 20% above recent average

        if close > sma_200 and volume_confirmed:
            signal = "bullish"
        elif close < sma_200 and volume_confirmed:
            signal = "bearish"
        else:
            signal = "neutral"  # trend exists but not volume-backed, or price is chopping at the line

        return TechnicalSignal(
            close=close,
            sma_200=round(float(sma_200), 2),
            price_vs_sma200_pct=round(float(pct_vs_sma), 2),
            volume_confirmed=bool(volume_confirmed),
            signal=signal,
            rsi_14=self._rsi(price_df["close"]),
        )

    def _rsi(self, close: pd.Series) -> float | None:
        if len(close) < self.rsi_window + 1:
            return None
        delta = close.diff().dropna()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.rsi_window).mean().iloc[-1]
        avg_loss = loss.rolling(self.rsi_window).mean().iloc[-1]
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return round(float(100 - (100 / (1 + rs))), 2)
