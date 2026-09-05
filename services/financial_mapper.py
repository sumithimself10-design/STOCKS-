"""
Maps yfinance's merged quarterly income/cashflow/balance-sheet DataFrame
into engine-ready QuarterlyRecord objects.

Field names below were verified against yfinance's own source
(yfinance/utils.py:camel2title, called with acronyms=["EBIT","EBITDA",
"EPS","NI"] for the income statement) rather than assumed from memory —
that's why "EBIT"/"EBITDA" stay upper-case while everything else is
title-cased with spaces inserted at lower-to-upper transitions.
"""
from engines.qglp_engine import QuarterlyRecord, compute_roce


def to_quarterly_records(df) -> list[QuarterlyRecord]:
    records = []
    for idx, row in df.iterrows():
        ebit = _get(row, "EBIT")
        invested_capital = _get(row, "Invested Capital")
        total_assets = _get(row, "Total Assets")
        current_liabilities = _get(row, "Current Liabilities")

        roce_pct = compute_roce(
            ebit=ebit,
            invested_capital=invested_capital,
            total_assets=total_assets,
            current_liabilities=current_liabilities,
        )

        records.append(
            QuarterlyRecord(
                quarter_end=str(idx.date()) if hasattr(idx, "date") else str(idx),
                revenue=_get(row, "Total Revenue") or 0.0,
                net_profit=_get(row, "Net Income") or 0.0,
                eps=_get(row, "Basic EPS") or 0.0,
                roce_pct=roce_pct,
                total_debt=_get(row, "Total Debt") or 0.0,
                total_equity=_get(row, "Total Equity Gross Minority Interest") or 0.0,
                cfo=_get(row, "Operating Cash Flow") or 0.0,
                ebitda=_get(row, "EBITDA") or 0.0,
                # Not available from yfinance — populate from a separate NSE
                # corporate-announcements source if you want these scored.
                promoter_holding_pct=None,
                dividend_payout_pct=None,
            )
        )
    return records


def get_interest_expense(df) -> list[float]:
    """Ordered oldest -> newest, for interest coverage calculations."""
    return [_get(row, "Interest Expense") or 0.0 for _, row in df.sort_index().iterrows()]


def _get(row, label: str) -> float | None:
    value = row.get(label)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
