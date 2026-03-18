# RC Pulse 📊 — AI-Powered Subscription Health Reports

**Turn your RevenueCat Charts API data into actionable strategic insights.**

RC Pulse is a Python CLI tool that connects to the [RevenueCat Charts API](https://www.revenuecat.com/docs/api-v2), pulls your key subscription metrics, and generates an AI-analyzed health report — complete with trend analysis, risk flags, and strategic recommendations.

Built by [Cleo Sterling](https://twitter.com/CleoSterlingAI), an AI agent, as a demonstration of what's possible when you combine RevenueCat's Charts API with autonomous AI agents.

> ⚠️ **Disclosure:** Cleo Sterling is an AI agent. This tool was built autonomously as part of RevenueCat's hiring process for the Agentic AI Developer & Growth Advocate role.

## Why RC Pulse?

Most developers check their RevenueCat dashboard manually. But what if your subscription data could *talk back*?

RC Pulse doesn't just show you numbers — it tells you what they **mean**:

- 📉 "MRR has declined 3 consecutive months — investigate churn in the annual cohort"
- 🚀 "Trial conversion spiked 12% after your paywall change — double down"
- ⚠️ "Revenue concentration: 78% from iOS. Consider platform diversification."

## Features

- **Multi-metric analysis** — Revenue, MRR, Active Subscriptions, Churn, Trials, New Customers, and more
- **Trend detection** — Automatically identifies upward/downward trends across all metrics
- **Segmented insights** — Break down by platform, country, product duration, store
- **AI-powered analysis** — Uses LLMs to generate strategic recommendations (optional)
- **Multiple output formats** — Terminal, Markdown, HTML, JSON
- **Zero config** — Just provide your API key and go

## Quick Start

### Installation

```bash
pip install rc-pulse
```

Or clone and install locally:

```bash
git clone https://github.com/ohmanthatsgreat/rc-pulse.git
cd rc-pulse
pip install -e .
```

### Basic Usage

```bash
# Generate a health report
rc-pulse report --api-key YOUR_RC_SECRET_KEY

# Specify date range
rc-pulse report --api-key YOUR_KEY --start 2025-01-01 --end 2026-03-18

# Output as Markdown
rc-pulse report --api-key YOUR_KEY --format markdown --output report.md

# Output as HTML (great for sharing)
rc-pulse report --api-key YOUR_KEY --format html --output report.html

# Include AI analysis (requires OPENAI_API_KEY)
rc-pulse report --api-key YOUR_KEY --ai-analysis
```

### Available Charts

RC Pulse supports all Charts API endpoints:

| Chart | Description |
|-------|-------------|
| `revenue` | Total revenue by period |
| `mrr` | Monthly Recurring Revenue |
| `active_subscriptions` | Current active subscribers |
| `churn` | Churn rate over time |
| `active_trials` | Active trial count |
| `trial_conversion` | Trial → Paid conversion rate |
| `new_customers` | New customer acquisition |
| `refund_rate` | Refund rate tracking |

### Segmented Reports

```bash
# Break down revenue by country
rc-pulse report --api-key YOUR_KEY --segment country

# Compare monthly vs annual subscribers
rc-pulse report --api-key YOUR_KEY --segment product_duration

# Platform breakdown
rc-pulse report --api-key YOUR_KEY --segment platform
```

## How It Works

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  RevenueCat   │────▶│   RC Pulse CLI    │────▶│  Health Report   │
│  Charts API   │     │                  │     │                 │
│              │     │  • Fetch metrics  │     │  • Trends       │
│  Revenue     │     │  • Detect trends  │     │  • Risk flags   │
│  MRR         │     │  • Score health   │     │  • Scores       │
│  Churn       │     │  • AI analysis    │     │  • Recs         │
│  Trials      │     │  (optional)       │     │  • Actions      │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

## Architecture

RC Pulse follows a simple pipeline:

1. **Fetch** — Calls the RevenueCat Charts API v2 for each metric, respecting rate limits (5 req/min)
2. **Transform** — Normalizes time-series data and computes derived metrics (growth rates, moving averages, period-over-period changes)
3. **Analyze** — Runs statistical trend detection and scores subscription health across 5 dimensions
4. **Report** — Generates formatted output with insights, risk flags, and recommendations
5. **AI Enhancement** (optional) — Passes the analysis to an LLM for strategic narrative and recommendations

## Health Score Methodology

RC Pulse scores your subscription business across 5 dimensions (0-100):

| Dimension | What it measures |
|-----------|-----------------|
| **Growth** | MRR trend + new customer acquisition rate |
| **Retention** | Churn rate + subscription renewal patterns |
| **Conversion** | Trial → paid + initial conversion rates |
| **Revenue Quality** | Revenue concentration + ARPU trends |
| **Momentum** | Recent performance vs. historical baseline |

The overall **Pulse Score** is a weighted average, giving you a single number to track your subscription health over time.

## Configuration

Create a `.rcpulse.yaml` for persistent config:

```yaml
api_key: sk_your_key_here
default_format: markdown
default_resolution: month
charts:
  - revenue
  - mrr
  - active_subscriptions
  - churn
  - trial_conversion
  - new_customers
ai:
  enabled: true
  provider: openai
  model: gpt-4o
```

## API Rate Limits

RevenueCat's Charts API has a rate limit of **5 requests per minute**. RC Pulse handles this automatically with built-in rate limiting and retry logic. A full report (8 charts) takes approximately 2 minutes to generate.

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.

---

Built with 🤖 by [Cleo Sterling](https://twitter.com/CleoSterlingAI) — an AI agent that actually runs businesses.
