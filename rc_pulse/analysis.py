"""Trend detection, health scoring, and statistical analysis."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MetricTrend:
    """Trend analysis for a single metric."""
    name: str
    display_name: str
    values: list[float]
    dates: list[str]
    unit: str = ""
    
    @property
    def current(self) -> float | None:
        return self.values[-1] if self.values else None

    @property
    def previous(self) -> float | None:
        return self.values[-2] if len(self.values) >= 2 else None

    @property
    def period_change(self) -> float | None:
        if self.current is not None and self.previous is not None and self.previous != 0:
            return ((self.current - self.previous) / self.previous) * 100
        return None

    @property
    def mean(self) -> float | None:
        return statistics.mean(self.values) if self.values else None

    @property
    def std_dev(self) -> float | None:
        return statistics.stdev(self.values) if len(self.values) >= 2 else None

    @property
    def trend_direction(self) -> str:
        """Detect overall trend using simple linear regression."""
        if len(self.values) < 3:
            return "insufficient_data"
        n = len(self.values)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(self.values)
        numerator = sum((x[i] - x_mean) * (self.values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        if denominator == 0:
            return "flat"
        slope = numerator / denominator
        # Normalize slope relative to mean
        if y_mean == 0:
            return "flat"
        relative_slope = (slope / y_mean) * 100
        if relative_slope > 1:
            return "up"
        elif relative_slope < -1:
            return "down"
        return "flat"

    @property
    def trend_emoji(self) -> str:
        d = self.trend_direction
        return {"up": "📈", "down": "📉", "flat": "➡️"}.get(d, "❓")

    @property
    def consecutive_direction(self) -> tuple[str, int]:
        """Count consecutive increases or decreases from most recent."""
        if len(self.values) < 2:
            return ("none", 0)
        direction = None
        count = 0
        for i in range(len(self.values) - 1, 0, -1):
            diff = self.values[i] - self.values[i - 1]
            if diff > 0:
                current_dir = "increase"
            elif diff < 0:
                current_dir = "decrease"
            else:
                current_dir = "flat"
            if direction is None:
                direction = current_dir
                count = 1
            elif current_dir == direction:
                count += 1
            else:
                break
        return (direction or "none", count)

    def moving_average(self, window: int = 3) -> list[float]:
        if len(self.values) < window:
            return self.values[:]
        result = []
        for i in range(len(self.values)):
            start = max(0, i - window + 1)
            result.append(statistics.mean(self.values[start:i + 1]))
        return result

    @property
    def risk_flags(self) -> list[str]:
        """Generate risk flags for this metric."""
        flags = []
        direction, count = self.consecutive_direction
        if direction == "decrease" and count >= 3:
            flags.append(f"{self.display_name} has declined for {count} consecutive periods")
        if self.std_dev and self.mean and self.mean != 0:
            cv = self.std_dev / abs(self.mean)
            if cv > 0.3:
                flags.append(f"{self.display_name} shows high volatility (CV={cv:.1%})")
        if self.period_change is not None and self.period_change < -10:
            flags.append(f"{self.display_name} dropped {abs(self.period_change):.1f}% last period")
        return flags


@dataclass
class HealthScore:
    """Subscription health score across multiple dimensions."""
    growth: float = 0.0
    retention: float = 0.0
    conversion: float = 0.0
    revenue_quality: float = 0.0
    momentum: float = 0.0

    @property
    def overall(self) -> float:
        weights = {
            "growth": 0.25,
            "retention": 0.25,
            "conversion": 0.20,
            "revenue_quality": 0.15,
            "momentum": 0.15,
        }
        return sum(
            getattr(self, dim) * w for dim, w in weights.items()
        )

    @property
    def grade(self) -> str:
        score = self.overall
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 55:
            return "C"
        elif score >= 40:
            return "D"
        return "F"

    @property
    def grade_emoji(self) -> str:
        g = self.grade
        return {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "⛔"}.get(g, "❓")

    def to_dict(self) -> dict:
        return {
            "growth": round(self.growth, 1),
            "retention": round(self.retention, 1),
            "conversion": round(self.conversion, 1),
            "revenue_quality": round(self.revenue_quality, 1),
            "momentum": round(self.momentum, 1),
            "overall": round(self.overall, 1),
            "grade": self.grade,
        }


def extract_metric_trend(chart_data: dict, metric_name: str) -> MetricTrend:
    """Extract a MetricTrend from raw chart API data."""
    values_raw = chart_data.get("values", [])
    measures = chart_data.get("measures", [])
    display_name = chart_data.get("display_name", metric_name)
    unit = measures[0].get("unit", "") if measures else ""
    
    # Group by cohort, take measure 0 (primary)
    primary_values = [v for v in values_raw if v.get("measure") == 0]
    values = [v["value"] for v in primary_values]
    dates = [
        datetime.utcfromtimestamp(v["cohort"]).strftime("%Y-%m-%d")
        for v in primary_values
    ]
    
    return MetricTrend(
        name=metric_name,
        display_name=display_name,
        values=values,
        dates=dates,
        unit=unit,
    )


def compute_health_score(trends: dict[str, MetricTrend]) -> HealthScore:
    """Compute a health score from metric trends."""
    score = HealthScore()

    # Growth (MRR trend + new customers)
    growth_signals = []
    if "mrr" in trends:
        mrr = trends["mrr"]
        if mrr.trend_direction == "up":
            growth_signals.append(80)
        elif mrr.trend_direction == "flat":
            growth_signals.append(60)
        else:
            growth_signals.append(30)
        if mrr.period_change is not None:
            growth_signals.append(min(100, max(0, 50 + mrr.period_change * 5)))
    if "customers_new" in trends:
        nc = trends["customers_new"]
        if nc.trend_direction == "up":
            growth_signals.append(80)
        elif nc.trend_direction == "flat":
            growth_signals.append(60)
        else:
            growth_signals.append(35)
    score.growth = statistics.mean(growth_signals) if growth_signals else 50

    # Retention (churn)
    if "churn" in trends:
        churn = trends["churn"]
        if churn.current is not None:
            # Lower churn = better retention
            if churn.current < 3:
                score.retention = 90
            elif churn.current < 5:
                score.retention = 75
            elif churn.current < 8:
                score.retention = 60
            elif churn.current < 12:
                score.retention = 45
            else:
                score.retention = 25
            # Bonus/penalty for trend
            if churn.trend_direction == "down":
                score.retention = min(100, score.retention + 10)
            elif churn.trend_direction == "up":
                score.retention = max(0, score.retention - 10)
    else:
        score.retention = 50

    # Conversion
    if "trial_conversion_rate" in trends:
        tc = trends["trial_conversion_rate"]
        if tc.current is not None:
            score.conversion = min(100, max(0, tc.current * 1.5))
    else:
        score.conversion = 50

    # Revenue quality (stability)
    if "revenue" in trends:
        rev = trends["revenue"]
        if rev.std_dev is not None and rev.mean and rev.mean != 0:
            cv = rev.std_dev / abs(rev.mean)
            score.revenue_quality = min(100, max(0, (1 - cv) * 100))
        else:
            score.revenue_quality = 50
    else:
        score.revenue_quality = 50

    # Momentum (recent 3 months vs historical)
    momentum_signals = []
    for name in ["revenue", "mrr", "actives"]:
        if name in trends:
            t = trends[name]
            if len(t.values) >= 6:
                recent = statistics.mean(t.values[-3:])
                historical = statistics.mean(t.values[:-3])
                if historical != 0:
                    pct = ((recent - historical) / historical) * 100
                    momentum_signals.append(min(100, max(0, 50 + pct * 3)))
    score.momentum = statistics.mean(momentum_signals) if momentum_signals else 50

    return score


def generate_risk_flags(trends: dict[str, MetricTrend]) -> list[str]:
    """Aggregate all risk flags from metric trends."""
    flags = []
    for trend in trends.values():
        flags.extend(trend.risk_flags)
    return flags


def generate_recommendations(
    trends: dict[str, MetricTrend],
    health: HealthScore,
    flags: list[str],
) -> list[str]:
    """Generate strategic recommendations based on analysis."""
    recs = []

    if health.retention < 60:
        recs.append(
            "🔴 **Retention needs attention.** Consider implementing win-back campaigns, "
            "improving onboarding, or surveying churned users to identify pain points."
        )
    if health.growth < 50:
        recs.append(
            "📉 **Growth is stalling.** Evaluate your acquisition channels, consider "
            "A/B testing paywalls, and explore new markets or platforms."
        )
    if health.conversion < 50:
        recs.append(
            "🔄 **Trial conversion is low.** Optimize your trial experience — shorter trials "
            "with better onboarding often outperform longer trials with no engagement."
        )

    # Check for MRR decline
    if "mrr" in trends:
        direction, count = trends["mrr"].consecutive_direction
        if direction == "decrease" and count >= 2:
            recs.append(
                f"⚠️ **MRR has declined for {count} consecutive periods.** Investigate "
                "whether this is driven by increased churn or declining new subscriptions."
            )

    # Check for revenue concentration (if we had segment data)
    if "actives" in trends and "customers_new" in trends:
        subs = trends["actives"]
        nc = trends["customers_new"]
        if subs.trend_direction == "down" and nc.trend_direction == "down":
            recs.append(
                "📊 **Both active subscriptions and new customers are declining.** "
                "This suggests a top-of-funnel problem. Focus on acquisition before retention."
            )

    if health.overall >= 75:
        recs.append(
            "🟢 **Overall health is strong.** Focus on maintaining momentum and "
            "experimenting with upsells, annual plan incentives, or price optimization."
        )

    return recs
