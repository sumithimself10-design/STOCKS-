"""
QGLP engine — quantifies Raamdeo Agrawal's Quality / Growth / Longevity / Price
framework against a company's reported quarterly financials.

Deliberately pure: every function takes plain data (lists/dicts) and returns
plain data. No DB session, no HTTP client in here — that keeps it unit-testable
without spinning up Postgres, and reusable if you ever want a CLI or a notebook
version of the same scoring.
"""
from dataclasses import dataclass, field
from statistics import mean, pstdev


@dataclass
class QuarterlyRecord:
    quarter_end: str
    revenue: float
    net_profit: float
    eps: float
    roce_pct: float | None
    total_debt: float
    total_equity: float
    cfo: float
    ebitda: float
    promoter_holding_pct: float | None = None
    dividend_payout_pct: float | None = None


@dataclass
class QGLPResult:
    quality_score: float
    growth_score: float
    longevity_score: float
    price_score: float
    composite_score: float
    notes: list[str] = field(default_factory=list)


class QGLPEngine:
    def __init__(
        self,
        weight_quality: float = 0.30,
        weight_growth: float = 0.30,
        weight_longevity: float = 0.20,
        weight_price: float = 0.20,
    ):
        self.weights = {
            "quality": weight_quality,
            "growth": weight_growth,
            "longevity": weight_longevity,
            "price": weight_price,
        }

    # ---- Quality -----------------------------------------------------
    def score_quality(self, records: list[QuarterlyRecord]) -> tuple[float, list[str]]:
        notes = []
        if len(records) < 4:
            notes.append("Quality: fewer than 4 quarters available, score is low-confidence")

        roce_values = [r.roce_pct for r in records if r.roce_pct is not None]
        roce_pass = mean(v > 15 for v in roce_values) if roce_values else 0

        de_ratios = [r.total_debt / r.total_equity for r in records if r.total_equity]
        de_pass = mean(d < 1 for d in de_ratios) if de_ratios else 0

        cfo_total = sum(r.cfo for r in records)
        ebitda_total = sum(r.ebitda for r in records)
        cfo_conversion = (cfo_total / ebitda_total) if ebitda_total else 0
        cfo_pass = 1.0 if cfo_conversion > 0.70 else max(cfo_conversion / 0.70, 0)

        score = (roce_pass * 40) + (de_pass * 35) + (cfo_pass * 25)
        return round(min(score, 100), 1), notes

    # ---- Growth --------------------------------------------------------
    def score_growth(self, records: list[QuarterlyRecord]) -> tuple[float, list[str]]:
        notes = []
        if len(records) < 5:
            notes.append("Growth: CAGR calculated on limited history, treat as indicative only")
            return 0.0, notes

        ordered = sorted(records, key=lambda r: r.quarter_end)
        revenue_growth_rates = [
            (b.revenue - a.revenue) / a.revenue
            for a, b in zip(ordered, ordered[1:])
            if a.revenue
        ]
        if not revenue_growth_rates:
            return 0.0, notes

        avg_growth = mean(revenue_growth_rates)
        consistency_penalty = pstdev(revenue_growth_rates) if len(revenue_growth_rates) > 1 else 0

        # Reward steady double-digit annualised growth, penalise volatility
        growth_component = min(max(avg_growth * 4, 0) * 100, 70)
        consistency_component = max(30 - consistency_penalty * 100, 0)
        score = growth_component + consistency_component
        return round(min(score, 100), 1), notes

    # ---- Longevity -------------------------------------------------------
    def score_longevity(self, records: list[QuarterlyRecord]) -> tuple[float, list[str]]:
        """The softest pillar — flagged as such rather than dressed up as precise."""
        notes = ["Longevity is a proxy score: streak length + payout consistency, "
                 "not a true moat assessment"]
        if len(records) < 8:
            notes.append("Longevity: under 2 years of data, confidence is low")

        roce_streak = sum(1 for r in records if (r.roce_pct or 0) > 15)
        streak_component = min(roce_streak / max(len(records), 1), 1) * 60

        payouts = [r.dividend_payout_pct for r in records if r.dividend_payout_pct is not None]
        payout_in_band = mean(0 <= p <= 30 for p in payouts) if payouts else 0.5
        payout_component = payout_in_band * 40

        score = streak_component + payout_component
        return round(min(score, 100), 1), notes

    # ---- Price -------------------------------------------------------
    def score_price(self, current_pe: float | None, pe_5yr_median: float | None) -> tuple[float, list[str]]:
        notes = []
        if current_pe is None or pe_5yr_median is None or pe_5yr_median <= 0:
            notes.append("Price: insufficient PE history to score, defaulted to neutral 50")
            return 50.0, notes

        discount = (pe_5yr_median - current_pe) / pe_5yr_median
        # Trading at a discount to its own history scores higher; big premium scores low
        score = 50 + (discount * 100)
        return round(min(max(score, 0), 100), 1), notes

    # ---- Composite -------------------------------------------------------
    def compute(
        self,
        records: list[QuarterlyRecord],
        current_pe: float | None,
        pe_5yr_median: float | None,
    ) -> QGLPResult:
        quality, n1 = self.score_quality(records)
        growth, n2 = self.score_growth(records)
        longevity, n3 = self.score_longevity(records)
        price, n4 = self.score_price(current_pe, pe_5yr_median)

        composite = (
            quality * self.weights["quality"]
            + growth * self.weights["growth"]
            + longevity * self.weights["longevity"]
            + price * self.weights["price"]
        )

        return QGLPResult(
            quality_score=quality,
            growth_score=growth,
            longevity_score=longevity,
            price_score=price,
            composite_score=round(composite, 1),
            notes=[*n1, *n2, *n3, *n4],
        )
