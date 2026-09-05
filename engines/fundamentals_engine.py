"""
Fundamentals engine — computes PE, debt ratios, and prepares the quarterly
earnings series for charting. Kept separate from QGLP so it can be called
on its own (the frontend fundamentals tab doesn't need a full QGLP recompute).
"""
from dataclasses import dataclass
from statistics import median

from engines.qglp_engine import QuarterlyRecord


@dataclass
class FundamentalsResult:
    pe_ratio: float | None
    pe_5yr_median: float | None
    debt_to_equity: float | None
    interest_coverage: float | None
    quarterly_revenue: list[float]
    quarterly_net_profit: list[float]
    quarterly_labels: list[str]


class FundamentalsEngine:
    def compute_pe(self, price: float, trailing_eps: float | None) -> float | None:
        if not trailing_eps or trailing_eps <= 0:
            return None
        return round(price / trailing_eps, 2)

    def compute_pe_median(self, historical_pe: list[float]) -> float | None:
        clean = [p for p in historical_pe if p and p > 0]
        return round(median(clean), 2) if clean else None

    def compute_debt_to_equity(self, records: list[QuarterlyRecord]) -> float | None:
        latest = self._latest(records)
        if not latest or not latest.total_equity:
            return None
        return round(latest.total_debt / latest.total_equity, 2)

    def compute_interest_coverage(
        self, records: list[QuarterlyRecord], interest_expenses: list[float]
    ) -> float | None:
        """EBIT / interest expense — tells you if debt is serviceable, D/E alone doesn't."""
        latest = self._latest(records)
        if not latest or not interest_expenses or interest_expenses[-1] == 0:
            return None
        ebit = latest.ebitda  # simplification: swap for true EBIT if depreciation is tracked
        return round(ebit / interest_expenses[-1], 2)

    def build_quarterly_series(self, records: list[QuarterlyRecord]) -> tuple[list[float], list[float], list[str]]:
        ordered = sorted(records, key=lambda r: r.quarter_end)
        revenue = [r.revenue for r in ordered]
        net_profit = [r.net_profit for r in ordered]
        labels = [r.quarter_end for r in ordered]
        return revenue, net_profit, labels

    def compute(
        self,
        price: float,
        trailing_eps: float | None,
        historical_pe: list[float],
        records: list[QuarterlyRecord],
        interest_expenses: list[float],
    ) -> FundamentalsResult:
        revenue, net_profit, labels = self.build_quarterly_series(records)
        return FundamentalsResult(
            pe_ratio=self.compute_pe(price, trailing_eps),
            pe_5yr_median=self.compute_pe_median(historical_pe),
            debt_to_equity=self.compute_debt_to_equity(records),
            interest_coverage=self.compute_interest_coverage(records, interest_expenses),
            quarterly_revenue=revenue,
            quarterly_net_profit=net_profit,
            quarterly_labels=labels,
        )

    @staticmethod
    def _latest(records: list[QuarterlyRecord]) -> QuarterlyRecord | None:
        return max(records, key=lambda r: r.quarter_end) if records else None
