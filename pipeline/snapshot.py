"""Hosted snapshot of the stock + news monitor, for the GitHub Pages dashboard.

The original tool (main.py) runs locally every 15 seconds with macOS voice alerts.
This script runs the same checks on a schedule in GitHub Actions:
  - stock prices from Yahoo Finance vs their average since START_DATE and vs the last snapshot
  - Google News article counts for each topic in monitor.TOPICS since START_DATE
It appends every snapshot to data/history.csv (same columns as main.py's results.csv)
and writes docs/data/latest.json for the dashboard.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import monitor  # noqa: E402  (the original Google News module)

TICKERS = {"WDS": "Woodside Energy", "SHEL": "Shell"}
START_DATE = date.fromisoformat(os.environ.get("MONITOR_START", "2026-07-07"))
PRICE_ALERT_PCT = 2.0     # move vs previous snapshot that triggers an alert
NEWS_SPIKE = 5            # new articles vs previous snapshot that triggers an alert (as in main.py)
HISTORY_CSV = ROOT / "data" / "history.csv"
ALERTS_JSON = ROOT / "data" / "alerts.json"
LATEST_JSON = ROOT / "docs" / "data" / "latest.json"
FIELDS = ["timestamp", "type", "name", "value", "pct_vs_avg", "pct_vs_last", "avg"]


def read_history() -> list[dict]:
    if not HISTORY_CSV.exists():
        return []
    with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def last_value(history: list[dict], kind: str, name: str):
    for row in reversed(history):
        if row["type"] == kind and row["name"] == name and row["value"] not in ("", "None"):
            return float(row["value"])
    return None


def fetch_prices() -> dict:
    import yfinance as yf

    out = {}
    for ticker, name in TICKERS.items():
        df = yf.download(ticker, start=START_DATE.isoformat(), auto_adjust=True, progress=False)
        close = df["Close"].squeeze().dropna()
        out[ticker] = {
            "name": name,
            "price": round(float(close.iloc[-1]), 2),
            "avg": round(float(close.mean()), 2),
            "history": [{"date": d.strftime("%Y-%m-%d"), "close": round(float(v), 2)} for d, v in close.items()],
        }
    return out


def fetch_news() -> dict:
    counts = {}
    for topic in monitor.TOPICS:
        try:
            counts[topic] = monitor.fetch_count(topic, START_DATE)
        except Exception as err:  # keep going if one feed fails
            print(f"news error for {topic!r}: {err}")
            counts[topic] = None
    return counts


def build(prices: dict, news: dict, history: list[dict], now: datetime) -> tuple[list[dict], dict, list[dict]]:
    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    rows, alerts = [], []

    stocks_out = []
    for ticker, p in prices.items():
        last = last_value(history, "stock", ticker)
        pct_avg = round((p["price"] - p["avg"]) / p["avg"] * 100, 2)
        pct_last = round((p["price"] - last) / last * 100, 2) if last else None
        rows.append({"timestamp": ts, "type": "stock", "name": ticker, "value": p["price"],
                     "pct_vs_avg": pct_avg, "pct_vs_last": "" if pct_last is None else pct_last, "avg": p["avg"]})
        if pct_last is not None and abs(pct_last) >= PRICE_ALERT_PCT:
            alerts.append({"timestamp": ts, "kind": "price",
                           "text": f"{ticker} moved {pct_last:+.2f}% since the last check (now ${p['price']})"})
        stocks_out.append({"ticker": ticker, **p, "pct_vs_avg": pct_avg, "pct_vs_last": pct_last})

    topics_out = []
    for topic, count in news.items():
        last = last_value(history, "news", topic)
        delta = None if (count is None or last is None) else int(count - last)
        rows.append({"timestamp": ts, "type": "news", "name": topic, "value": "" if count is None else count,
                     "pct_vs_avg": "", "pct_vs_last": "", "avg": ""})
        if delta is not None and delta >= NEWS_SPIKE:
            alerts.append({"timestamp": ts, "kind": "news",
                           "text": f"News spike: '{topic}' grew by {delta} articles ({int(last)} → {count})"})
        trend = [{"timestamp": r["timestamp"], "count": float(r["value"])}
                 for r in history if r["type"] == "news" and r["name"] == topic and r["value"] not in ("", "None")]
        if count is not None:
            trend.append({"timestamp": ts, "count": count})
        topics_out.append({"topic": topic, "count": count, "delta": delta, "trend": trend[-60:]})

    latest = {
        "generated_utc": now.isoformat(timespec="seconds"),
        "start_date": START_DATE.isoformat(),
        "snapshots": len({r["timestamp"] for r in history}) + 1,
        "rules": {"price_alert_pct": PRICE_ALERT_PCT, "news_spike": NEWS_SPIKE},
        "stocks": stocks_out,
        "topics": topics_out,
    }
    return rows, latest, alerts


def main() -> int:
    now = datetime.now(timezone.utc)
    history = read_history()
    prices = fetch_prices()
    news = fetch_news()
    rows, latest, new_alerts = build(prices, news, history, now)

    HISTORY_CSV.parent.mkdir(parents=True, exist_ok=True)
    new_file = not HISTORY_CSV.exists()
    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerows(rows)

    alerts = json.loads(ALERTS_JSON.read_text()) if ALERTS_JSON.exists() else []
    alerts = (new_alerts + alerts)[:50]
    ALERTS_JSON.write_text(json.dumps(alerts, indent=1))
    latest["alerts"] = alerts[:20]

    LATEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(latest, indent=1))
    print(f"Snapshot {latest['generated_utc']}: {len(rows)} rows, {len(new_alerts)} new alerts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
