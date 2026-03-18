"""RC Pulse CLI — Generate subscription health reports from RevenueCat Charts API."""

from __future__ import annotations

import asyncio
import os
import sys

import click

from .api import ChartsClient, AVAILABLE_CHARTS
from .analysis import (
    extract_metric_trend,
    compute_health_score,
    generate_risk_flags,
    generate_recommendations,
)
from .report import (
    generate_terminal_report,
    generate_markdown_report,
    generate_json_report,
    generate_html_report,
)


DEFAULT_CHARTS = [
    "revenue", "mrr", "actives", "churn",
    "trial_conversion_rate", "customers_new", "trials", "refund_rate",
]


async def _run_report(
    api_key: str,
    start_date: str | None,
    end_date: str | None,
    resolution: str,
    charts: list[str],
    fmt: str,
    output: str | None,
    segment: str | None,
) -> None:
    client = ChartsClient(api_key=api_key)
    try:
        # Resolve project
        projects = await client.list_projects()
        project_name = projects[0]["name"] if projects else "Unknown"
        click.echo(f"📡 Connected to project: {project_name}")

        # Progress callback
        def on_progress(chart: str, current: int, total: int):
            click.echo(f"  [{current}/{total}] Fetching {chart}...")

        # Fetch all chart data
        click.echo(f"📊 Fetching {len(charts)} charts (rate limited to 5/min)...")
        raw_data = await client.fetch_all_charts(
            charts=charts,
            start_date=start_date,
            end_date=end_date,
            resolution=resolution,
            on_progress=on_progress,
        )

        # Extract trends
        trends = {}
        for chart_name, data in raw_data.items():
            if "error" in data:
                click.echo(f"  ⚠️  Skipping {chart_name}: {data['error']}")
                continue
            trends[chart_name] = extract_metric_trend(data, chart_name)

        if not trends:
            click.echo("❌ No chart data retrieved. Check your API key and permissions.")
            return

        # Compute health score
        health = compute_health_score(trends)
        flags = generate_risk_flags(trends)
        recs = generate_recommendations(trends, health, flags)

        date_range = f"{start_date or 'earliest'} → {end_date or 'latest'}"

        # Generate report
        if fmt == "terminal":
            report = generate_terminal_report(
                trends, health, flags, recs, project_name, date_range
            )
        elif fmt == "markdown":
            report = generate_markdown_report(
                trends, health, flags, recs, project_name, date_range
            )
        elif fmt == "json":
            report = generate_json_report(
                trends, health, flags, recs, project_name, date_range
            )
        elif fmt == "html":
            report = generate_html_report(
                trends, health, flags, recs, project_name, date_range
            )
        else:
            report = generate_terminal_report(
                trends, health, flags, recs, project_name, date_range
            )

        if output:
            with open(output, "w") as f:
                f.write(report)
            click.echo(f"\n✅ Report saved to {output}")
        else:
            click.echo("\n" + report)

    finally:
        await client.close()


@click.group()
@click.version_option(version="0.1.0", prog_name="rc-pulse")
def main():
    """RC Pulse — AI-powered subscription health reports from RevenueCat Charts API."""
    pass


@main.command()
@click.option("--api-key", envvar="REVENUECAT_API_KEY", help="RevenueCat v2 secret API key")
@click.option("--start", "start_date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end", "end_date", default=None, help="End date (YYYY-MM-DD)")
@click.option(
    "--resolution", default="2", type=click.Choice(["0", "1", "2", "3", "4"]),
    help="Time resolution: 0=day, 1=week, 2=month, 3=quarter, 4=year"
)
@click.option(
    "--charts", default=None,
    help="Comma-separated chart names (default: revenue,mrr,active_subscriptions,churn,trial_conversion,new_customers,active_trials,refund_rate)"
)
@click.option(
    "--format", "fmt", default="terminal",
    type=click.Choice(["terminal", "markdown", "json", "html"]),
    help="Output format"
)
@click.option("--output", "-o", default=None, help="Save report to file")
@click.option("--segment", default=None, help="Segment dimension (e.g., country, platform)")
def report(api_key, start_date, end_date, resolution, charts, fmt, output, segment):
    """Generate a subscription health report."""
    if not api_key:
        click.echo("❌ API key required. Use --api-key or set REVENUECAT_API_KEY")
        sys.exit(1)

    chart_list = charts.split(",") if charts else DEFAULT_CHARTS
    asyncio.run(_run_report(api_key, start_date, end_date, resolution, chart_list, fmt, output, segment))


@main.command()
@click.option("--api-key", envvar="REVENUECAT_API_KEY", required=True)
def charts(api_key):
    """List available chart names."""
    click.echo("Available charts:")
    for c in AVAILABLE_CHARTS:
        click.echo(f"  • {c}")


@main.command()
@click.option("--api-key", envvar="REVENUECAT_API_KEY", required=True)
@click.argument("chart_name")
def options(api_key, chart_name):
    """Show available options (filters, segments) for a chart."""
    async def _show():
        client = ChartsClient(api_key=api_key)
        try:
            opts = await client.get_chart_options(chart_name)
            import json
            click.echo(json.dumps(opts, indent=2))
        finally:
            await client.close()
    asyncio.run(_show())


if __name__ == "__main__":
    main()
