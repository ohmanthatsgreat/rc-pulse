"""RevenueCat Charts API v2 client with rate limiting."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any

import httpx

BASE_URL = "https://api.revenuecat.com/v2"

# Charts API rate limit: 5 req/min
RATE_LIMIT = 5
RATE_WINDOW = 60  # seconds

AVAILABLE_CHARTS = [
    "revenue",
    "mrr",
    "actives",
    "actives_movement",
    "actives_new",
    "arr",
    "churn",
    "cohort_explorer",
    "conversion_to_paying",
    "customers_new",
    "customers_active",
    "ltv_per_customer",
    "ltv_per_paying_customer",
    "mrr_movement",
    "refund_rate",
    "subscription_retention",
    "subscription_status",
    "trials",
    "trials_movement",
    "trials_new",
    "trial_conversion_rate",
]


@dataclass
class RateLimiter:
    """Simple sliding window rate limiter."""
    max_requests: int = RATE_LIMIT
    window_seconds: float = RATE_WINDOW
    _timestamps: list[float] = field(default_factory=list)

    async def acquire(self) -> None:
        now = time.monotonic()
        # Remove timestamps outside the window
        self._timestamps = [
            t for t in self._timestamps if now - t < self.window_seconds
        ]
        if len(self._timestamps) >= self.max_requests:
            # Wait until the oldest timestamp expires
            wait_time = self.window_seconds - (now - self._timestamps[0]) + 0.1
            await asyncio.sleep(wait_time)
        self._timestamps.append(time.monotonic())


@dataclass
class ChartsClient:
    """RevenueCat Charts API v2 client."""
    api_key: str
    project_id: str | None = None
    _client: httpx.AsyncClient | None = field(default=None, repr=False)
    _limiter: RateLimiter = field(default_factory=RateLimiter)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers=self.headers,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        await self._limiter.acquire()
        client = await self._ensure_client()
        resp = await client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def list_projects(self) -> list[dict]:
        data = await self._get("/projects")
        return data.get("items", [])

    async def resolve_project_id(self) -> str:
        if self.project_id:
            return self.project_id
        projects = await self.list_projects()
        if not projects:
            raise ValueError("No projects found for this API key")
        self.project_id = projects[0]["id"]
        return self.project_id

    async def get_chart_options(self, chart_name: str) -> dict:
        pid = await self.resolve_project_id()
        return await self._get(f"/projects/{pid}/charts/{chart_name}/options")

    async def get_chart_data(
        self,
        chart_name: str,
        start_date: str | None = None,
        end_date: str | None = None,
        resolution: str = "2",  # month
        segment: str | None = None,
        filters: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        pid = await self.resolve_project_id()
        params: dict[str, str] = {"resolution": resolution}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if segment:
            params["segment"] = segment
        if filters:
            for k, v in filters.items():
                params[f"filter[{k}]"] = v
        return await self._get(f"/projects/{pid}/charts/{chart_name}", params=params)

    async def get_overview(self) -> dict[str, Any]:
        pid = await self.resolve_project_id()
        return await self._get(f"/projects/{pid}/metrics/overview")

    async def fetch_all_charts(
        self,
        charts: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        resolution: str = "2",
        on_progress: Any = None,
    ) -> dict[str, dict]:
        """Fetch multiple charts, respecting rate limits."""
        if charts is None:
            charts = [
                "revenue", "mrr", "active_subscriptions", "churn",
                "trial_conversion", "new_customers", "active_trials",
                "refund_rate",
            ]
        results = {}
        for i, chart in enumerate(charts):
            if on_progress:
                on_progress(chart, i + 1, len(charts))
            try:
                data = await self.get_chart_data(
                    chart, start_date=start_date, end_date=end_date,
                    resolution=resolution,
                )
                results[chart] = data
            except httpx.HTTPStatusError as e:
                results[chart] = {"error": str(e), "status_code": e.response.status_code}
        return results
